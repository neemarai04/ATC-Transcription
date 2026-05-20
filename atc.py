from __future__ import annotations

import os
# Fix OpenMP/Intel MKL thread bloating before importing heavy dependencies
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"

import queue
import re
import subprocess
import threading
import time
import json
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import List
from urllib.error import URLError
from urllib.request import urlopen

import numpy as np
import uvicorn
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from faster_whisper import WhisperModel
from pydantic import BaseModel

# =========================================================
# 1. CONFIGURATION
# =========================================================

# 🔴 Replace with actual LiveATC stream URL before running locally
STREAM_URL = "REPLACE_WITH_LIVE_ATC_STREAM_URL"

#  Whisper model 
MODEL_NAME = "jacktol/whisper-medium.en-fine-tuned-for-ATC-faster-whisper"

SAMPLERATE = 16000
CHUNK_DURATION = 0.5
CHUNK_SIZE = int(SAMPLERATE * CHUNK_DURATION * 2)

VAD_THRESHOLD = 0.01
SPEECH_TIMEOUT = 1.5
MAX_RECORD_SECONDS = 15
MAX_SAMPLES = int(SAMPLERATE * MAX_RECORD_SECONDS)

LOG_FILE = "atc_log.txt"
LOG_PATH = Path(__file__).resolve().parent / LOG_FILE
LOG_LINE_RE = re.compile(r"^\[(?P<time>\d{2}:\d{2}:\d{2})\]\s*(?P<text>.*)$")

# OpenSky region filter (Dublin Airport bounding box)
EIDW_VIEW = {
    "lat_min": 53.2,
    "lat_max": 53.62,
    "lon_min": -6.58,
    "lon_max": -5.9,
}


OPENSKY_STATES_URL = (
    "https://opensky-network.org/api/states/all"
    f"?lamin={EIDW_VIEW['lat_min']}"
    f"&lomin={EIDW_VIEW['lon_min']}"
    f"&lamax={EIDW_VIEW['lat_max']}"
    f"&lomax={EIDW_VIEW['lon_max']}"
)
# =========================================================
# 2. GLOBAL RUNTIME STATE
# =========================================================

audio_queue: queue.Queue = queue.Queue()
stop_event = threading.Event()
threads_started = False
threads_lock = threading.Lock()
log_file_lock = threading.Lock()

print("Initializing ATC Whisper model...")

try:
    # ⚠️ Change device depending on deployment (cpu/gpu)
    model = WhisperModel(
        MODEL_NAME,
        device="gpu",
        compute_type="float16",
    )
    print("Whisper initialized.")
except Exception as e:
    print(f"GPU init failed, switching to CPU int8: {e}")
    model = WhisperModel(
        MODEL_NAME,
        device="cpu",
        compute_type="int8",
    )

# =========================================================
# 3. TRANSCRIBER WORKERS
# =========================================================
def transcription_worker() -> None:
    while not stop_event.is_set():
        try:
            audio_data = audio_queue.get(timeout=1.0) 
        except queue.Empty:
            continue
            
        if audio_data is None:
            break

        audio_np = np.array(audio_data, dtype=np.float32)
        if len(audio_np) < SAMPLERATE:
            continue

        audio_np /= max(1e-6, np.max(np.abs(audio_np)))

        try:
            segments, _ = model.transcribe( #whisper 
                audio_np,
                beam_size=5,
                language="en",
                temperature=0.0,
                condition_on_previous_text=False,
            )

            text = " ".join(s.text.strip() for s in segments)
            if len(text) > 3:
                ts = datetime.now().strftime("%H:%M:%S")
                log_line = f"[{ts}] {text}"
                print(log_line)

                with log_file_lock:
                    with LOG_PATH.open("a", encoding="utf-8") as f:
                        f.write(log_line + "\n")

        except Exception as e:
            print(f"Transcription error: {e}")



def start_ffmpeg() -> subprocess.Popen:
    return subprocess.Popen(
        [
            "ffmpeg",
            "-i", STREAM_URL,
            "-f", "s16le",
            "-ac", "1",
            "-ar", str(SAMPLERATE),
            "-loglevel", "quiet",
            "-",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL
    )

#  live stream processing
def process_stream() -> None:
    while not stop_event.is_set():
        speech_active = False
        last_voice_time = 0.0
        buffer: List[float] = []
        process = start_ffmpeg()
        print("Link established with LiveATC stream.")

        try:
            while not stop_event.is_set():
                if process.stdout is None:
                    raise RuntimeError("ffmpeg stdout is unavailable")

                raw = process.stdout.read(CHUNK_SIZE) 
                if not raw:
                    raise RuntimeError("Stream disconnected")

                chunk = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
                energy = np.sqrt(np.mean(chunk ** 2))

                if energy > VAD_THRESHOLD:
                    if not speech_active:
                        speech_active = True
                    last_voice_time = time.time()
                    buffer.extend(chunk)
                elif speech_active:
                    buffer.extend(chunk)
                    # Sentence boundary reached due to silent gap timeout
                    if (time.time() - last_voice_time) > SPEECH_TIMEOUT: 
                        audio_queue.put(buffer[:MAX_SAMPLES]) 
                        buffer = []
                        speech_active = False

                # Memory leak guard: Force-flush recording if it passes max allowed length
                if len(buffer) >= MAX_SAMPLES:
                    audio_queue.put(buffer[:MAX_SAMPLES])
                    buffer = []
                    speech_active = False

        except Exception as e:
            print(f"Stream error: {e}")
        finally:
            process.kill()
            process.wait()
            time.sleep(2)


# transcription & stream
def start_transcriber_threads_once() -> None:
    global threads_started
    with threads_lock:
        if threads_started:
            return
        threading.Thread(target=transcription_worker, daemon=True).start()
        threading.Thread(target=process_stream, daemon=True).start()
        threads_started = True

# =========================================================
# 4. FASTAPI APP
# =========================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup Engine Tasks
    start_transcriber_threads_once()
    yield
    # Shutdown System Disconnects
    stop_event.set()
    audio_queue.put(None)

app = FastAPI(title="Sky Transcript API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TranscriptEntry(BaseModel):
    timestamp: str
    text: str

class TranscriptResponse(BaseModel):
    source: str
    count: int
    entries: List[TranscriptEntry]

class OpenSkyFlight(BaseModel):
    icao24: str
    callsign: str
    latitude: float
    longitude: float
    speed_mps: float | None
    speed_kts: float | None
    baro_altitude_m: float | None
    geo_altitude_m: float | None
    on_ground: bool

class OpenSkyTrafficResponse(BaseModel):
    source: str
    area: dict
    count: int
    flights: List[OpenSkyFlight]

@app.get("/api/health")
def health() -> dict:
    return {
        "status": "ok",
        "log_exists": LOG_PATH.exists(),
        "log_path": str(LOG_PATH),
        "stream_url": STREAM_URL,
    }


@app.get("/api/transcripts", response_model=TranscriptResponse)
def get_transcripts(limit: int = Query(default=30, ge=1, le=200)) -> TranscriptResponse:
    if not LOG_PATH.exists():
        return TranscriptResponse(source=str(LOG_PATH), count=0, entries=[])

    with log_file_lock:
        with LOG_PATH.open("r", encoding="utf-8") as f:
            raw_lines = [line.strip() for line in f if line.strip()]

    selected = raw_lines[-limit:]
    entries: List[TranscriptEntry] = []

    for line in selected:
        match = LOG_LINE_RE.match(line)
        if match:
            entries.append(
                TranscriptEntry(timestamp=match.group("time"), text=match.group("text"))
            )
        else:
            entries.append(
                TranscriptEntry(
                    timestamp=datetime.now().strftime("%H:%M:%S"),
                    text=line,
                )
            )

    return TranscriptResponse(source=str(LOG_PATH), count=len(entries), entries=entries)


@app.get("/api/opensky/tar90", response_model=OpenSkyTrafficResponse)
def get_opensky_tar90(limit: int = Query(default=100, ge=1, le=500)) -> OpenSkyTrafficResponse:
    """Return OpenSky aircraft in the EIDW region with position and speed."""
    try:
        with urlopen(OPENSKY_STATES_URL, timeout=12) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (URLError, TimeoutError, ValueError) as exc:
        return OpenSkyTrafficResponse(
            source=f"opensky-error: {exc}",
            area=EIDW_VIEW,
            count=0,
            flights=[],
        )

    states = payload.get("states") or []
    flights: List[OpenSkyFlight] = []

    for state in states:
        lat = state[6]
        lon = state[5]
        if not isinstance(lat, (float, int)) or not isinstance(lon, (float, int)):
            continue

        velocity = state[9]
        speed_mps = float(velocity) if isinstance(velocity, (float, int)) else None
        
        # Protected against multiplying against a missing payload object (NoneType)
        speed_kts = round(speed_mps * 1.94384, 2) if speed_mps is not None else None

        flights.append(
            OpenSkyFlight(
                icao24=str(state[0] or ""),
                callsign=str((state[1] or "").strip() or "Unknown"),
                latitude=float(lat),
                longitude=float(lon),
                speed_mps=speed_mps,
                speed_kts=speed_kts,
                baro_altitude_m=float(state[7]) if isinstance(state[7], (float, int)) else None,
                geo_altitude_m=float(state[13]) if isinstance(state[13], (float, int)) else None,
                on_ground=bool(state[8]),
            )
        )

    # Clean fallback value applied inside sort key lambda to avoid arbitrary type evaluation crashes
    flights.sort(
        key=lambda f: f.speed_mps if f.speed_mps is not None else -1.0,
        reverse=True,
    )

    limited_flights = flights[:limit]
    return OpenSkyTrafficResponse(
        source="opensky-network.org/api/states/all",
        area=EIDW_VIEW,
        count=len(limited_flights),
        flights=limited_flights,
    )


if __name__ == "__main__":
    uvicorn.run("atc:app", host="0.0.0.0", port=8000, reload=False)

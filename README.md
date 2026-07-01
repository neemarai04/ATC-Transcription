# ATC Transcription System

An AI-assisted Air Traffic Control (ATC) transcription and aircraft monitoring system developed during an internship under the EMBRACE initiative at NITK Surathkal.

The system uses AI-powered speech recognition to transcribe live ATC radio communications streamed from LiveATC while displaying real-time aircraft operating within a configurable airspace region using the OpenSky Network API. It features a React-based dashboard for visualizing transcriptions and aircraft activity in near real time.

---

## Features

* AI-powered transcription of ATC radio communications
* Faster-Whisper based speech recognition optimized for aviation
* Real-time (or near real-time) transcription workflow
* Aircraft tracking using the OpenSky Network API
* Interactive React dashboard
* Backend API for transcription processing
---

## Technologies Used

### Frontend

* React
* Vite
* JavaScript
* CSS

### Backend

* Python
* Faster-Whisper
* OpenSky Network API
* AI-based transcription

---

## Project Structure

```text
transcription/
│
├── atc.py
├── requirements.txt
├── dashboard/ 
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   ├── styles.css
│   ├── index.html
│   ├── package.json
│   ├── package-lock.json
│   ├── vite.config.js
```

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/neemarai04/ATC-Transcription.git
cd ATC-Transcription
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Frontend Dependencies

```bash
cd dashboard
npm install
```

---

## Configuration

Before running the project locally, update the required configuration values inside `atc.py`.

### 1. ATC Audio Stream URL

Replace the placeholder ATC stream URL before running the application.

Example:

```python
# Replace with actual LiveATC or audio stream URL before running locally
STREAM_URL = "REPLACE_WITH_LIVE_ATC_STREAM_URL"
```

You may use:
* LiveATC stream URLs (where access is available))
* Public audio stream endpoints
* Local testing streams

### 2. Whisper Model Configuration

The project currently uses:

```python
# Whisper model
MODEL_NAME = "jacktol/whisper-medium.en-fine-tuned-for-ATC-faster-whisper"
```

You may replace it with any compatible Whisper or Faster-Whisper model depending on your hardware and performance requirements.



### 3. OpenSky Region Filter

The default aircraft tracking region is configured for Dublin Airport.

Example:

```python
# OpenSky region filter (Dublin Airport bounding box)
EIDW_VIEW = {
    "lat_min": 53.2,
    "lat_max": 53.62,
    "lon_min": -6.58,
    "lon_max": -5.9,
}
```

You can modify these coordinates to monitor a different airport or airspace region.

---

## Running the Project

### Start the Backend

From the project root directory:

```bash
python atc.py
```

### Start the Frontend

Open another terminal:

```bash
cd dashboard 
npm run dev
```

---

### Open in Browser

After running the frontend, open the local URL shown in the terminal (usually `http://localhost:5173`).

---

## Future Improvements

* Improved transcription accuracy
* Enhanced radio noise suppression
* Speaker identification
* Multi-frequency monitoring
* Live streaming support
* NLP-based communication analysis
* Flight history and analytics

---

## Author

Neema J Rai

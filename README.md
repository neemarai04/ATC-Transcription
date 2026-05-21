# ATC Transcription System

An AI-assisted Air Traffic Control (ATC) transcription and monitoring system developed during an internship under the EMBRACE initiative at NITK Surathkal.

## Overview

This project focuses on processing and transcribing ATC/HAM radio communications using speech recognition and AI-based processing techniques. The system includes a frontend dashboard and backend processing modules for handling transcription-related tasks.

## Features

* Audio transcription for ATC communication
* AI-assisted processing and analysis
* Interactive dashboard interface
* Real-time or near real-time transcription workflow
* Backend API integration
* Aircraft tracking integration
* Whisper-based ATC speech recognition
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
* Speech Recognition / AI-based transcription
---

## Important Configuration

Before running the project locally, update the required configuration values inside `atc.py`.

### 1. ATC Audio Stream URL

Replace the placeholder ATC stream URL before running the application.

Example:

```python
# Replace with actual LiveATC or audio stream URL before running locally
STREAM_URL = "REPLACE_WITH_LIVE_ATC_STREAM_URL"
```

You may use:
- LiveATC stream URLs (requires valid access where applicable)
- Public audio stream endpoints
- Local testing streams



### 2. Whisper Model Configuration

The project currently uses:

```python
# Whisper model
MODEL_NAME = "jacktol/whisper-medium.en-fine-tuned-for-ATC-faster-whisper"
```

You may replace it with another supported Whisper or Faster-Whisper model depending on performance and accuracy requirements.



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


## Project Structure

```text
transcription/
│
├── atc.py
├── requirements.txt
├── dashboard/ (frontend)
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
## Internship Context

This project was developed as part of an industry-oriented internship conducted under the EMBRACE initiative at NITK Surathkal, focusing on communication systems, signal processing, and AI applications in aviation and emergency communication systems.

---
## Future Improvements

* Improved transcription accuracy
* Noise reduction for radio communication
* Speaker identification
* Live streaming support
* Advanced NLP analysis

---
## Author

Neema J Rai

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

## Technologies Used

### Frontend

* React
* Vite
* JavaScript
* CSS

### Backend

* Python
* Speech Recognition / AI-based transcription

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

### Open in Browser

After running the frontend, open the local URL shown in the terminal (usually `http://localhost:5173`).

## Internship Context

This project was developed as part of an industry-oriented internship conducted under the EMBRACE initiative at NITK Surathkal, focusing on communication systems, signal processing, and AI applications in aviation and emergency communication systems.

## Future Improvements

* Improved transcription accuracy
* Noise reduction for radio communication
* Speaker identification
* Live streaming support
* Advanced NLP analysis

## Author

Neema J Rai

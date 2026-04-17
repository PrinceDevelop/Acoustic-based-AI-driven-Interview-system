Acoustic-Based AI Driven Interview System for Automated Candidate Evaluation

Project Overview

The Acoustic-Based AI Driven Interview System is an intelligent web-based recruitment platform that automates candidate interview evaluation using Artificial Intelligence.

The system captures candidate responses through webcam and microphone, converts speech into text, analyzes acoustic and linguistic features, and generates automated scores with feedback. It is designed to improve hiring efficiency, reduce manual effort, and minimize bias in interview assessment.

Key Features

* User Registration and Login
* Secure Session Management
* Interactive Dashboard
* Live Video Interview Interface
* Audio Extraction from Recorded Video
* Speech-to-Text Conversion using Whisper
* Acoustic Feature Analysis using Librosa
* NLP-Based Response Evaluation
* AI Score Generation and Feedback
* Resume Upload and Parsing
* Email Result Notification
* Responsive User Interface

Technology Stack

## Frontend

* HTML5
* CSS3
* JavaScript

## Backend

* Python
* Flask

## Database

* SQLite

## AI / Processing Libraries

* Whisper
* Librosa
* NumPy
* TextBlob / NLP Tools

## Utilities

* FFmpeg
* Gunicorn


# Project Structure

```text id="67nk7v"
Acoustic-Based-AI-Driven-Interview-System/
│
├── app.py
├── database.py
├── audio_processing.py
├── nlp_analysis.py
├── model.py
├── email_service.py
├── resume_parser.py
├── requirements.txt
├── Procfile
├── .gitignore
│
├── static/
│   ├── global.css
│   └── script.js
│
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── signup.html
│   ├── dashboard.html
│   ├── interview.html
│   ├── services.html
│   ├── contact.html
│   ├── reset.html
│   └── resume_result.html
│
└── uploads/
```

---

# System Workflow

```text id="1d68yu"
User Login
   ↓
Dashboard Access
   ↓
Start Interview
   ↓
Record Video Response
   ↓
Extract Audio
   ↓
Speech-to-Text
   ↓
Acoustic Analysis
   ↓
NLP Analysis
   ↓
Score Generation
   ↓
Result + Feedback + Email
```

---

# Installation Guide

## 1. Clone Repository

```bash id="z8ws7x"
git clone <repository-url>
cd Acoustic-Based-AI-Driven-Interview-System
```

## 2. Create Virtual Environment

```bash id="ub5v3q"
python -m venv venv
venv\Scripts\activate
```

## 3. Install Dependencies

```bash id="c8l4v4"
pip install -r requirements.txt
```

## 4. Install FFmpeg

Download and install FFmpeg from the official website:
[https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)

Ensure FFmpeg is added to system PATH.

## 5. Run Application

```bash id="3r7j0v"
python app.py
```

## 6. Open in Browser

```text id="v4w9f1"
http://127.0.0.1:5000
```

---

# Main Objectives

1. Automate the interview evaluation process using AI.
2. Analyze speech confidence, pitch, and clarity.
3. Evaluate textual responses using NLP.
4. Generate real-time scores and feedback.
5. Improve fairness and recruitment efficiency.

---

# Limitations

* Sensitive to noisy environments
* Depends on microphone/webcam quality
* Accent variation may affect transcription
* Cannot fully replace human judgment

---

# Future Scope

* Facial Emotion Detection
* Adaptive AI Question Generation
* Cloud Deployment
* Recruiter Analytics Dashboard
* Multilingual Interview Support
* Mobile Application Version

---

# Learning Outcomes

* Artificial Intelligence Integration
* Audio Signal Processing
* Natural Language Processing
* Full Stack Web Development
* Database Management
* Deployment Practices


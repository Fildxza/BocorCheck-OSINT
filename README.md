# BocorCheck

An OSINT-Based Personal Data Exposure Monitoring and Risk Analysis Platform developed as a Final Year Project for the Bachelor of Information Technology (Hons.) in Computer Forensics.

---

## Overview

BocorCheck is a cybersecurity web application designed to help users identify whether their personal information has been exposed in publicly available breach datasets.

The platform combines Open Source Intelligence (OSINT) techniques with AI-powered mitigation recommendations and Telegram notifications to improve personal data security awareness.

---

## Key Features

- Email Breach Detection
- Personal Data Exposure Monitoring
- AI-Powered Mitigation Recommendations (Microsoft Phi-3 via Ollama)
- Telegram Notification Integration
- Risk Scoring System
- Investigation History
- Monitoring Dashboard
- Dark Web Simulation Module
- Interactive Breach Timeline
- User Authentication and Account Management

---

## Technology Stack

### Backend

- Python
- Flask
- MySQL

### Frontend

- HTML5
- Bootstrap 5
- JavaScript

### Artificial Intelligence

- Ollama
- Microsoft Phi-3 Mini

### Security

- bcrypt
- Session Authentication

---

## Project Structure

```text
BocorCheck/
│
├── app.py
├── bot.py
├── ai_mitigation.py
├── auth.py
├── mitigation.py
├── monitoring.py
├── darkweb_checker.py
├── data_analyzer.py
├── db_setup.py
│
├── templates/
├── static/
├── sql/
├── scripts/
├── tests/
├── docs/
│
├── requirements.txt
├── README.md
└── LICENSE
```

---

## Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/BocorCheck.git
cd BocorCheck
```

Create a virtual environment:

```bash
python -m venv .venv
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Configure the `.env` file:

```env
DB_HOST=
DB_USER=
DB_PASSWORD=
DB_NAME=

BOT_TOKEN=
OLLAMA_URL=http://localhost:11434
```

---

## Running the Application

Start Ollama:

```bash
ollama serve
ollama run phi3
```

Run the Flask application:

```bash
python app.py
```

---

## Testing

The repository includes standalone testing scripts for:

- AI Integration
- Mitigation Functions
- Breach Data Validation
- User Interface Testing
- Telegram Integration

---

## Screenshots

The following screenshots can be added after deployment:

- Dashboard
- Investigation History
- Monitoring Dashboard
- AI Mitigation Response
- Telegram Notification
- Dark Web Dashboard
- Breach Timeline

---

## Academic Information

**Project Title**

Development of an OSINT-Based Personal Data Exposure Monitoring and Risk Analysis

**Programme**

Bachelor of Information Technology (Hons.) in Computer Forensics

**University**

Universiti Tun Abdul Razak (UNIRAZAK)

---

## Disclaimer

This project was developed for academic and educational purposes.

The Dark Web module is implemented as a simulation environment for demonstrating cybersecurity concepts. It does not perform live dark web monitoring.

---

## License

This project is intended for academic and educational use only.

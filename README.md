# ZenFlow - AI Ergonomics Coach

ZenFlow is an AI-powered ergonomics and posture detection system that uses computer vision and machine learning to monitor user posture in real time through webcam video analysis.

The system detects posture-related issues such as slouching, forward head tilt, and shoulder imbalance, and provides real-time feedback and alerts to improve ergonomic habits.

---

## Features

- Real-time posture detection
- Webcam-based body posture monitoring
- AI-powered ergonomic analysis
- Low-latency posture alerts
- Live posture feedback dashboard
- Session-based monitoring and analytics

---

## Technologies Used

- Python
- TensorFlow
- OpenCV
- MediaPipe
- Flask
- HTML
- CSS
- JavaScript

---

## Project Workflow

1. Webcam captures live video feed
2. OpenCV processes video frames
3. MediaPipe detects body keypoints
4. TensorFlow model analyzes posture patterns
5. System identifies posture issues
6. Alerts and posture feedback are displayed in real time

---

## Posture Issues Detected

- Slouching
- Forward head posture
- Shoulder imbalance
- Neck strain risk

---

## System Architecture

```bash
ZenFlow/
│
├── app.py
├── posture_model/
├── templates/
│   └── index.html
├── static/
│   ├── style.css
│   └── script.js
├── requirements.txt
└── README.md
```

---

## Installation

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python app.py
```

Open in browser:

```bash
http://127.0.0.1:5000
```

---

## Performance

- Achieved 94–98% posture detection accuracy
- Real-time frame processing with low latency
- Continuous posture monitoring using computer vision

---

## Future Improvements

- Mobile application integration
- Personalized posture correction plans
- Cloud-based analytics dashboard
- Deep learning posture classification improvements
- Workplace ergonomics reporting system

---

## Applications

- Workplace ergonomics
- Student posture monitoring
- Fitness and rehabilitation support
- Remote work wellness systems
- Health and productivity tracking

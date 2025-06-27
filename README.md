# 🏋️‍♂️ Calisthenics Form Analyzer

A full-stack web application built with **React** (frontend) and **Flask** (backend) that analyzes static calisthenics skills in real-time using your webcam. It provides **live feedback** and **grading** on your form for various advanced holds like the **Handstand**, **Front Lever**, **90-Degree Hold**, and **Planche**.

---

## 🚀 Features

- 📸 **Live Camera Feed** – Use your webcam to perform calisthenics moves and receive instant feedback.
- 🧠 **Pose Detection** – Detects key body points using computer vision (Mediapipe / OpenCV).
- 📝 **Skill Grading** – Evaluates the accuracy of your form and gives you a grade (e.g., A–F).
- 💬 **Feedback** – Provides real-time tips to improve your technique.
- 🧍‍♂️ **Supported Skills (Static)**:
  - Handstand
  - Front Lever
  - 90-Degree Hold
  - Planche
- 📤 **Video Upload** *(coming soon)* – Analyze pre-recorded videos instead of using the webcam.

---

## 🛠️ Tech Stack

| Frontend         | Backend       | CV / ML              |
|------------------|---------------|----------------------|
| React (TypeScript) | Flask (Python) | OpenCV, Mediapipe     |

---

## 📦 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/axli16/JointTrack.git
python FlaskServer.py
cd calisthenic-tracker
npm start dev
```

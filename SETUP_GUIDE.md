# 🚀 JointTrack - Confluent Hackathon Setup Guide

## Overview
This guide will help you set up the real-time streaming architecture for the Confluent Challenge using:
- **Confluent Cloud** (Kafka + Flink) for data streaming
- **Google Cloud Vertex AI** (Gemini) for AI-powered form analysis
- **MediaPipe** for pose detection
- **Flask** backend + **React** frontend

---

## ✅ Phase 1: Confluent Cloud Setup (COMPLETED)

### What You've Done:
- [x] Created Confluent Cloud account
- [x] Set up a cluster on Google Cloud
- [x] Created topics: `pose-stream` and `feedback-stream`
- [x] Generated API keys
- [x] Saved credentials to `.env` file

### Your Topics:
1. **pose-stream** - Receives real-time pose landmarks from users
2. **feedback-stream** - Sends AI-generated feedback back to users

---

## 📦 Phase 2: Install Dependencies

### Python Dependencies
```bash
pip install confluent-kafka python-dotenv google-cloud-aiplatform
```

### Verify Installation
```bash
python test_kafka_connection.py
```

This should:
- ✅ Connect to Confluent Cloud
- ✅ Produce a test message
- ✅ Consume the test message

---

## 🏗️ Architecture Overview

```
┌─────────────┐         ┌──────────────┐         ┌─────────────────┐
│   React     │  POST   │    Flask     │ Produce │  Confluent      │
│  Frontend   │────────▶│   Backend    │────────▶│  pose-stream    │
│ (MediaPipe) │         │  (Producer)  │         │                 │
└─────────────┘         └──────────────┘         └────────┬────────┘
                                                           │
                                                           │ Consume
                                                           ▼
                                                  ┌─────────────────┐
                                                  │  AI Consumer    │
                                                  │  (Python)       │
                                                  │                 │
                                                  │  1. Buffer 3s   │
                                                  │  2. Call Gemini │
                                                  │  3. Get Feedback│
                                                  └────────┬────────┘
                                                           │ Produce
                                                           ▼
                                                  ┌─────────────────┐
       ┌────────────────────────────────────────▶│  Confluent      │
       │                                          │ feedback-stream │
       │  WebSocket/SSE                           └─────────────────┘
       │
┌─────────────┐
│   React     │
│  Frontend   │
│ (Display)   │
└─────────────┘
```

---

## 🔧 Files Created

### 1. `FlaskServerStreaming.py`
- **Purpose**: New Flask server with Kafka producer
- **Key Endpoint**: `/stream-pose` - Receives landmarks and streams to Kafka
- **Usage**: Replace your current `FlaskServer.py` or run alongside for testing

### 2. `kafka_utils.py`
- **Purpose**: Helper functions to convert MediaPipe data to JSON
- **Key Function**: `mediapipe_to_json()` - Formats landmarks for Kafka

### 3. `test_kafka_connection.py`
- **Purpose**: Verify your Confluent Cloud connection
- **Run**: `python test_kafka_connection.py`

### 4. `.env.example`
- **Purpose**: Template for your credentials
- **Action**: Copy to `.env` and fill in your actual values

---

## 🎯 Next Steps

### Step 1: Test Kafka Connection ⏳ (You are here)
```bash
python test_kafka_connection.py
```

### Step 2: Update React Frontend
Modify your React app to:
1. Throttle MediaPipe output to ~5 FPS (200ms intervals)
2. POST landmarks to `/stream-pose` endpoint
3. Display real-time feedback

### Step 3: Create AI Consumer Service
Build a Python service that:
1. Consumes from `pose-stream`
2. Buffers 2-3 seconds of landmarks
3. Sends to Google Vertex AI (Gemini)
4. Produces feedback to `feedback-stream`

### Step 4: Google Cloud Setup
1. Create Google Cloud project
2. Enable Vertex AI API
3. Set up service account
4. Test Gemini API

### Step 5: Connect Frontend to Feedback Stream
Add WebSocket or Server-Sent Events to receive real-time AI feedback

---

## 🐛 Troubleshooting

### "Module not found: confluent_kafka"
```bash
pip install confluent-kafka
```

### "Missing configuration in .env"
Make sure your `.env` file has:
```
CONFLUENT_BOOTSTRAP_SERVERS=pkc-xxxxx.confluent.cloud:9092
CONFLUENT_API_KEY=your-key
CONFLUENT_API_SECRET=your-secret
POSE_TOPIC=pose-stream
FEEDBACK_TOPIC=feedback-stream
```

### "Connection refused" or "Authentication failed"
- Double-check your API key and secret
- Verify bootstrap server URL
- Make sure cluster is running in Confluent Cloud

---

## 📊 Testing the Full Pipeline

### 1. Start Flask Server
```bash
python FlaskServerStreaming.py
```

### 2. Send Test Pose Data
```bash
curl -X POST http://localhost:5000/stream-pose \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "exercise": "handstand",
    "landmarks": [
      {"part": "left_shoulder", "x": 0.5, "y": 0.3, "z": -0.1, "visibility": 0.99}
    ]
  }'
```

### 3. Check Confluent Cloud Console
- Go to Topics → `pose-stream`
- Click "Messages"
- You should see your test message!

---

## 🎓 Key Concepts

### Why Kafka?
- **Decoupling**: Frontend doesn't wait for AI processing
- **Scalability**: Can handle 1000s of users simultaneously
- **Reliability**: Messages are persisted, won't lose data
- **Real-time**: Sub-second latency

### Why Windowing?
- A single frame isn't enough to judge form
- Need 2-3 seconds (10-15 frames) to see the movement
- Flink SQL can aggregate frames into "clips"

### Why Gemini?
- Hardcoded angles are brittle
- AI can understand complex movements
- Can provide natural language feedback
- Adapts to different body types

---

## 📚 Resources

- [Confluent Cloud Docs](https://docs.confluent.io/cloud/current/overview.html)
- [Confluent Python Client](https://docs.confluent.io/kafka-clients/python/current/overview.html)
- [Google Vertex AI](https://cloud.google.com/vertex-ai/docs)
- [MediaPipe Pose](https://google.github.io/mediapipe/solutions/pose.html)

---

## 🏆 Hackathon Checklist

- [x] Confluent Cloud account created
- [x] Topics created
- [x] API keys generated
- [x] Flask server with Kafka producer
- [ ] Test Kafka connection
- [ ] Update React frontend
- [ ] Create AI consumer service
- [ ] Google Cloud setup
- [ ] End-to-end testing
- [ ] Demo video
- [ ] Documentation

---

**Need help?** Check the troubleshooting section or review the code comments in each file.

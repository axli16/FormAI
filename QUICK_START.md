# 🎯 Quick Reference - Commands to Run

## Start the Full System (3 Terminals)

### Terminal 1: Flask Backend
```bash
cd f:\JointTrack
python FlaskServer.py
```
**Streams pose data to Kafka at 5 FPS**

---

### Terminal 2: React Frontend
```bash
cd f:\JointTrack\calisthenics-tracker
npm start
```
**Displays video feed and feedback**

---

### Terminal 3: AI Feedback Service
```bash
cd f:\JointTrack
python ai_feedback_service.py
```
**Analyzes poses and generates feedback**

---

## Optional: Monitor Data Flow

### View Pose Stream (Terminal 4)
```bash
python view_pose_stream.py
```
**Shows pose data flowing through Kafka**

---

## Test Kafka Connection
```bash
python quick_test_kafka.py
```

---

## File Structure

```
JointTrack/
├── FlaskServer.py              # ✅ UPDATED - Streams to Kafka
├── VideoFeed.py                # ✅ Existing - Pose detection
├── ai_feedback_service.py      # ✅ NEW - AI analysis
├── view_pose_stream.py         # ✅ NEW - Monitor stream
├── quick_test_kafka.py         # ✅ NEW - Test connection
├── .env                        # ✅ Your credentials
├── TESTING_GUIDE.md            # ✅ Full guide
└── calisthenics-tracker/
    └── src/
        └── App.js              # ✅ Existing - React UI
```

---

## Environment Variables (.env)

```bash
# Confluent Cloud
CONFLUENT_BOOTSTRAP_SERVERS=pkc-619z3.us-east1.gcp.confluent.cloud:9092
CONFLUENT_API_KEY=AEHDS4HH...
CONFLUENT_API_SECRET=...

# Topics
POSE_TOPIC=pose-stream
FEEDBACK_TOPIC=feedback-stream

# Google Cloud (Optional)
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json
```

---

## URLs

- **React App**: http://localhost:3000
- **Flask API**: http://localhost:5000
- **Feedback Endpoint**: http://localhost:5000/feedback
- **Confluent Cloud**: https://confluent.cloud

---

## Data Flow Summary

```
Camera → MediaPipe → Flask → Kafka (pose-stream) → AI Service → Kafka (feedback-stream) → Flask → React
```

---

## Troubleshooting Quick Fixes

| Problem | Solution |
|---------|----------|
| Kafka not configured | Check `.env` file |
| No video feed | Check camera permissions |
| No feedback | Refresh React app |
| AI service not working | Check Kafka credentials |
| CORS errors | Restart Flask server |

---

## Key Metrics to Show

1. **Latency**: Time from pose to feedback (~3-4 seconds)
2. **Throughput**: 5 messages/second to Kafka
3. **Accuracy**: AI-generated feedback quality
4. **Scalability**: Kafka can handle 1000s of users

---

## Demo Script

1. **Start all services** (3 terminals)
2. **Show Confluent console** with messages flowing
3. **Perform a handstand** - show detection
4. **Show AI feedback** appearing
5. **Try different skills** - front lever, planche
6. **Highlight real-time aspect** - feedback while moving

---

## Hackathon Talking Points

- ✅ **Data in Motion**: Processing poses in real-time, not batch
- ✅ **Confluent Cloud**: Using Kafka for streaming
- ✅ **Google Cloud**: AI-powered feedback (Vertex AI)
- ✅ **Scalable**: Can handle multiple users simultaneously
- ✅ **Extensible**: Easy to add new sports/exercises

---

**Ready to run? Start with Terminal 1, then 2, then 3!** 🚀

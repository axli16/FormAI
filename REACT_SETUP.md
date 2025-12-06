# React Frontend Setup for Streaming

## 📦 Install MediaPipe Dependencies

Run this in the `calisthenics-tracker` directory:

```bash
cd calisthenics-tracker
npm install @mediapipe/pose @mediapipe/camera_utils @mediapipe/drawing_utils
```

## 🔄 Switch to Streaming Version

### Option 1: Replace App.js (Recommended for hackathon)
```bash
# Backup your current App.js
copy src\App.js src\App.backup.js

# Replace with streaming version
copy src\AppStreaming.js src\App.js
```

### Option 2: Import in index.js
Edit `src/index.js` and change:
```javascript
import App from './App';
```
to:
```javascript
import App from './AppStreaming';
```

## 🚀 Run the Frontend

```bash
npm start
```

## 🎯 How It Works

### Old Architecture (Batch Processing):
```
React → Display video from Flask → Flask processes with MediaPipe
```

### New Architecture (Real-time Streaming):
```
React (MediaPipe in browser) → Extract landmarks → POST to Flask → Kafka → AI
```

## ✨ New Features

1. **MediaPipe in Browser**: Pose detection runs client-side
2. **Throttled Streaming**: Sends landmarks at 5 FPS (200ms intervals)
3. **Visual Feedback**: See pose skeleton drawn in real-time
4. **Streaming Indicator**: Shows when data is flowing to Kafka
5. **Skill Selection**: Choose which exercise you're performing

## 🧪 Testing the Full Pipeline

### 1. Start Flask Backend
```bash
# In JointTrack directory
python FlaskServerStreaming.py
```

### 2. Start React Frontend
```bash
# In calisthenics-tracker directory
npm start
```

### 3. Test Streaming
1. Allow camera access when prompted
2. You should see your pose skeleton drawn on screen
3. Click "Start Streaming"
4. Check the browser console - you should see "Streamed to Kafka" messages
5. Check Confluent Cloud console - you should see messages in `pose-stream` topic!

## 🐛 Troubleshooting

### Camera not working
- Make sure you allowed camera permissions
- Try a different browser (Chrome works best)
- Check if another app is using the camera

### CORS errors
- Make sure Flask has `flask-cors` installed
- Check that Flask is running on port 5000

### MediaPipe not loading
- Check browser console for errors
- Make sure you have a stable internet connection (MediaPipe loads from CDN)
- Try clearing browser cache

### No data in Kafka
- Check Flask console for errors
- Verify your .env file has correct Kafka credentials
- Make sure you're clicking "Start Streaming" button

## 📊 What Gets Streamed

Each message to Kafka contains:
```json
{
  "user_id": "user_1",
  "timestamp": 1765048576573,
  "exercise": "handstand",
  "landmarks": [
    {"part": "nose", "x": 0.5, "y": 0.3, "z": -0.1, "visibility": 0.99},
    {"part": "left_shoulder", "x": 0.4, "y": 0.5, "z": -0.05, "visibility": 0.98},
    ...
  ]
}
```

## 🎬 Next Steps

Once this is working:
1. ✅ Verify messages appear in Confluent Cloud
2. Build the AI Consumer service (reads from Kafka, sends to Gemini)
3. Add feedback display in React (receive AI responses)
4. Set up Google Cloud Vertex AI
5. Demo time! 🎉

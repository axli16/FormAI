from flask import Flask, Response, jsonify, request
import os
from flask_cors import CORS
from confluent_kafka import Producer
import json
import socket
from dotenv import load_dotenv
import time
import VideoFeed
from feedback_logger import get_logger

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)
feed = VideoFeed.VideoCamera()
feedback = {"skill": "", "grade": "", "tips":[]}

# --- CONFLUENT KAFKA SETUP ---
def get_kafka_config():
    """Get Kafka configuration from environment variables"""
    bootstrap = os.getenv('CONFLUENT_BOOTSTRAP_SERVERS')
    if not bootstrap or bootstrap == 'your-bootstrap-server-here.confluent.cloud:9092':
        print("⚠️  Kafka not configured - streaming disabled")
        return None
    
    return {
        'bootstrap.servers': bootstrap,
        'security.protocol': 'SASL_SSL',
        'sasl.mechanism': 'PLAIN',
        'sasl.username': os.getenv('CONFLUENT_API_KEY'),
        'sasl.password': os.getenv('CONFLUENT_API_SECRET'),
        'client.id': socket.gethostname()
    }

# Initialize Kafka Producer (optional - won't break if not configured)
kafka_config = get_kafka_config()
producer = None
feedback_consumer = None

if kafka_config:
    try:
        producer = Producer(kafka_config)
        print("✅ Kafka producer initialized")
        
        # Also initialize consumer for feedback
        from confluent_kafka import Consumer
        consumer_config = kafka_config.copy()
        consumer_config['group.id'] = 'flask-feedback-reader'
        consumer_config['auto.offset.reset'] = 'latest'
        feedback_consumer = Consumer(consumer_config)
        feedback_topic = os.getenv('FEEDBACK_TOPIC', 'feedback-stream')
        feedback_consumer.subscribe([feedback_topic])
        print(f"✅ Kafka consumer initialized for {feedback_topic}")
        
    except Exception as e:
        print(f"⚠️  Kafka initialization failed: {e}")
        producer = None
        feedback_consumer = None

# Store AI-generated feedback
user_selected_skill = "handstand"  # Default
ai_feedback = {"skill": user_selected_skill, "grade": "", "tips": [], "source": "rule-based"}

# Initialize feedback logger
feedback_logger = get_logger()

def poll_ai_feedback():
    """Poll for AI-generated feedback from Kafka (non-blocking)"""
    global ai_feedback
    if feedback_consumer is None:
        return
    
    try:
        # Non-blocking poll
        msg = feedback_consumer.poll(0.1)
        if msg is not None and msg.error() is None:
            feedback_data = json.loads(msg.value().decode('utf-8'))
            ai_feedback = feedback_data
            ai_feedback['source'] = 'ai'
            print(f"📥 Received AI feedback: {feedback_data['skill']} - {feedback_data['grade']}")
            
            # Log the AI feedback
            feedback_logger.log_feedback(
                feedback_data,
                metadata={
                    "user_id": "user_1",
                    "source": "kafka_consumer"
                }
            )
    except Exception as e:
        pass  # Silently fail, don't break the app

def delivery_report(err, msg):
    """Kafka delivery callback"""
    if err is not None:
        print(f'❌ Kafka delivery failed: {err}')
    # Uncomment for debugging:
    # else:
    #     print(f'✅ Delivered to {msg.topic()}')

# Throttle streaming to ~5 FPS
last_stream_time = 0
STREAM_INTERVAL = 0.2  # 200ms = 5 FPS

def generate_frames():
    global last_stream_time
    while True:
        frame = feed.get_frame()
        if frame is None:
            continue
        
        # Stream landmarks to Kafka (throttled to 5 FPS)
        if producer is not None:
            current_time = time.time()
            if current_time - last_stream_time >= STREAM_INTERVAL:
                last_stream_time = current_time
                stream_landmarks_to_kafka()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def stream_landmarks_to_kafka():
    """Stream current pose landmarks to Kafka"""
    try:
        if not feed.landmarks or len(feed.landmarks) == 0:
            return
        
        # Convert landmarks to JSON format
        landmark_data = []
        landmark_names = {
            0: 'nose',
            11: 'left_shoulder', 12: 'right_shoulder',
            13: 'left_elbow', 14: 'right_elbow',
            15: 'left_wrist', 16: 'right_wrist',
            23: 'left_hip', 24: 'right_hip',
            25: 'left_knee', 26: 'right_knee',
            27: 'left_ankle', 28: 'right_ankle'
        }
        
        for idx, name in landmark_names.items():
            if idx < len(feed.landmarks):
                lm = feed.landmarks[idx]
                landmark_data.append({
                    "part": name,
                    "x": round(lm.x, 4),
                    "y": round(lm.y, 4),
                    "z": round(lm.z, 4),
                    "visibility": round(lm.visibility, 4)
                })
        
        # Use user-selected skill instead of auto-detection
        skill_name = user_selected_skill
        
        # Convert angles dict (enum keys to strings for JSON serialization)
        angles_serializable = {}
        for key, value in feed.angles.items():
            # Convert enum to string name
            key_name = key.name if hasattr(key, 'name') else str(key)
            angles_serializable[key_name] = value
        
        # Create message payload
        message = {
            "user_id": "user_1",
            "timestamp": int(time.time() * 1000),
            "exercise": skill_name,
            "landmarks": landmark_data,
            "angles": angles_serializable  # Now JSON-serializable
        }
        
        # Send to Kafka
        topic = os.getenv('POSE_TOPIC', 'pose-stream')
        producer.produce(
            topic,
            key="user_1",
            value=json.dumps(message),
            callback=delivery_report
        )
        producer.poll(0)  # Trigger callbacks
        
    except Exception as e:
        print(f"Error streaming to Kafka: {e}")

@app.route('/feedback')        
def getfeedback():
    # Poll for new AI feedback
    poll_ai_feedback()
    
    # Use AI feedback if available, otherwise use rule-based
    if ai_feedback.get('source') == 'ai' and ai_feedback.get('skill'):
        return jsonify({
            "skill": str(ai_feedback["skill"]),
            "grade": str(ai_feedback["grade"]),
            "tips": list(ai_feedback["tips"]),
            "source": "ai"
        })
    else:
        # Fallback to rule-based feedback
        # update_feedback()
        return jsonify({
            "skill": "Detecting...",
            "grade": "Pending",
            "tips": ["Looking..."],
            "source": "rule-based"
        })

# Store user-selected skill


@app.route('/set-skill', methods=['POST'])
def set_skill():
    """Receive skill selection from frontend"""
    global user_selected_skill
    try:
        data = request.json
        skill = data.get('skill', 'handstand')
        user_selected_skill = skill
        print(f"✅ Skill set to: {skill}")
        return jsonify({"status": "success", "skill": skill})
    except Exception as e:
        print(f"Error setting skill: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

def update_feedback():
    global feedback
    skill_detected = feed.detect_skill()
    skill_feedback = feed.feed_back(skill_detected)
    accuracy = skill_feedback[-2] 
    skill_name = skill_feedback[-1]

    tips = []
    for i in range(0, len(skill_feedback) - 2):
        tips.append(skill_feedback[i])
    
    feedback["skill"] = user_selected_skill
    feedback["grade"] = accuracy
    feedback["tips"] = tips

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
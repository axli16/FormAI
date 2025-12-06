from flask import Flask, Response, jsonify, request
import os
from flask_cors import CORS
from confluent_kafka import Producer
import json
import socket
from dotenv import load_dotenv

import VideoFeed

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize video feed
feed = VideoFeed.VideoCamera()
feedback = {"skill": "", "grade": "", "tips": []}

# --- CONFLUENT KAFKA CONFIGURATION ---
def read_kafka_config():
    """Read Kafka configuration from environment variables"""
    return {
        'bootstrap.servers': os.getenv('CONFLUENT_BOOTSTRAP_SERVERS'),
        'security.protocol': 'SASL_SSL',
        'sasl.mechanism': 'PLAIN',
        'sasl.username': os.getenv('CONFLUENT_API_KEY'),
        'sasl.password': os.getenv('CONFLUENT_API_SECRET'),
        'client.id': socket.gethostname()
    }

# Initialize Kafka Producer
kafka_config = read_kafka_config()
producer = Producer(kafka_config)

def delivery_report(err, msg):
    """Callback for Kafka message delivery reports"""
    if err is not None:
        print(f'❌ Message delivery failed: {err}')
    else:
        print(f'✅ Message delivered to {msg.topic()} [partition {msg.partition()}]')

# --- NEW ENDPOINT: Stream Pose Data to Kafka ---
@app.route('/stream-pose', methods=['POST'])
def stream_pose():
    """
    Receives pose landmarks from React frontend and streams them to Confluent Cloud
    
    Expected JSON payload:
    {
        "user_id": "athlete_1",
        "timestamp": 1234567890,
        "exercise": "pushup",
        "landmarks": [
            {"part": "left_elbow", "x": 0.5, "y": 0.3, "z": -0.1, "visibility": 0.99},
            ...
        ]
    }
    """
    try:
        data = request.json
        
        # Validate required fields
        if not data or 'landmarks' not in data:
            return jsonify({"error": "Missing landmarks data"}), 400
        
        # Add server timestamp if not provided
        if 'timestamp' not in data:
            import time
            data['timestamp'] = int(time.time() * 1000)  # milliseconds
        
        # Convert to JSON string for Kafka
        json_payload = json.dumps(data)
        
        # Get topic name from environment
        topic = os.getenv('POSE_TOPIC', 'pose-stream')
        
        # Produce to Kafka
        producer.produce(
            topic,
            key=data.get('user_id', 'default_user'),  # Use user_id as key for ordering
            value=json_payload,
            callback=delivery_report
        )
        
        # Trigger any outstanding callbacks
        producer.poll(0)
        
        return jsonify({
            "status": "streaming",
            "topic": topic,
            "timestamp": data['timestamp']
        }), 200
        
    except Exception as e:
        print(f"Error streaming pose data: {e}")
        return jsonify({"error": str(e)}), 500

# --- EXISTING ENDPOINTS (Keep for backward compatibility) ---
@app.route('/feedback')        
def getfeedback():
    """Legacy endpoint - returns hardcoded feedback from current frame"""
    update_feedback()
    return jsonify({
        "skill": str(feedback["skill"]) or "Detecting...",
        "grade": str(feedback["grade"]) or "Pending",
        "tips": list(feedback["tips"]) or "Looking"
    })

def update_feedback():
    """Legacy function - uses hardcoded angle evaluation"""
    global feedback
    skill_detected = feed.detect_skill()
    skill_feedback = feed.feed_back(skill_detected)
    accuracy = skill_feedback[-2] 
    skill_name = skill_feedback[-1]

    tips = []
    for i in range(0, len(skill_feedback) - 2):
        tips.append(skill_feedback[i])
    
    feedback["skill"] = skill_name
    feedback["grade"] = accuracy
    feedback["tips"] = tips

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "kafka_connected": kafka_config.get('bootstrap.servers') is not None
    })

# Cleanup on shutdown
def shutdown():
    """Flush any remaining messages before shutdown"""
    print("Flushing remaining messages...")
    producer.flush()

if __name__ == "__main__":
    import atexit
    atexit.register(shutdown)
    
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Flask server starting on port {port}")
    print(f"📡 Kafka bootstrap: {kafka_config.get('bootstrap.servers')}")
    print(f"📤 Streaming to topic: {os.getenv('POSE_TOPIC', 'pose-stream')}")
    
    app.run(debug=True, host="0.0.0.0", port=port)

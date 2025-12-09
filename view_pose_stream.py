"""
Simple consumer to verify pose data is flowing through Kafka
Run this while your Flask server and React app are running
"""
from confluent_kafka import Consumer
from dotenv import load_dotenv
import os
import json

load_dotenv()

def main():
    config = {
        'bootstrap.servers': os.getenv('CONFLUENT_BOOTSTRAP_SERVERS'),
        'security.protocol': 'SASL_SSL',
        'sasl.mechanism': 'PLAIN',
        'sasl.username': os.getenv('CONFLUENT_API_KEY'),
        'sasl.password': os.getenv('CONFLUENT_API_SECRET'),
        'group.id': 'test-viewer',
        'auto.offset.reset': 'latest'  # Only show new messages
    }
    
    consumer = Consumer(config)
    topic = os.getenv('POSE_TOPIC', 'pose-stream')
    consumer.subscribe([topic])
    
    print("="*60)
    print(f"👀 Watching for pose data on topic: {topic}")
    print("="*60)
    print("\nWaiting for messages... (Ctrl+C to stop)\n")
    
    message_count = 0
    
    try:
        while True:
            msg = consumer.poll(1.0)
            
            if msg is None:
                continue
            if msg.error():
                print(f"❌ Error: {msg.error()}")
                continue
            
            message_count += 1
            value = json.loads(msg.value().decode('utf-8'))
            
            print(f"\n📨 Message #{message_count}")
            print(f"   User: {value.get('user_id')}")
            print(f"   Exercise: {value.get('exercise')}")
            print(f"   Landmarks: {len(value.get('landmarks', []))}")
            print(f"   Timestamp: {value.get('timestamp')}")
            
            # Show a few key angles if available
            if 'angles' in value and value['angles']:
                print(f"   Sample Angles:")
                for key, val in list(value['angles'].items())[:3]:
                    print(f"      {key}: {val}°")
            
    except KeyboardInterrupt:
        print(f"\n\n✅ Received {message_count} messages total")
    finally:
        consumer.close()

if __name__ == "__main__":
    main()

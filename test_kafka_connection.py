"""
Test script to verify Confluent Cloud connection
Run this to make sure your credentials are working before integrating with the full app
"""
from confluent_kafka import Producer, Consumer
from dotenv import load_dotenv
import os
import json
import time

# Load environment variables
load_dotenv()

def get_kafka_config():
    """Load Kafka configuration from .env file"""
    return {
        'bootstrap.servers': os.getenv('CONFLUENT_BOOTSTRAP_SERVERS'),
        'security.protocol': 'SASL_SSL',
        'sasl.mechanism': 'PLAIN',
        'sasl.username': os.getenv('CONFLUENT_API_KEY'),
        'sasl.password': os.getenv('CONFLUENT_API_SECRET'),
    }

def test_producer():
    """Test producing a message to Kafka"""
    print("\n🧪 Testing Kafka Producer...")
    
    config = get_kafka_config()
    config['client.id'] = 'test-producer'
    
    producer = Producer(config)
    topic = os.getenv('POSE_TOPIC', 'pose-stream')
    
    # Create a test message
    test_message = {
        "user_id": "test_user",
        "timestamp": int(time.time() * 1000),
        "exercise": "test",
        "landmarks": [
            {"part": "left_shoulder", "x": 0.5, "y": 0.3, "z": -0.1, "visibility": 0.99}
        ]
    }
    
    def delivery_callback(err, msg):
        if err:
            print(f"❌ Delivery failed: {err}")
        else:
            print(f"✅ Message delivered to {msg.topic()} [partition {msg.partition()}]")
    
    try:
        producer.produce(
            topic,
            key="test_user",
            value=json.dumps(test_message),
            callback=delivery_callback
        )
        
        print(f"📤 Producing test message to topic '{topic}'...")
        producer.flush(timeout=10)
        print("✅ Producer test successful!")
        return True
        
    except Exception as e:
        print(f"❌ Producer test failed: {e}")
        return False

def test_consumer():
    """Test consuming messages from Kafka"""
    print("\n🧪 Testing Kafka Consumer...")
    
    config = get_kafka_config()
    config['group.id'] = 'test-consumer-group'
    config['auto.offset.reset'] = 'earliest'
    config['client.id'] = 'test-consumer'
    
    consumer = Consumer(config)
    topic = os.getenv('POSE_TOPIC', 'pose-stream')
    
    try:
        consumer.subscribe([topic])
        print(f"📥 Subscribed to topic '{topic}'")
        print("⏳ Waiting for messages (will timeout after 10 seconds)...")
        
        start_time = time.time()
        message_count = 0
        
        while time.time() - start_time < 10:  # 10 second timeout
            msg = consumer.poll(1.0)
            
            if msg is None:
                continue
            if msg.error():
                print(f"❌ Consumer error: {msg.error()}")
                continue
                
            message_count += 1
            key = msg.key().decode('utf-8') if msg.key() else None
            value = msg.value().decode('utf-8')
            
            print(f"\n✅ Received message #{message_count}:")
            print(f"   Key: {key}")
            print(f"   Value: {value[:100]}...")  # First 100 chars
            
        if message_count > 0:
            print(f"\n✅ Consumer test successful! Received {message_count} message(s)")
        else:
            print("\n⚠️  No messages received (this is OK if topic is empty)")
            
        return True
        
    except Exception as e:
        print(f"❌ Consumer test failed: {e}")
        return False
    finally:
        consumer.close()

def main():
    """Run all tests"""
    print("="*60)
    print("🚀 Confluent Cloud Connection Test")
    print("="*60)
    
    # Check environment variables
    print("\n📋 Checking configuration...")
    bootstrap = os.getenv('CONFLUENT_BOOTSTRAP_SERVERS')
    api_key = os.getenv('CONFLUENT_API_KEY')
    api_secret = os.getenv('CONFLUENT_API_SECRET')
    
    if not all([bootstrap, api_key, api_secret]):
        print("❌ Missing configuration! Please check your .env file:")
        print(f"   CONFLUENT_BOOTSTRAP_SERVERS: {'✅' if bootstrap else '❌'}")
        print(f"   CONFLUENT_API_KEY: {'✅' if api_key else '❌'}")
        print(f"   CONFLUENT_API_SECRET: {'✅' if api_secret else '❌'}")
        return
    
    print(f"✅ Bootstrap Server: {bootstrap}")
    print(f"✅ API Key: {api_key[:8]}...")
    print(f"✅ Topic: {os.getenv('POSE_TOPIC', 'pose-stream')}")
    
    # Run tests
    producer_ok = test_producer()
    
    if producer_ok:
        time.sleep(2)  # Wait a bit for message to be available
        consumer_ok = test_consumer()
    
    print("\n" + "="*60)
    print("🎉 All tests completed!")
    print("="*60)

if __name__ == "__main__":
    main()

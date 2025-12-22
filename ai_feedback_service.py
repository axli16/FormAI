"""
AI Consumer Service - Processes pose data from Kafka and generates intelligent feedback
This service:
1. Consumes pose landmarks from 'pose-stream' topic
2. Buffers 2-3 seconds of data
3. Sends to Google Vertex AI (Gemini) for analysis
4. Produces feedback to 'feedback-stream' topic
"""
from confluent_kafka import Consumer, Producer
from dotenv import load_dotenv
import os
import json
import time
from collections import deque
import socket
from feedback_logger import get_logger

# TODO: Install google-cloud-aiplatform
# pip install google-cloud-aiplatform

try:
    import vertexai
    from vertexai.generative_models import GenerativeModel
    VERTEX_AI_AVAILABLE = True
except ImportError:
    print("⚠️  google-cloud-aiplatform not installed. Install with: pip install google-cloud-aiplatform")
    VERTEX_AI_AVAILABLE = False

load_dotenv()

class PoseBuffer:
    """Buffers pose data for analysis"""
    def __init__(self, window_seconds=3, fps=5):
        self.window_size = window_seconds * fps  # Number of frames to buffer
        self.buffer = deque(maxlen=self.window_size)
        self.last_analysis_time = 0
        self.analysis_interval = window_seconds  # Analyze every N seconds
    
    def add(self, pose_data):
        """Add a pose frame to the buffer"""
        self.buffer.append(pose_data)
    
    def should_analyze(self):
        """Check if enough time has passed and buffer is full"""
        current_time = time.time()
        is_full = len(self.buffer) >= self.window_size
        time_elapsed = current_time - self.last_analysis_time >= self.analysis_interval
        return is_full and time_elapsed
    
    def get_sequence(self):
        """Get the current sequence for analysis"""
        self.last_analysis_time = time.time()
        return list(self.buffer)

class AIFeedbackGenerator:
    """Generates feedback using Google Vertex AI"""
    
    def __init__(self):
        self.model = None
        if VERTEX_AI_AVAILABLE:
            try:
                # Initialize Vertex AI
                project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
                if project_id:
                    vertexai.init(project=project_id, location="us-central1")
                    self.model = GenerativeModel("gemini-1.5-flash")
                    print("✅ Vertex AI initialized")
                else:
                    print("⚠️  GOOGLE_CLOUD_PROJECT not set in .env")
            except Exception as e:
                print(f"⚠️  Vertex AI initialization failed: {e}")
    
    def analyze_pose_sequence(self, pose_sequence):
        """
        Analyze a sequence of poses and generate feedback
        
        Args:
            pose_sequence: List of pose data dictionaries
        
        Returns:
            dict: {"skill": str, "grade": str, "tips": [str]}
        """
        if not self.model:
            # Fallback to rule-based analysis
            return self._rule_based_analysis(pose_sequence)
        
        try:
            # Get the exercise type from the first frame
            exercise = pose_sequence[0].get('exercise', 'unknown')
            
            # Create a summary of the sequence
            summary = self._create_sequence_summary(pose_sequence)
            
            # Create prompt for Gemini
            prompt = self._create_analysis_prompt(exercise, summary)
            
            # Get AI response
            response = self.model.generate_content(prompt)
            
            # Parse response
            return self._parse_ai_response(response.text, exercise)
            
        except Exception as e:
            print(f"AI analysis error: {e}")
            return self._rule_based_analysis(pose_sequence)
    
    def _create_sequence_summary(self, pose_sequence):
        """Create a text summary of the pose sequence"""
        if not pose_sequence:
            return "No data"
        
        # Get average angles from the sequence
        all_angles = {}
        for frame in pose_sequence:
            angles = frame.get('angles', {})
            for key, value in angles.items():
                if key not in all_angles:
                    all_angles[key] = []
                all_angles[key].append(value)
        
        avg_angles = {k: sum(v)/len(v) for k, v in all_angles.items() if v}
        
        return f"Average angles over {len(pose_sequence)} frames: {json.dumps(avg_angles, indent=2)}"
    
    def _create_analysis_prompt(self, exercise, summary):
        """Create a prompt for Gemini"""
        prompts = {
            "handstand": """
You are a calisthenics coach analyzing a handstand. Here's the pose data:

{summary}

Analyze this handstand and provide:
1. A grade from 0-100
2. 2-3 specific tips for improvement

Focus on:
- Arm straightness (should be ~180°)
- Body alignment (stack angle should be ~180°)
- Leg straightness

Respond in this exact format:
GRADE: [number]
TIPS:
- [tip 1]
- [tip 2]
- [tip 3]
""",
            "front_lever": """
You are a calisthenics coach analyzing a front lever. Here's the pose data:

{summary}

Analyze this front lever and provide:
1. A grade from 0-100
2. 2-3 specific tips for improvement

Focus on:
- Body parallel to ground (flat body angle ~180°)
- Arm and body angle (~90°)
- Leg straightness

Respond in this exact format:
GRADE: [number]
TIPS:
- [tip 1]
- [tip 2]
- [tip 3]
""",
            "planche": """
You are a calisthenics coach analyzing a planche. Here's the pose data:

{summary}

Analyze this planche and provide:
1. A grade from 0-100
2. 2-3 specific tips for improvement

Focus on:
- Body parallel to ground
- Shoulder protraction
- Leg straightness

Respond in this exact format:
GRADE: [number]
TIPS:
- [tip 1]
- [tip 2]
- [tip 3]
""",
            "vertical_jump": """
You are an athletic performance coach analyzing a vertical jump. Here's the movement data over time:

{summary}

This data shows the athlete's body position throughout the jump sequence. Analyze:

1. **Crouch Phase**: How deep did they crouch? (hip and knee angles)
2. **Takeoff Power**: Did they explosively extend hips, knees, and ankles?
3. **Arm Swing**: Did arms swing upward to generate momentum?
4. **Peak Height**: Maximum vertical displacement of hips
5. **Landing**: Controlled landing with proper knee flexion?

Provide:
1. A grade from 0-100 based on jump technique
2. 2-3 specific tips to increase vertical jump height

Respond in this exact format:
GRADE: [number]
TIPS:
- [tip 1]
- [tip 2]
- [tip 3]
"""
        }
        
        template = prompts.get(exercise, prompts["handstand"])
        return template.format(summary=summary)
    
    def _parse_ai_response(self, response_text, exercise):
        """Parse Gemini's response into structured feedback"""
        try:
            lines = response_text.strip().split('\n')
            grade = "0"
            tips = []
            
            for line in lines:
                if line.startswith("GRADE:"):
                    grade = line.replace("GRADE:", "").strip()
                elif line.startswith("- "):
                    tips.append(line[2:].strip())
            print(f"AI response: {response_text}")
            return {
                "skill": exercise.replace("_", " ").title(),
                "grade": grade,
                "tips": tips
            }
        except:
            return self._rule_based_analysis([{"exercise": exercise}])
    
    def _rule_based_analysis(self, pose_sequence):
        """Fallback rule-based analysis"""
        return {"skill": "Unknown", "grade": "0", "tips": ["No pose data available"]}

        # if not pose_sequence:
        #     return {"skill": "Unknown", "grade": "0", "tips": ["No pose data available"]}
        
        # exercise = pose_sequence[0].get('exercise', 'unknown')
        
        # # Simple rule-based grading
        # avg_angles = {}
        # for frame in pose_sequence:
        #     angles = frame.get('angles', {})
        #     for key, value in angles.items():
        #         if key not in avg_angles:
        #             avg_angles[key] = []
        #         avg_angles[key].append(value)
        
        # # Calculate simple grade based on angle deviations
        # grade = 70  # Base grade
        # tips = []
        
        # # Vertical Jump Analysis
        # if exercise == 'vertical_jump':
        #     # Track hip height changes over the sequence
        #     hip_heights = []
        #     knee_angles = []
            
        #     for frame in pose_sequence:
        #         landmarks = frame.get('landmarks', [])
        #         # Find hip landmark
        #         for lm in landmarks:
        #             if 'hip' in lm.get('part', ''):
        #                 hip_heights.append(lm.get('y', 0))
        #                 break
                
        #         # Get knee angles
        #         angles = frame.get('angles', {})
        #         if 'LEG_ANGLE_LEFT' in angles:
        #             knee_angles.append(angles['LEG_ANGLE_LEFT'])
            
        #     if hip_heights:
        #         # Calculate jump metrics
        #         min_hip = min(hip_heights)  # Lowest point (crouch)
        #         max_hip = max(hip_heights)  # Highest point (peak)
        #         jump_range = abs(max_hip - min_hip)
                
        #         # Grade based on jump height (y-axis is inverted in mediapipe)
        #         if jump_range > 0.3:  # Significant vertical displacement
        #             grade = 85
        #             tips.append("Great jump height! Keep that explosive power")
        #         elif jump_range > 0.2:
        #             grade = 75
        #             tips.append("Good jump. Try to explode more powerfully from the crouch")
        #         else:
        #             grade = 60
        #             tips.append("Crouch deeper and explode upward more forcefully")
                
        #         # Check knee extension
        #         if knee_angles:
        #             max_knee = max(knee_angles)
        #             if max_knee < 160:
        #                 tips.append("Fully extend your knees at takeoff for maximum power")
        #             else:
        #                 tips.append("Good knee extension at takeoff")
                
        #         # Arm swing tip
        #         tips.append("Swing your arms upward explosively to add momentum")
            
        #     return {
        #         "skill": "Vertical Jump",
        #         "grade": str(grade),
        #         "tips": tips[:3]  # Limit to 3 tips
        #     }
        
        # # Static skills analysis (existing code)
        # # Check arm angles
        # if 'ARM_ANGLE_LEFT' in avg_angles:
        #     left_arm = sum(avg_angles['ARM_ANGLE_LEFT']) / len(avg_angles['ARM_ANGLE_LEFT'])
        #     if left_arm < 160:
        #         tips.append("Straighten your left arm more")
        #         grade -= 10
        
        # if 'ARM_ANGLE_RIGHT' in avg_angles:
        #     right_arm = sum(avg_angles['ARM_ANGLE_RIGHT']) / len(avg_angles['ARM_ANGLE_RIGHT'])
        #     if right_arm < 160:
        #         tips.append("Straighten your right arm more")
        #         grade -= 10
        
        # if not tips:
        #     tips.append("Good form! Keep practicing")
        
        # return {
        #     "skill": exercise.replace("_", " ").title(),
        #     "grade": str(max(0, grade)),
        #     "tips": tips
        # }

def main():
    """Main consumer loop"""
    print("="*60)
    print("🤖 AI Feedback Service Starting...")
    print("="*60)
    
    # Kafka Consumer Config
    consumer_config = {
        'bootstrap.servers': os.getenv('CONFLUENT_BOOTSTRAP_SERVERS'),
        'security.protocol': 'SASL_SSL',
        'sasl.mechanism': 'PLAIN',
        'sasl.username': os.getenv('CONFLUENT_API_KEY'),
        'sasl.password': os.getenv('CONFLUENT_API_SECRET'),
        'group.id': 'ai-feedback-service',
        'auto.offset.reset': 'latest'
    }
    
    # Kafka Producer Config
    producer_config = {
        'bootstrap.servers': os.getenv('CONFLUENT_BOOTSTRAP_SERVERS'),
        'security.protocol': 'SASL_SSL',
        'sasl.mechanism': 'PLAIN',
        'sasl.username': os.getenv('CONFLUENT_API_KEY'),
        'sasl.password': os.getenv('CONFLUENT_API_SECRET'),
        'client.id': socket.gethostname()
    }
    
    consumer = Consumer(consumer_config)
    producer = Producer(producer_config)
    
    pose_topic = os.getenv('POSE_TOPIC', 'pose-stream')
    feedback_topic = os.getenv('FEEDBACK_TOPIC', 'feedback-stream')
    
    consumer.subscribe([pose_topic])
    
    buffer = PoseBuffer(window_seconds=3, fps=5)
    ai_generator = AIFeedbackGenerator()
    
    # Initialize feedback logger
    feedback_logger = get_logger()
    
    print(f"✅ Consuming from: {pose_topic}")
    print(f"✅ Producing to: {feedback_topic}")
    print(f"✅ Logging feedback to: feedback_logs/")
    print("\n⏳ Waiting for pose data...\n")
    
    try:
        while True:
            msg = consumer.poll(1.0)
            
            if msg is None:
                continue
            if msg.error():
                print(f"❌ Consumer error: {msg.error()}")
                continue
            
            # Parse pose data
            pose_data = json.loads(msg.value().decode('utf-8'))
            buffer.add(pose_data)
            
            # Analyze when buffer is full
            if buffer.should_analyze():
                print("🔍 Analyzing pose sequence...")
                sequence = buffer.get_sequence()
                feedback = ai_generator.analyze_pose_sequence(sequence)
                
                print(f"   Skill: {feedback['skill']}")
                print(f"   Grade: {feedback['grade']}")
                print(f"   Tips: {feedback['tips']}")
                
                # Log the feedback for review
                feedback_logger.log_feedback(
                    feedback,
                    metadata={
                        "user_id": pose_data.get('user_id', 'unknown'),
                        "exercise": pose_data.get('exercise', 'unknown'),
                        "sequence_length": len(sequence)
                    }
                )
                
                # Produce feedback to Kafka
                producer.produce(
                    feedback_topic,
                    key=pose_data.get('user_id', 'user_1'),
                    value=json.dumps(feedback)
                )
                producer.flush()
                print("✅ Feedback sent to Kafka\n")
    
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down...")
    finally:
        consumer.close()

if __name__ == "__main__":
    main()

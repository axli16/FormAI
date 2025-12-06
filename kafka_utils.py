"""
Utility functions for converting MediaPipe landmarks to Kafka-friendly JSON format
"""
import json
from datetime import datetime

def mediapipe_to_json(landmarks, mp_pose, user_id="default_user", exercise="unknown"):
    """
    Convert MediaPipe pose landmarks to JSON format for Kafka streaming
    
    Args:
        landmarks: MediaPipe pose landmarks object
        mp_pose: MediaPipe pose solution object
        user_id: Unique identifier for the user
        exercise: Name of the exercise being performed
    
    Returns:
        Dictionary ready to be sent to Kafka
    """
    landmark_list = []
    
    # Map of landmark names for better readability
    landmark_names = {
        0: "nose",
        11: "left_shoulder",
        12: "right_shoulder",
        13: "left_elbow",
        14: "right_elbow",
        15: "left_wrist",
        16: "right_wrist",
        23: "left_hip",
        24: "right_hip",
        25: "left_knee",
        26: "right_knee",
        27: "left_ankle",
        28: "right_ankle"
    }
    
    # Extract key landmarks (not all 33, just the important ones for calisthenics)
    for idx, landmark in enumerate(landmarks):
        if idx in landmark_names:
            landmark_list.append({
                "part": landmark_names[idx],
                "x": round(landmark.x, 4),
                "y": round(landmark.y, 4),
                "z": round(landmark.z, 4),
                "visibility": round(landmark.visibility, 4)
            })
    
    return {
        "user_id": user_id,
        "timestamp": int(datetime.now().timestamp() * 1000),  # milliseconds
        "exercise": exercise,
        "landmarks": landmark_list
    }

def calculate_angles_from_landmarks(landmarks_dict):
    """
    Calculate key angles from landmark positions
    This can be used for quick client-side validation
    
    Args:
        landmarks_dict: Dictionary of landmarks from mediapipe_to_json
    
    Returns:
        Dictionary of calculated angles
    """
    import math
    
    def get_landmark(name, landmarks):
        for lm in landmarks:
            if lm['part'] == name:
                return lm
        return None
    
    def calculate_angle(a, b, c):
        """Calculate angle between three points"""
        if not all([a, b, c]):
            return None
            
        radians = math.atan2(c['y'] - b['y'], c['x'] - b['x']) - \
                  math.atan2(a['y'] - b['y'], a['x'] - b['x'])
        angle = abs(radians * 180.0 / math.pi)
        
        if angle > 180.0:
            angle = 360 - angle
            
        return round(angle, 2)
    
    landmarks = landmarks_dict.get('landmarks', [])
    
    # Calculate key angles
    angles = {}
    
    # Left arm angle
    left_shoulder = get_landmark('left_shoulder', landmarks)
    left_elbow = get_landmark('left_elbow', landmarks)
    left_wrist = get_landmark('left_wrist', landmarks)
    angles['left_arm'] = calculate_angle(left_shoulder, left_elbow, left_wrist)
    
    # Right arm angle
    right_shoulder = get_landmark('right_shoulder', landmarks)
    right_elbow = get_landmark('right_elbow', landmarks)
    right_wrist = get_landmark('right_wrist', landmarks)
    angles['right_arm'] = calculate_angle(right_shoulder, right_elbow, right_wrist)
    
    # Left leg angle
    left_hip = get_landmark('left_hip', landmarks)
    left_knee = get_landmark('left_knee', landmarks)
    left_ankle = get_landmark('left_ankle', landmarks)
    angles['left_leg'] = calculate_angle(left_hip, left_knee, left_ankle)
    
    # Right leg angle
    right_hip = get_landmark('right_hip', landmarks)
    right_knee = get_landmark('right_knee', landmarks)
    right_ankle = get_landmark('right_ankle', landmarks)
    angles['right_leg'] = calculate_angle(right_hip, right_knee, right_ankle)
    
    return angles

def print_landmark_summary(landmarks_dict):
    """Pretty print landmark data for debugging"""
    print(f"\n{'='*50}")
    print(f"User: {landmarks_dict.get('user_id')}")
    print(f"Exercise: {landmarks_dict.get('exercise')}")
    print(f"Timestamp: {landmarks_dict.get('timestamp')}")
    print(f"Landmarks detected: {len(landmarks_dict.get('landmarks', []))}")
    
    angles = calculate_angles_from_landmarks(landmarks_dict)
    print(f"\nKey Angles:")
    for angle_name, angle_value in angles.items():
        if angle_value:
            print(f"  {angle_name}: {angle_value}°")
    print(f"{'='*50}\n")

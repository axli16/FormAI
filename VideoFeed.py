import cv2
import mediapipe as mp
import numpy as np
from threading import Lock
from moviepy import VideoFileClip
import boto3
import uuid

import joint
from constants import skills, positions

BUCKET = 'calivideo'


class VideoCamera(object):
    def __init__(self, video_source= 0):
        self.source = 0
        self.video = cv2.VideoCapture(video_source)
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.landmarks = []
        self.angles = {}
        self.image = None
        self.lock = Lock()
        self.s3 = boto3.client('s3')
    
    def switch_video_source(self, video):
        with self.lock:
            self.video.release()
            self.video = cv2.VideoCapture(video)
            self.source = video
    
    def get_rotation(self, filepath):
        clip = VideoFileClip(filepath)
        return clip.rotation
    
    def __del__(self):
        self.video.release()

    def detect_skill(self):
        return joint.detect_skill(self.landmarks, self.mp_pose)
    
    def feed_back(self, skill):
        feedback = []
        skill_name = ""
        if skill == joint.skills.HANDSTAND:
            feedback = joint.evaluateHandstand(self.angles)
            skill_name = "Handstand"
        elif skill == joint.skills.FRONTLEVER:
            feedback = joint.evaluateFrontLever(self.angles)
            skill_name = "Front Lever"
        elif skill == joint.skills.NINTYHOLD:
            feedback = joint.evaluate90Hold(self.angles)
            skill_name = "90 Hold"
        elif skill == joint.skills.PLANCHE:
            feedback = joint.evaluatePlanche(self.angles)
            skill_name = "Planche"
        feedback.append(skill_name)
        return feedback
    

    # Rendering angles on joint point 
    def renderAngle(self,  point, angle):
        # Visualize angle 
        cv2.putText(self.image, str(int(angle)),
                    tuple(np.multiply(point, [640, 480]).astype(int)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA
                    )
    

    # Get the angles based on the points and what skill it is 
    def getAngles(self, landmarks, skill, mp_pose):
        angle_dict = {}

        #Left arm straight
        shoulderL = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
        elbowL =  [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
        wristL =  [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

        left_arm_angle = joint.calculate_angle(shoulderL, elbowL, wristL)
        self.renderAngle(elbowL, left_arm_angle)
        angle_dict[positions.ARM_ANGLE_LEFT] = left_arm_angle
        
        # Right arm straight
        shoulderR = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
        elbowR =  [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
        wristR =  [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]

        right_arm_angle = joint.calculate_angle(shoulderR, elbowR, wristR)
        self.renderAngle( elbowR, right_arm_angle)
        angle_dict[positions.ARM_ANGLE_RIGHT] = right_arm_angle

        # Left Leg straight
        hipL = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
        kneeL =  [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
        ankleL =  [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]

        left_leg_angle = joint.calculate_angle(hipL, kneeL, ankleL)
        self.renderAngle( kneeL, left_leg_angle)
        angle_dict[positions.LEG_ANGLE_LEFT] = left_leg_angle
        
        # Right leg straight
        hipR = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
        kneeR =  [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
        ankleR =  [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]

        right_leg_angle = joint.calculate_angle(hipR, kneeR, ankleR)
        self.renderAngle(kneeR, right_leg_angle)
        angle_dict[positions.LEG_ANGLE_RIGHT] = right_leg_angle

        if skill == skills.HANDSTAND:
            # Stack 
            stack_angle_left = joint.calculate_angle(wristL, shoulderL, hipL)
            stack_angle_right = joint.calculate_angle(wristR, shoulderR, hipR)
            self.renderAngle(shoulderL, stack_angle_left)
            self.renderAngle(shoulderR, stack_angle_right)
            angle_dict[positions.STACK_ANGLE_LEFT] = stack_angle_left
            angle_dict[positions.STACK_ANGLE_RIGHT] = stack_angle_right

        elif skill == skills.FRONTLEVER or skill == skills.PLANCHE or skill == skills.NINTYHOLD:
            # Hand position over hips around 90 degrees
            left_hand_position_front_lever = joint.calculate_angle(wristL, hipL, shoulderL)
            right_hand_position_front_lever = joint.calculate_angle(wristR, hipR, shoulderR)
            self.renderAngle(hipL, left_hand_position_front_lever)
            self.renderAngle(hipR, right_hand_position_front_lever)
            angle_dict[positions.NINTY_DEGREE_HAND_TO_HIP_LEFT] = left_hand_position_front_lever
            angle_dict[positions.NINTY_DEGREE_HAND_TO_HIP_RIGHT] = right_hand_position_front_lever

            #Flat body (Right now the only way I can think of to see if the body is paralled to ground as )
            left_shoulder_ankle = joint.calculate_angle(shoulderL, hipL, ankleL)
            right_shoulder_ankle = joint.calculate_angle(shoulderR, hipR, ankleR)
            angle_dict[positions.FLAT_BODY_LEFT] = left_shoulder_ankle
            angle_dict[positions.FLAT_BODY_RIGHT] = right_shoulder_ankle

            # Angle of arm and body to make sure paralled to ground
            arm_torso_angle_left = joint.calculate_angle(wristL, shoulderL, hipL)
            arm_torso_angle_right = joint.calculate_angle(wristR, shoulderR, hipR)
            angle_dict[positions.ARMPIT_ANGLE_LEFT] = arm_torso_angle_left
            angle_dict[positions.ARMPIT_ANGLE_RIGHT] = arm_torso_angle_right

        return angle_dict
    
    def process(self, skill):
        with self.lock:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            output_path =  self.source.replace('.mp4', '_processed.mp4')
            out = cv2.VideoWriter(output_path, fourcc, 30.0, (int(self.video.get(3)), int(self.video.get(4))))
            while self.video.isOpened():
                rotation = 0
                
                ret, frame = self.video.read() 
                # if not ret or frame is None:
                #     print("Frame not read — video likely ended.")
                #     # self.video.release()  # Release video to avoid broken state
                #     self.switch_video_source(0)
                #     return None
                if self.source != 0:
                    rotation = self.get_rotation(self.source)
                    if rotation == 90:
                        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
                    elif rotation == 180:
                        frame = cv2.rotate(frame, cv2.ROTATE_180)
                    elif rotation == 270:
                        frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)

                # Recolour to RGB 
                self.image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.image.flags.writeable = False 
                
                # Make Detection
                results = self.pose.process(self.image)

                # BGR for open cv 
                self.image.flags.writeable = True 
                self.image = cv2.cvtColor(self.image, cv2.COLOR_RGB2BGR)

                try: 
                    self.landmarks = results.pose_landmarks.landmark

                    # skill = self.detect_skill()
                    self.angles = self.getAngles(self.landmarks, skill, self.mp_pose)
                except:
                    pass
                
                # Render detections 
                self.mp_drawing.draw_landmarks(self.image, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)
                out.write(frame)
            
            self.video.release()
            out.release()
            

            s3_key = f"uploads/{uuid.uuid4()}_{self.source}"

            self.s3.upload_file(output_path, BUCKET, s3_key)

            url = f"https://{BUCKET}.s3.amazonaws.com/{s3_key}"
            return url


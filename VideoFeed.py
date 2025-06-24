import cv2
import mediapipe as mp
import joint

class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.landmarks = None
        self.angles
    
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
            feedback = skill_name = "Front Lever"
        elif skill == joint.skills.NINTYHOLD:
            feedback = joint.evaluate90Hold(self.angles)
            skill_name = "90 Hold"
        elif skill == joint.skills.PLANCHE:
            feedback = joint.evaluatePlanche(self.angles)
            skill_name = "Planche"
        feedback.append(skill_name)
        return feedback
    
    def get_frame(self):
        ret, frame = self.video.read() 

        # Recolour to RGB 
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False 
        
        # Make Detection
        results = self.pose.process(image)

        # BGR for open cv 
        image.flags.writeable = True 
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        try: 
            self.landmarks = results.pose_landmarks.landmark

            skill = self.detect_skill(self.landmarks, self.mp_pose)
            self.angles = joint.getAngles(self.landmarks, skill, image, self.mp_pose)
            

            # cv2.putText(image, skill_name, (200, 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
        except:
            pass

        # Render detections 
        self.mp_drawing.draw_landmarks(image, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)

        # cv2.imshow('Mediapipe Feed', image)

        #Encode the frame to JPEG
        ret, buffer = cv2.imencode('.jpg', image)
        image_bytes = buffer.tobytes()

        return image_bytes

        # if cv2.waitKey(10) & 0xFF == ord('q'):
        #     break

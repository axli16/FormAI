import cv2
import mediapipe as mp
import numpy as np
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose



def calculate_angle(a,b,c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180.0 :
        angle = 360 - angle

    return angle

cap = cv2.VideoCapture(0)
## Setup mediapipe instance 
with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose: # confidence for tracking too high means no tracking as it can't detect 
    while cap.isOpened(): 
        ret, frame = cap.read() 

        # Recolour to RGB 
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False 
        
        # Make Detection
        results = pose.process(image)

        # BGR for open cv 
        image.flags.writeable = True 
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        try: 
            landmarks = results.pose_landmarks.landmark
        except:
            pass

        # Render detections 
        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        cv2.imshow('Mediapipe Feed', image)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
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

if __name__ == "__main__":
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

                # Get coordinates 
                shoulderL = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                elbowL =  [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                wristL =  [landmarks[mp_pose.PoseLandmark.LEFT_WRIST].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

                #Calculate angle 
                angle = calculate_angle(shoulderL, elbowL, wristL)

                # Visualize angle 
                cv2.putText(image, str(angle),
                            tuple(np.multiply(elbowL, [640, 480]).astype(int)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA
                            )
                
                shoulderR = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].x, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
                elbowR =  [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW].x, landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
                wristR =  [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST].x, landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]

                #Calculate angle 
                angle = calculate_angle(shoulderR, elbowR, wristR)

                # Visualize angle 
                cv2.putText(image, str(angle),
                            tuple(np.multiply(elbowR, [640, 480]).astype(int)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA
                            )
            except:
                pass

            # Render detections 
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            cv2.imshow('Mediapipe Feed', image)

            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
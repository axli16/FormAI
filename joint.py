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

def renderAngle( p2, angle):
    

    # Visualize angle 
    cv2.putText(image, str(int(angle)),
                tuple(np.multiply(p2, [640, 480]).astype(int)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA
                            )

def checkHandstand(landmarks):
    arm_correction = "Good"
    leg_correction = "Good"
    stack_correction = "Good"

    # Get coordinates arms
    shoulderL = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
    elbowL =  [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
    wristL =  [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

    left_arm_angle = calculate_angle(shoulderL, elbowL, wristL)
    renderAngle(elbowL, left_arm_angle)
    
    shoulderR = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
    elbowR =  [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
    wristR =  [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]

    right_arm_angle = calculate_angle(shoulderR, elbowR, wristR)
    renderAngle( elbowR, right_arm_angle)

    # Get coordinates legs
    hipL = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
    kneeL =  [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
    ankleL =  [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]

    left_leg_angle = calculate_angle(hipL, kneeL, ankleL)
    renderAngle( kneeL, left_leg_angle)
    
    hipR = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
    kneeR =  [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
    ankleR =  [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]

    right_leg_angle = calculate_angle(hipR, kneeR, ankleR)
    renderAngle(kneeR, right_leg_angle)
    
    # Get coordinates for stack 
    stack_angle_left = calculate_angle(wristL, shoulderL, hipL)
    stack_angle_right = calculate_angle(wristR, shoulderR, hipR)
    renderAngle(shoulderL, stack_angle_left)
    renderAngle(shoulderR, stack_angle_right)

    if  left_arm_angle < 170.0  or right_arm_angle < 170.0 :
        arm_correction = "Arms too bent"
    else:
        arm_correction = "Arms Good"

    if left_leg_angle < 170.0 or right_leg_angle < 170.0:
        leg_correction = "Straighten legs"
    else:
        leg_correction = "Legs Good"

    if stack_angle_left < 170 or stack_angle_right < 170:
        # Wrist shoulder and hips are not stacked 
        stack_correction = "Not stacked"
    else:
        stack_correction = "Good Stack"

    cv2.putText(image, arm_correction, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA )
    cv2.putText(image, leg_correction, (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA )
    cv2.putText(image, stack_correction, (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA )

    return 


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

                checkHandstand(landmarks)

            except:
                pass

            # Render detections 
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            cv2.imshow('Mediapipe Feed', image)

            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
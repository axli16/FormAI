from flask import Flask, Response
import cv2
import mediapipe as mp
import numpy as np
from constants import skills, positions

app = Flask(__name__)

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose


# Calculations 

# Calculate the angle between 3 points on the mediapipe points 
def calculate_angle(a,b,c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180.0 :
        angle = 360 - angle

    return angle


#Score the skills
def calculateScore(total_angle):
    angle = 0
    angleP = 0
    for key, value in total_angle.items():
        angle += key
        angleP += value 
    score = (angle / (angleP)) * 100
    return int(score)


# Rendering angles on joint point 
def renderAngle( point, angle, image):
    # Visualize angle 
    cv2.putText(image, str(int(angle)),
                tuple(np.multiply(point, [640, 480]).astype(int)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA
                )


# Get the angles based on the points and what skill it is 
def getAngles(landmarks, skill, image):
    angle_dict = {}

    #Left arm straight
    shoulderL = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
    elbowL =  [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
    wristL =  [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

    left_arm_angle = calculate_angle(shoulderL, elbowL, wristL)
    renderAngle(elbowL, left_arm_angle, image)
    angle_dict[positions.ARM_ANGLE_LEFT] = left_arm_angle
    
    # Right arm straight
    shoulderR = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
    elbowR =  [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
    wristR =  [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]

    right_arm_angle = calculate_angle(shoulderR, elbowR, wristR)
    renderAngle( elbowR, right_arm_angle, image)
    angle_dict[positions.ARM_ANGLE_RIGHT] = right_arm_angle

    # Left Leg straight
    hipL = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
    kneeL =  [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
    ankleL =  [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]

    left_leg_angle = calculate_angle(hipL, kneeL, ankleL)
    renderAngle( kneeL, left_leg_angle, image)
    angle_dict[positions.LEG_ANGLE_LEFT] = left_leg_angle
    
    # Right leg straight
    hipR = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
    kneeR =  [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
    ankleR =  [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]

    right_leg_angle = calculate_angle(hipR, kneeR, ankleR)
    renderAngle(kneeR, right_leg_angle, image)
    angle_dict[positions.LEG_ANGLE_RIGHT] = right_leg_angle

    if skill == skills.HANDSTAND:
        # Stack 
        stack_angle_left = calculate_angle(wristL, shoulderL, hipL)
        stack_angle_right = calculate_angle(wristR, shoulderR, hipR)
        renderAngle(shoulderL, stack_angle_left, image)
        renderAngle(shoulderR, stack_angle_right, image)
        angle_dict[positions.STACK_ANGLE_LEFT] = stack_angle_left
        angle_dict[positions.STACK_ANGLE_RIGHT] = stack_angle_right

    elif skill == skills.FRONTLEVER or skill == skills.PLANCHE or skill == skills.NINTYHOLD:
        # Hand position over hips around 90 degrees
        left_hand_position_front_lever = calculate_angle(wristL, hipL, shoulderL)
        right_hand_position_front_lever = calculate_angle(wristR, hipR, shoulderR)
        renderAngle(hipL, left_hand_position_front_lever, image)
        renderAngle(hipR, right_hand_position_front_lever, image)
        angle_dict[positions.NINTY_DEGREE_HAND_TO_HIP_LEFT] = left_hand_position_front_lever
        angle_dict[positions.NINTY_DEGREE_HAND_TO_HIP_RIGHT] = right_hand_position_front_lever

        #Flat body (Right now the only way I can think of to see if the body is paralled to ground as )
        left_shoulder_ankle = calculate_angle(shoulderL, hipL, ankleL)
        right_shoulder_ankle = calculate_angle(shoulderR, hipR, ankleR)
        angle_dict[positions.FLAT_BODY_LEFT] = left_shoulder_ankle
        angle_dict[positions.FLAT_BODY_RIGHT] = right_shoulder_ankle

        # Angle of arm and body to make sure paralled to ground
        arm_torso_angle_left = calculate_angle(wristL, shoulderL, hipL)
        arm_torso_angle_right = calculate_angle(wristR, shoulderR, hipR)
        angle_dict[positions.ARMPIT_ANGLE_LEFT] = arm_torso_angle_left
        angle_dict[positions.ARMPIT_ANGLE_RIGHT] = arm_torso_angle_right

    

    return angle_dict

#Evaluate poses 

#Score the handstand 
def evaluateHandstand(landmarks, image):
    arm_correction = "Good"
    leg_correction = "Good"
    stack_correction = "Good"

    angles = getAngles(landmarks, skills.HANDSTAND, image)
    
    if  angles[positions.ARM_ANGLE_LEFT] < 170.0  or angles[positions.ARM_ANGLE_RIGHT] < 170.0 :
        arm_correction = "Arms too bent"
    else:
        arm_correction = "Arms Good"

    if angles[positions.LEG_ANGLE_LEFT] < 170.0 or angles[positions.LEG_ANGLE_RIGHT] < 170.0:
        leg_correction = "Straighten legs"
    else:
        leg_correction = "Legs Good"

    if angles[positions.STACK_ANGLE_LEFT] < 170 or angles[positions.STACK_ANGLE_RIGHT] < 170:
        # Wrist shoulder and hips are not stacked 
        stack_correction = "Not stacked"
    else:
        stack_correction = "Good Stack"
    
    
    # Calulate score 
    angle_sum = {
        angles[positions.ARM_ANGLE_LEFT]: 180,
        angles[positions.ARM_ANGLE_RIGHT]: 180, 
        angles[positions.LEG_ANGLE_LEFT]: 180,
        angles[positions.LEG_ANGLE_RIGHT]: 180, 
        angles[positions.STACK_ANGLE_LEFT]: 180,
        angles[positions.STACK_ANGLE_RIGHT]: 180
    }

    score = calculateScore(angle_sum)
    percentage = str(score) + "%"


    # Render tips and score 
    cv2.putText(image, arm_correction, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA )
    cv2.putText(image, leg_correction, (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA )
    cv2.putText(image, stack_correction, (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA )
    cv2.putText(image, percentage, (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA )

    return 

#score the front lever 
def evaluateFrontLever(landmarks, image):
    arm_correction = "Good"
    leg_correction = "Good"
    wrist_position = "Good"
    arm_angle = "Good"
    flat_body = "Good"


    angles = getAngles(landmarks, skills.FRONTLEVER, image)


    if  angles[positions.ARM_ANGLE_LEFT] < 170.0  or angles[positions.ARM_ANGLE_RIGHT] < 170.0 :
        arm_correction = "Arms too bent"
    else:
        arm_correction = "Arms Good"

    if angles[positions.LEG_ANGLE_LEFT] < 170.0 or angles[positions.LEG_ANGLE_RIGHT] < 170.0:
        leg_correction = "Straighten legs"
    else:
        leg_correction = "Legs Good"

    if 60 < angles[positions.NINTY_DEGREE_HAND_TO_HIP_LEFT] < 100 or 60 < angles[positions.NINTY_DEGREE_HAND_TO_HIP_RIGHT] < 100:
        # 
        wrist_position = "Good, hands over hips"
    else:
        wrist_position = "Hands not over hips"
    
    #TODO:gotta figure how this check works or if needed 
    if angles[positions.ARMPIT_ANGLE_LEFT] > 45.0 or angles[positions.ARMPIT_ANGLE_RIGHT] > 45.0:
        arm_angle = "arms to raised"
    else:
        arm_angle = "Arm Angle Good"

    if angles[positions.FLAT_BODY_LEFT] < 170.0 or angles[positions.FLAT_BODY_RIGHT] < 170.0:
        flat_body = "Body not flat"
    else:
        flat_body = "Good flat body"
    
    #calculate score
    angle_sum = {
        angles[positions.ARM_ANGLE_LEFT]: 180,
        angles[positions.ARM_ANGLE_RIGHT]: 180, 
        angles[positions.LEG_ANGLE_LEFT]: 180,
        angles[positions.LEG_ANGLE_RIGHT]: 180, 
        angles[positions.NINTY_DEGREE_HAND_TO_HIP_LEFT]: 90,
        angles[positions.NINTY_DEGREE_HAND_TO_HIP_RIGHT]: 90
    }

    score = calculateScore(angle_sum)
    percentage = str(score) + "%"

    # Render tips and score 
    cv2.putText(image, arm_correction, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA )
    cv2.putText(image, leg_correction, (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA )
    cv2.putText(image, wrist_position, (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA )
    cv2.putText(image, percentage, (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA )

    return 


#Score the planche
def evaluatePlanche(landmarks, image):
    arm_correction = "Good"
    leg_correction = "Good"
    wrist_position = "Good"
    arm_angle = "Good"
    flat_body = "Good"


    angles = getAngles(landmarks, skills.PLANCHE, image)


    if  angles[positions.ARM_ANGLE_LEFT] < 170.0  or angles[positions.ARM_ANGLE_RIGHT] < 170.0 :
        arm_correction = "Arms too bent"
    else:
        arm_correction = "Arms Good"

    if angles[positions.LEG_ANGLE_LEFT] < 170.0 or angles[positions.LEG_ANGLE_RIGHT] < 170.0:
        leg_correction = "Straighten legs"
    else:
        leg_correction = "Legs Good"

    if 60 < angles[positions.NINTY_DEGREE_HAND_TO_HIP_LEFT] < 100 or 60 < angles[positions.NINTY_DEGREE_HAND_TO_HIP_RIGHT] < 100:
        # 
        wrist_position = "Good, hands over hips"
    else:
        wrist_position = "Hands not over hips"
    
    #TODO:gotta figure how this check works or if needed 
    if angles[positions.ARMPIT_ANGLE_LEFT] < 20.0 or angles[positions.ARMPIT_ANGLE_RIGHT] < 20.0:
        arm_angle = "Lift lower body"
    else:
        arm_angle = "Good"

    if angles[positions.FLAT_BODY_LEFT] < 170.0 or angles[positions.FLAT_BODY_RIGHT] < 170.0:
        flat_body = "Body not flat"
    else:
        flat_body = "Good flat body"
    
    #calculate score
    angle_sum = {
        angles[positions.ARM_ANGLE_LEFT]: 180,
        angles[positions.ARM_ANGLE_RIGHT]: 180, 
        angles[positions.LEG_ANGLE_LEFT]: 180,
        angles[positions.LEG_ANGLE_RIGHT]: 180, 
        angles[positions.NINTY_DEGREE_HAND_TO_HIP_LEFT]: 90,
        angles[positions.NINTY_DEGREE_HAND_TO_HIP_RIGHT]: 90
    }

    score = calculateScore(angle_sum)
    percentage = str(score) + "%"

    # Render tips and score 
    cv2.putText(image, arm_correction, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA )
    cv2.putText(image, leg_correction, (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA )
    cv2.putText(image, wrist_position, (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA )
    cv2.putText(image, percentage, (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA )

    return 


#Score the planche
def evaluate90Hold(landmarks, image):
    arm_correction = "Good"
    leg_correction = "Good"
    wrist_position = "Good"
    flat_body = "Good"


    angles = getAngles(landmarks, skills.NINTYHOLD, image)


    if  80.0 < angles[positions.ARM_ANGLE_LEFT] < 105.0  or 80.0< angles[positions.ARM_ANGLE_RIGHT] < 105.0 :
        arm_correction = "Good "
    else:
        arm_correction = "bend arms "

    if angles[positions.LEG_ANGLE_LEFT] < 170.0 or angles[positions.LEG_ANGLE_RIGHT] < 170.0:
        leg_correction = "Straighten legs"
    else:
        leg_correction = "Legs Good"

    if 60 < angles[positions.NINTY_DEGREE_HAND_TO_HIP_LEFT] < 100 or 60 < angles[positions.NINTY_DEGREE_HAND_TO_HIP_RIGHT] < 100:
        # 
        wrist_position = "Good, hands over hips"
    else:
        wrist_position = "Hands not over hips"
    
    if angles[positions.FLAT_BODY_LEFT] < 170.0 or angles[positions.FLAT_BODY_RIGHT] < 170.0:
        flat_body = "Body not flat"
    else:
        flat_body = "Good flat body"
    
    #calculate score
    angle_sum = {
        angles[positions.ARM_ANGLE_LEFT]: 90,
        angles[positions.ARM_ANGLE_RIGHT]: 90, 
        angles[positions.LEG_ANGLE_LEFT]: 180,
        angles[positions.LEG_ANGLE_RIGHT]: 180, 
        angles[positions.NINTY_DEGREE_HAND_TO_HIP_LEFT]: 90,
        angles[positions.NINTY_DEGREE_HAND_TO_HIP_RIGHT]: 90
    }

    score = calculateScore(angle_sum)
    percentage = str(score) + "%"

    # Render tips and score 
    cv2.putText(image, arm_correction, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA )
    cv2.putText(image, leg_correction, (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA )
    cv2.putText(image, wrist_position, (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA )
    cv2.putText(image, percentage, (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA )

    return 
# Determines what skill is being shown at the moment
def detect_skill(landmarks):

    #hand value coordinates
    left_wrist_position = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
    right_wrist_position = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]

    # Hip value coordinates 
    left_hip_position = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
    right_hip_position = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]

    # 
    if left_wrist_position[1] < left_hip_position[1] and right_wrist_position[1] < right_hip_position[1]: # if wrist position is higher than the hip position 
        return skills.FRONTLEVER
    else:
        left_shoulder_position = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
        right_shoulder_position = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]

        angle_shoulder_left = calculate_angle(left_wrist_position, left_shoulder_position, left_hip_position)
        angle_shoulder_right = calculate_angle(right_wrist_position, right_shoulder_position, right_hip_position)

        if angle_shoulder_left > 100.0 and angle_shoulder_right > 100.0 and left_hip_position[1] < left_shoulder_position[1] and right_hip_position[1] < right_shoulder_position[1]:
            return skills.HANDSTAND
        
        left_elbow_position = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
        right_elbow_position = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]

        angle_elbow_left = calculate_angle(left_shoulder_position, left_elbow_position, left_wrist_position)
        angle_elbow_right = calculate_angle(right_shoulder_position, right_elbow_position, right_wrist_position)

        if angle_elbow_left < 165.0 and angle_elbow_right < 165.0: 
            return skills.NINTYHOLD
        else: 
            return skills.PLANCHE
    
    return skills.UNKNOWN


def runVideo():
    cap = cv2.VideoCapture(0)
    skill = skills.HANDSTAND
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

                skill = detect_skill(landmarks)

                skill_name = ""
                if skill == skills.HANDSTAND:
                    evaluateHandstand(landmarks, image)
                    skill_name = "Handstand"
                elif skill == skills.FRONTLEVER:
                    evaluateFrontLever(landmarks, image)
                    skill_name = "Front Lever"
                elif skill == skills.NINTYHOLD:
                    #TODO: evaluate 
                    evaluate90Hold(landmarks, image)
                    skill_name = "90 Hold"
                elif skill == skills.PLANCHE:
                    #TODO: evaluate 
                    evaluatePlanche(landmarks, image)
                    skill_name = "Planche"

                cv2.putText(image, skill_name, (200, 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
            except:
                pass

            # Render detections 
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            cv2.imshow('Mediapipe Feed', image)

            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        
if __name__ == "__main__":
    runVideo()
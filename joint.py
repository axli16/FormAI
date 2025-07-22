import numpy as np
from constants import skills, positions



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


#Evaluate poses 

#Score the handstand 
def evaluateHandstand(angles):
    arm_correction = "Good"
    leg_correction = "Good"
    stack_correction = "Good"

    # angles = getAngles(landmarks, skills.HANDSTAND, image)
    
    if  angles[positions.ARM_ANGLE_LEFT] < 170.0  or angles[positions.ARM_ANGLE_RIGHT] < 170.0 :
        arm_correction = "Arms too bent"

    if angles[positions.LEG_ANGLE_LEFT] < 170.0 or angles[positions.LEG_ANGLE_RIGHT] < 170.0:
        leg_correction = "Point toes, and squeeze legs "

    if angles[positions.STACK_ANGLE_LEFT] < 170 or angles[positions.STACK_ANGLE_RIGHT] < 170:
        # Wrist shoulder and hips are not stacked 
        stack_correction = "Push through palms, and use fingers to control"
    
    
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
    # cv2.putText(image, arm_correction, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA )
    # cv2.putText(image, leg_correction, (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA )
    # cv2.putText(image, stack_correction, (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA )
    # cv2.putText(image, percentage, (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA )

    return [arm_correction, leg_correction, stack_correction, percentage]

#score the front lever 
def evaluateFrontLever( angles):
    arm_correction = "Good"
    leg_correction = "Good"
    wrist_position = "Good"
    arm_angle = "Good"
    flat_body = "Good"


    # angles = getAngles(landmarks, skills.FRONTLEVER, image)


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
    # cv2.putText(image, arm_correction, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA )
    # cv2.putText(image, leg_correction, (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA )
    # cv2.putText(image, wrist_position, (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA )
    # cv2.putText(image, percentage, (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA )

    return [arm_correction, leg_correction, wrist_position, percentage]


#Score the planche
def evaluatePlanche(angles):
    arm_correction = "Good"
    leg_correction = "Good"
    wrist_position = "Good"
    arm_angle = "Good"
    flat_body = "Good"


    # angles = getAngles(landmarks, skills.PLANCHE, image)


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
    # cv2.putText(image, arm_correction, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA )
    # cv2.putText(image, leg_correction, (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA )
    # cv2.putText(image, wrist_position, (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA )
    # cv2.putText(image, percentage, (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA )

    return [arm_correction, leg_correction, wrist_position, percentage]


#Score the planche
def evaluate90Hold(angles):
    arm_correction = "Good"
    leg_correction = "Good"
    wrist_position = "Good"
    flat_body = "Good"


    # angles = getAngles(landmarks, skills.NINTYHOLD, image)


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
    # cv2.putText(image, arm_correction, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA )
    # cv2.putText(image, leg_correction, (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA )
    # cv2.putText(image, wrist_position, (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA )
    # cv2.putText(image, percentage, (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA )

    return [arm_correction, leg_correction, wrist_position, percentage]

# Determines what skill is being shown at the moment
def detect_skill(landmarks, mp_pose):

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

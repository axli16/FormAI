from enum import Enum

#static skills 
class skills(Enum):     
    UNKNOWN = 0
    HANDSTAND = 1
    FRONTLEVER = 2
    PLANCHE = 3
    BACKLEVER = 4
    NINTYHOLD = 5

# Body positions
class positions(Enum):
    ARM_ANGLE_LEFT = 1
    ARM_ANGLE_RIGHT = 2
    LEG_ANGLE_LEFT = 3
    LEG_ANGLE_RIGHT = 4
    STACK_ANGLE_LEFT = 5
    STACK_ANGLE_RIGHT = 6
    NINTY_DEGREE_HAND_TO_HIP_LEFT = 7
    NINTY_DEGREE_HAND_TO_HIP_RIGHT = 8
    FLAT_BODY_LEFT = 9
    FLAT_BODY_RIGHT = 10
    ARMPIT_ANGLE_LEFT = 11
    ARMPIT_ANGLE_RIGHT = 12
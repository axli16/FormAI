from enum import Enum

#static skills 
class skills(Enum):     
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
    FRONT_LEVER_HAND_POSITION_LEFT = 7
    FRONT_LEVER_HAND_POSITION_RIGHT = 8
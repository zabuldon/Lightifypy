from enum import Enum


class Capability(Enum):
    """
    Enum of Lightify capabilities
    """
    Dimming = 0
    TunableWhite = 1
    PureWhite = 2
    RGB = 3
    Unk2 = 4
    MotionSensor = 5
    Switching = 6
    Unk3 = 7

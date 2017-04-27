from enum import Enum


class Command(Enum):
    # Retrieves information and status about all paired devices
    STATUS_ALL = (0x13, True)
    # Retrieves information about a single paired device
    STATUS_SINGLE = (0x68, False)
    # Retrieves information about all configured zones (group of devices)
    ZONE_LIST = (0x1E, True)
    # Retrieves information about a single configured broadcast
    ZONE_INFO = (0x26, False)
    # Reconfigures the luminance of the addressed device or broadcast
    LIGHT_LUMINANCE = (0x31, False)
    # Reconfigures the power on/off status of the addressed device or broadcast
    LIGHT_SWITCH = (0x32, False)
    # Reconfigures the white light temperature of the addressed device or broadcast
    LIGHT_TEMPERATURE = (0x33, False)
    # Reconfigures the RGB color of the addressed device or broadcast
    LIGHT_COLOR = (0x36, False)

    def get_id(self):
        return self.value[0]

    def is_broadcast(self):
        return self.value[1]

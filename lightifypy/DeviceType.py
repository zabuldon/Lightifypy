from enum import Enum


class DeviceType(Enum):
    Unknown = [-1]
    Bulb = [2, 4, 10]
    PlugSocket = [16]
    MotionSensor = [32]
    Switch = [64, 65]
    types = []

    @staticmethod
    def find_by_type_id(type_id):
        for d in DeviceType:
            if type_id in d.value:
                return d
        return DeviceType.Unknown

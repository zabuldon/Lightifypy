from lightifypy.LightifyLuminary import LightifyLuminary
from lightifypy.Capability import Capability
import struct


class LightifyZone(LightifyLuminary):
    def __init__(self, link, name, zone_id):
        LightifyLuminary.__init__(self, link, name, [Capability.TunableWhite, Capability.RGB])
        self.__zone_id = zone_id
        self.__name = name
        self.__luminaries = []
        self.__address = struct.pack('<Q', zone_id)
        self.type_flag = 0x02

    def address(self):
        return self.__address

    def is_powered(self):
        powered = True
        for luminary in self.__luminaries:
            if not luminary.is_powered():
                powered = False
                break
        return powered

    def get_temperature(self):
        temperature = -1
        for luminary in self.__luminaries:
            if temperature == -1:
                temperature = luminary.get_temperature()
            elif temperature != luminary.get_temperature():
                temperature = 2000
                break
        return temperature

    def get_luminance(self):
        luminance = -1
        for luminary in self.__luminaries:
            if luminance == -1:
                luminance = luminary.getLuminance()
            elif luminance != luminary.getLuminance():
                luminance = 100
                break
        return luminance

    def get_rgb(self):
        rgb = []
        for luminary in self.__luminaries:
            if not rgb:
                rgb = luminary.getRGB()
            elif set(rgb) == set(luminary.getRGB()):
                rgb = [0xff, 0xff, 0xff]
                break
        return rgb

    def get_zone_id(self):
        return self.__zone_id

    def to_string(self):
        return 'LightifyZone: zoneId={}, name={} address={}, luminaries={}'.format(
            self.__zone_id, self.get_name(), self.address(), ','.join(self.__luminaries))

    def add_device(self, luminary):
        self.__luminaries.append(luminary)

    def get_lums(self):
        return self.__luminaries

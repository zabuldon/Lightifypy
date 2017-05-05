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
        self.__lightifyLink = link
        self.type_flag = 0x02
        self.link = link

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
                luminance = luminary.get_luminance()
            elif luminance != luminary.get_luminance():
                luminance = 100
                break
        return luminance

    def get_rgb(self):
        rgb = None
        for luminary in self.__luminaries:
            if not rgb:
                rgb = luminary.get_rgb()
            elif rgb == luminary.get_rgb():
                rgb = (255, 255, 255)
                break
        return rgb

    def is_rgb(self):
        for luminary in self.__luminaries:
            if Capability.RGB in luminary.capabilities:
                return True
        else:
            return False

    def get_zone_id(self):
        return self.__zone_id

    def to_string(self):
        return 'LightifyZone: zoneId={}, name={} address={}, luminaries={}'.format(
            self.__zone_id, self.get_name(), self.address(), ','.join(self.__luminaries))

    def add_device(self, luminary):
        self.__luminaries.append(luminary)

    def get_lums(self):
        return self.__luminaries

    def update_powered(self, status):
        for lum in self.__luminaries:
            lum.update_powered(status)

    def update_luminance(self, luminance):
        for lum in self.__luminaries:
            self.__lightifyLink.logger.info('UPDATING STATUS.Ser lum to %s', luminance)
            lum.update_luminance(luminance)

    def update_temperature(self, temp):
        for lum in self.__luminaries:
            lum.update_temperature(temp)
from lightifypy.LightifyLuminary import LightifyLuminary
import struct


class LightifyLight(LightifyLuminary):
    def __init__(self, link, name, capabilities, address):
        LightifyLuminary.__init__(self, link, name, capabilities)
        self.__address = struct.pack('<Q', address)
        self.type_flag = 0x00

    def address(self):
        return self.__address

    def to_string(self):
        return "LightifyLight{ address={} }".format(self.__address)
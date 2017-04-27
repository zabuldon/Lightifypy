from lightifypy.Errors import LightifyException
from lightifypy.Command import Command
import struct


class PacketBuilder(object):
    def __init__(self, lightify_link):
        self.__lightify_link = lightify_link
        self.__luminary = None
        self.__command = None
        self.__data = bytes()
        self.__switching = -1
        self.__rgb = None
        self.__luminance = None
        self.__temperature = None
        self.__millis = 0
        self.__seq = 1
        self.__buffer = bytes()

    def with_(self, luminary):
        self.__luminary = luminary
        return self

    def on(self, command):
        self.__command = command
        return self

    def switching(self, switching):
        self.__switching = switching
        return self

    def rgb(self, r, g, b):
        self.__rgb = [r, g, b]
        return self

    def luminance(self, luminance):
        self.__luminance = luminance
        return self

    def temperature(self, temperature):
        self.__temperature = temperature
        return self

    def millis(self, millis):
        self.__millis = millis
        return self

    def data(self, data):
        self.__data = data
        return self

    def build(self):
        self.validate()
        packet_size = self.calculate_packet_size()

        request_id = self.__lightify_link.next_seq()
        self.put_header(packet_size, request_id)
        if not self.__luminary:
            self.put_global()
        else:
            self.put_addressable()
        while len(self.__buffer) < packet_size+2:
            self.__buffer += struct.pack('<B', 0)
        return self.__buffer

    def validate(self):
        command = self.__command
        if not command:
            assert LightifyException('command must be set')

        if command.is_broadcast():
            if not self.__luminary:
                assert LightifyException("luminary must be set for non-broadcast commands")

        if command == Command.LIGHT_COLOR and not self.__rgb:
            assert LightifyException("rgb not set for rgb command")

        if command == Command.LIGHT_LUMINANCE and not self.__luminance:
            assert LightifyException("luminance not set for luminance command")

        if command == Command.LIGHT_TEMPERATURE and not self.__temperature:
            assert LightifyException("temperature not set for temperature command")

    def calculate_packet_size(self):
        size = 6 if self.__command.is_broadcast() else 14
        if self.__luminary:
            size += 8
        if self.__switching != -1:
            size += 1
        if self.__rgb:
            size += 6
        if self.__luminance:
            size += 3
        if self.__temperature:
            size += 4
        if self.__data:
            size += len(self.__data)
        return size

    def put_header(self, packet_size, request_id):
        broadcast_or_unicast = 0x02 if self.__command.is_broadcast() else self.__luminary.type_flag
        self.__buffer += struct.pack('<H', packet_size)
        self.__buffer += struct.pack('<B', broadcast_or_unicast)
        self.__buffer += struct.pack('<B', self.__command.get_id())
        self.__buffer += struct.pack('<I', request_id)

    def put_global(self):
        if self.__command == Command.STATUS_ALL:
            self.__buffer += self.__data

    def put_addressable(self):
        self.__buffer += self.__luminary.address()
        if self.__command == Command.LIGHT_SWITCH:
            self.__buffer += struct.pack('<B', 0x01 if self.__switching else 0x00)
        elif self.__command == Command.LIGHT_TEMPERATURE:
            self.__buffer += struct.pack('<H', self.__temperature if self.__temperature else 0)
        elif self.__command == Command.LIGHT_LUMINANCE:
            self.__buffer += struct.pack('<B', self.__luminance if self.__luminance else 0)
            self.__buffer += struct.pack('<H', self.__millis)
        elif self.__command == Command.LIGHT_COLOR:
            r = self.__rgb[0]
            g = self.__rgb[1]
            b = self.__rgb[2]
            self.__buffer += struct.pack('<3B', r, g, b)
            self.__buffer += struct.pack('<B', 0xff)
            self.__buffer += struct.pack('<H', self.__millis)

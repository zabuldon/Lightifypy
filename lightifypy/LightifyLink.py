from lightifypy.Command import Command
from lightifypy.PacketBuilder import PacketBuilder
import struct
from lightifypy.LightifyZone import LightifyZone
import socket
import sys
from lightifypy.DeviceType import DeviceType
from lightifypy.Errors import LightifyException
from lightifypy.Constant import BITMASK_PURE_WHITE, BITMASK_RGB, BITMASK_TUNABLE_WHITE
from lightifypy.Capability import Capability
from lightifypy.LightifyLight import LightifyLight
import binascii
import logging
import threading


class LightifyLink:
    """
    Main class of Lightify connector
    """
    def __init__(self, address, port=4000):
        """
        :param address(str): IP Address of Lightify gateway
        :param port(int): TCP port of Lightify gateway (default 4000)
        """
        self.__charset = "cp437"
        self.__address = address
        self.__zones = {}
        self.__devices = {}
        self.__seq = 1
        self.__logger = logging.getLogger('lightfypy')
        self.__logger.addHandler(logging.NullHandler())
        self.__logger.info("Logging lightfypy")
        self.__lock = threading.RLock()
        self.logger = self.__logger
        with self.__lock:
            try:
                self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            except socket.error as msg:
                self.__logger.error(msg[1])
                sys.exit(1)
            try:
                self.__sock.connect((address, port))
            except socket.error as msg:
                self.__logger.error(msg[1])
                sys.exit(2)

            self.update()

    def __next_seq(self):
        """
        Generation of new sequence for packet ID
        :return int:
        """
        self.__seq += 1
        return self.__seq

    def next_seq(self):
        return self.__next_seq()

    def __send(self, data):
        """
        Sending data to a socket
        :param data: Buffer to send
        :return None: if success
        """
        return self.__sock.sendall(data)

    def __read_packet(self):
        """
        Read data from socket
        :return: bytes readed from socket
        """
        (size,) = struct.unpack('<H', self.__sock.recv(2))
        buffer = self.__sock.recv(size)
        return buffer

    def __fill_zone_list(self):
        """
        Filling zones list
        """
        command = Command.ZONE_LIST
        packet = PacketBuilder(self).on(command).build()
        buffer = self.__do_read(packet, command)
        (num,) = struct.unpack("<H", buffer[7:9])
        for i in range(0, num):
            pos = 9 + i * 18
            payload = buffer[pos:pos + 18]
            (zone_id, name) = struct.unpack("<H16s", payload)
            clear_name = bytes()
            for b in name:
                if b != 0x00:
                    clear_name += bytes([b])
            zone = LightifyZone(self, clear_name.decode('UTF-8'), zone_id)
            self.__zones[self.__get_zone_uid(zone_id)] = zone
            self.__handle_zone_info(zone)

    def __do_read(self, packet, command):
        """
        Main read function. This function sends data to socket than read response and check validity of received data
        :param packet: Bytes to be sent
        :param command: Command to be send. See Command.Command class to get more info
        :return: bytes of received data
        """
        self.__send(packet)
        buff = self.__read_packet()
        (error,) = self.__handle_header(packet, buff, command)
        if error != 0x00:
            sent = packet.upper()
            received = buff.upper()
            self.__logger.error("Packet content, sent: {}, received: {}".format(sent, received))
            self.__logger.error("Error code: 0x{}, command: {}".format(error, command.name))
            raise LightifyException('Error Stacktrace')
        return buff

    def __handle_zone_info(self, zone):
        """
        Filling zone information and grouping devices by zones.
        :param zone: Zone instance of LightifyZone.LightifyZone class
        """
        command = Command.ZONE_INFO
        packet = PacketBuilder(self).on(command).with_(zone).build()
        data = self.__do_read(packet, command)
        payload = data[7:]
        (zone_id, name, num) = struct.unpack("<H16sB", payload[:19])
        clear_name = bytes()
        for b in name:
            if b != 0x00:
                clear_name += bytes([b])
        name = clear_name
        self.__logger.debug("Idx %d: '%s' %d", zone_id, name, num)
        zone = self.__zones[self.__get_zone_uid(zone_id)]
        for i in range(0, num):
            pos = 7 + 19 + i * 8
            payload = data[pos:pos + 8]
            (addr,) = struct.unpack("<Q", payload[:8])
            light = self.__find_device(addr)
            zone.add_device(light)

    def __perform_search(self):
        """
        Search all devices attached to the Lightify network
        """
        command = Command.STATUS_ALL
        packet = PacketBuilder(self).on(command).data(struct.pack('<B', 0x01)).build()
        data = self.__do_read(packet, command)[7:]
        (num_of_lights,) = struct.unpack('<H', data[:2])
        record_size = 50
        for i in range(0, num_of_lights):
            pos = 2 + i * record_size
            payload = data[pos:pos + record_size]

            (device_id, device_address, dev_type) = struct.unpack('<HQB', payload[:11])
            (zone_id, status) = struct.unpack('<H?', payload[16:19])
            (lum, temp, r, g, b, w) = struct.unpack('<BHBBBB', payload[19:26])
            name = payload[26:]
            clear_name = bytes()
            for b in name:
                if b != 0x00:
                    clear_name += bytes([b])
            name = clear_name
            device_type = DeviceType.find_by_type_id(dev_type)
            if device_type != DeviceType.Bulb:
                self.__logger.warning("Found unsupported Lightify device, type id: {}. Skipping.".format(dev_type))
                continue
            is_rgb = (dev_type & BITMASK_RGB) == BITMASK_RGB
            is_tunable_white = (dev_type & BITMASK_TUNABLE_WHITE) == BITMASK_TUNABLE_WHITE
            is_pure_white = (dev_type & BITMASK_PURE_WHITE) == BITMASK_PURE_WHITE
            capabilities = []
            if is_rgb:
                capabilities.append(Capability.RGB)
            if is_tunable_white:
                capabilities.append(Capability.TunableWhite)
            if is_pure_white:
                capabilities.append(Capability.PureWhite)
            light = LightifyLight(self, name, capabilities, device_address)
            light.update_luminance(lum)
            light.update_powered(status)
            light.update_rgb(r, g, b)
            light.update_temperature(temp)
            (mac,) = struct.unpack('<Q', light.address())
            self.__devices[mac] = light

    def __perform_status_update(self, luminary):
        command = Command.STATUS_SINGLE
        packet = PacketBuilder(self).on(command).with_(luminary).build()
        buffer = self.__do_read(packet, command)
        (on, lum, temp, red, green, blue, h) = struct.unpack("<27x2BH4B16x", buffer)
        luminary.update_powered(on)
        luminary.set_luminance(lum)
        luminary.set_temperature(temp)
        luminary.set_rgb(red, green, blue)

    def __perform_switch(self, luminary, activate):
        command = Command.LIGHT_SWITCH
        packet = PacketBuilder(self).on(command).with_(luminary).switching(activate).build()
        self.__do_read(packet, command)
        luminary.update_powered(activate)

    def __perform_luminance(self, luminary, millis, luminance):
        command = Command.LIGHT_LUMINANCE
        packet = PacketBuilder(self).on(command).with_(luminary).luminance(luminance).millis(millis).build()
        self.__do_read(packet, command)
        luminary.update_luminance(luminance)
        luminary.update_powered(True)

    def __perform_rgb(self, luminary, r, g, b, millis):
        command = Command.LIGHT_COLOR
        packet = PacketBuilder(self).on(command).with_(luminary).rgb(r, g, b).millis(millis).build()
        self.__do_read(packet, command)
        luminary.update_rgb(r, g, b)
        luminary.update_powered(True)

    def __perform_temperature(self, luminary, temperature, millis):
        command = Command.LIGHT_TEMPERATURE
        packet = PacketBuilder(self).on(command).with_(luminary).temperature(temperature).millis(millis).build()
        self.__do_read(packet, command)
        luminary.update_temperature(temperature)
        luminary.update_powered(True)

    @staticmethod
    def __handle_header(packet, buffer, command):
        """
        :param packet: Data which was send to the Lightify gateway
        :param buffer: Data which was received from Lightify gateway
        :param command: Command which was sent. See Command.Command class to get more info
        :return: integer of error code
        """
        print(binascii.hexlify(buffer))
        (status, command_id) = struct.unpack('<BB', buffer[:2])
        if status != 0x01 and status != 0x03:
            sent = packet.upper()
            received = buffer.upper()
            print("Packet content, sent: {}, received: {}", sent, received)
            print("Status code: 0x{}, command: {}".format(status, command.name))
        if command_id != command.get_id():
            raise LightifyException("Illegal packet type: {} , command: {}".format(
                struct.pack('<B', command_id).hex().upper(), command.name))
        return struct.unpack('<B', buffer[6:7])

    @staticmethod
    def __get_zone_uid(zone_id):
        """
        :param zone_id: integer of zone identificator.
        :return: sting of zone id
        """
        return "zone::{}".format(zone_id)

    def __find_device(self, mac):
        """
        Return device by mac
        :param mac:
        :return:
        """
        return self.__devices[mac]

    def get_zones(self):
        """
        Get all zones
        :return: list of zones
        """
        return self.__zones

    def get_devices(self):
        """
        Get all found devices in network
        :return: list of devices

        """
        return self.__devices

    def update_status(self, target):
        self.__perform_status_update(target)

    def set_temperature(self, target, temperature, millis):
        self.__perform_temperature(target, temperature, millis)

    def set_rgb(self, target, r, g, b, millis):
        if len(values) > 3:
            self.__perform_rgb(target, r, g, b, millis)
        else:
            self.__logger.error('Value should have at least 3 values')

    def set_status(self, target, powered):
        if isinstance(target, LightifyZone) and not powered:
            self.__perform_luminance(target, 0, 0)
        self.__perform_switch(target, powered)

    def set_luminance(self, target, millis, lums):
        self.__perform_luminance(target, millis, lums)

    def update(self):
        self.__perform_search()
        self.__fill_zone_list()
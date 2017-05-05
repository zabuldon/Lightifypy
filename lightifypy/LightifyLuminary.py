from lightifypy.Capability import Capability


class LightifyLuminary(object):
    def __init__(self, link, name, capabilities):
        self.__lightifyLink = link
        self.__name = name
        self.__capabilities = capabilities
        self.__status = False
        self.__temperature = 0
        self.__luminance = 0
        self.__rgb = None
        self.__address = None
        self.type_flag = None
        self.__online = True

    def get_name(self):
        return self.__name

    def set_switch(self,  powered):
        self.__lightifyLink.set_status(self, powered)

    def set_luminance(self, millis, lum):
        self.__lightifyLink.set_luminance(self, millis, lum)

    def set_rgb(self, r, g, b, millis):
        self.__lightifyLink.set_rgb(self, r, g, b, millis)

    def set_temperature(self, temperature, millis):
        self.__lightifyLink.set_temperature(self, temperature, millis)

    def supports(self, capability):
        return capability in self.__capabilities

    def is_powered(self):
        return self.__status

    def get_temperature(self):
        return self.__temperature

    def get_luminance(self):
        return self.__luminance

    def get_rgb(self):
        return self.__rgb

    def to_string(self):
        return "LightifyLuminary( name='{}', status={}, temperature={}, luminance={}, rgb={}".format(
            self.__name, self.__status, self.__temperature, self.__luminance, ','.join(self.__rgb)
        )

    def is_rgb(self):
        return Capability.RGB in self.__capabilities

    def update_temperature(self, temperature):
        self.__temperature = temperature

    def update_luminance(self, luminance):
        self.__luminance = luminance

    def update_rgb(self, r, g, b):
        self.__rgb = (r, g, b)

    def update_powered(self, status):
        self.__status = status

    def address(self):
        return self.__address

    def update(self):
        self.__lightifyLink.update()
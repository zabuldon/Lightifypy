class LightifyLuminary(object):
    def __init__(self, link, name, capabilities):
        self.__lightifyLink = link
        self.__name = name
        self.__capabilities = capabilities
        self.__status = False
        self.__temperature = 0
        self.__luminance = 0
        self.__rgb = []
        self.__address = None
        self.type_flag = None
        self.__online = True

    def get_name(self):
        return self.__name

    def set_switch(self, activate, consumer):
        self.__lightifyLink.perform_switch(self, activate, consumer)

    def set_luminance(self, luminance, millis, consumer):
        self.__lightifyLink.perform_luminance(luminance, millis, consumer)

    def set_rgb(self, r, g, b, millis, consumer):
        self.__lightifyLink.perform_rgb(self, r, g, b, millis, consumer)

    def set_temperature(self, temperature, millis, consumer):
        self.__lightifyLink.perform_temperature(self, temperature, millis, consumer)

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

    def update_temperature(self, temperature):
        self.__temperature = temperature

    def update_luminance(self, luminance):
        self.__luminance = luminance

    def update_rgb(self, r, g, b):
        self.__rgb = [r, g, b]

    def update_powered(self, status):
        self.__status = status

    def update_online(self, val):
        self.__online = val

    def address(self):
        return self.__address

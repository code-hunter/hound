__author__ = 'chaclus'


class ProxyInfo(object):
    def __init__(self):
        self.ip = None
        self.port = None
        self.area = None
        self.level = None
        self.protocol = None
        self.speed = None
        self.isValid = None

    def as_dict(self):
        return {
            'ip': self.ip,
            'port': self.port,
            'area': self.area,
            'level': self.level,
            'protocol': self.protocol,
            'speed': self.speed,
            'isValid': self.isValid
        }
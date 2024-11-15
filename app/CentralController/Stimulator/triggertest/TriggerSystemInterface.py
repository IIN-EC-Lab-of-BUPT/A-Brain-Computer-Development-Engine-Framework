import abc


class TriggerSystemInterface(metaclass=abc.ABCMeta):

    def open(self):
        pass

    def send(self, event):
        pass

    def close(self):
        pass

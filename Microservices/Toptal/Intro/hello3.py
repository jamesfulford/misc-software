from time import sleep
from nameko.rpc import rpc


class GreetingService(object):
    name = "greeting_service"

    @rpc
    def hello(self, name):
        sleep(5)
        return "Hello, {}! This is the new format.".format(name)

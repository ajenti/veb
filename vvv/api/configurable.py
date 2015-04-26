from jadi import interface


@interface
class Configurable(object):
    name = None

    def __init__(self, context):
        self.context = context

    def configure(self):
        pass

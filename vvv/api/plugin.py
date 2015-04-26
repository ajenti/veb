from jadi import interface


@interface
class Plugin(object):
    name = None

    @classmethod
    def by_name(cls, context, name):
        for cmd in cls.classes():
            if cmd.name == name:
                return cmd(context)

    def __init__(self, context):
        self.context = context

    def add_config_defaults(self, config):
        pass

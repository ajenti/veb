from jadi import interface


class CommandArgumentError(Exception):
    pass


@interface
class Command(object):
    name = None
    usage = None

    @classmethod
    def by_name(cls, context, name):
        for cmd in cls.classes():
            if cmd.name == name:
                return cmd(context)

    def __init__(self, context):
        self.context = context

    def consume_arguments(self, argv):
        pass

    def run(self):
        raise NotImplementedError

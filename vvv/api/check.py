from jadi import interface


@interface
class Check(object):
    name = None

    def __init__(self, context):
        self.context = context

    def get_instances(self):
        return [[]]

    def get_name(self, *args):
        return self.name

    def run(self, *args):
        pass


class CheckFailure(Exception):
    pass

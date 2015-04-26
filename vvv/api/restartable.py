import logging

from jadi import interface


@interface
class Restartable(object):
    name = None

    def __init__(self, context):
        self.context = context
        self.scheduled = False

    def schedule_restart(self):
        logging.debug('Scheduling restart of %s', self.name)
        self.scheduled = True

    def restart(self):
        logging.info('Restarting %s', self.name)
        self.do_restart()
        self.scheduled = False

    def do_restart(self):
        raise NotImplementedError

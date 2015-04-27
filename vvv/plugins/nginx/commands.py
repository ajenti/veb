import logging
from jadi import component

from vvv.api.command import Command, CommandArgumentError
from vvv.api.config import MainConfig


@component(Command)
class WebsiteMaintenanceCommand(Command):
    name = 'maintenance'
    usage = '''
maintenance <website-name> on|off - enables (disables) maintenance mode for a website
'''

    def consume_arguments(self, argv):
        if len(argv) < 1:
            raise CommandArgumentError('short-name is required')
        if len(argv) < 2:
            raise CommandArgumentError('on|off is required')
        self.website_name = argv.pop(0)
        self.on = argv.pop(0) == 'on'

    def run(self):
        cfg = MainConfig.get(self.context)
        for website in cfg.data['websites']:
            if website['name'] == self.website_name:
                website['maintenance_mode'] = self.on
        cfg.save()

        logging.info('Website %s maintenance mode set to: %s', self.website_name, self.on)

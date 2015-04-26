import logging
from jadi import component

from vvv.api.command import Command, CommandArgumentError


@component(Command)
class HelpCommand(Command):
    name = 'help'
    usage = '''
help [command-name] - get help for a command
'''

    def consume_arguments(self, argv):
        if not argv:
            raise CommandArgumentError('command-name is required')
        self.command_name = argv.pop(0)

    def run(self):
        command = Command.by_name(self.context, self.command_name)
        if not command:
            logging.critical('Unknown command %s', self.command_name)
            return

        if not command.usage:
            logging.critical('Command %s has no usage information', self.command_name)
            return

        return command.usage

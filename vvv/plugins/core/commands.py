# encoding: utf8
import logging
import os
import subprocess
import tempfile
import yaml
from jadi import component

from vvv.api.command import Command, CommandArgumentError
from vvv.api.config import MainConfig
from vvv.api.check import Check, CheckFailure
from vvv.api.configurable import Configurable
from vvv.api.restartable import Restartable


@component(Command)
class CheckCommand(Command):
    name = 'check'
    usage = '''
check - run configuration checks
'''

    def run(self):
        failed = 0
        for check in Check.all(self.context):
            instances = check.get_instances()
            for instance in instances:
                try:
                    result = check.run(*instance)
                    message = None
                except CheckFailure as e:
                    result = False
                    message = str(e)

                if result:
                    logging.info('✓ %s' % check.get_name(*instance))
                else:
                    logging.error('✗ %s - failed' % check.get_name(*instance))
                    if message:
                        logging.error(message)
                    failed += 1

        if failed > 0:
            logging.error('------------------')
            logging.error('%i check(s) failed', failed)
            logging.error('------------------')
        else:
            logging.info('-------------------')
            logging.info('✓ All checks passed')
            logging.info('-------------------')


@component(Command)
class ApplyCommand(Command):
    name = 'apply'
    usage = '''
apply - re-apply current configuration
'''

    def run(self):
        for configurable in Configurable.all(self.context):
            logging.info('Configuring %s', configurable.name)
            configurable.configure()

        for restartable in Restartable.all(self.context):
            if restartable.scheduled:
                restartable.restart()

        logging.info('Configuration applied')


@component(Command)
class AddWebsiteCommand(Command):
    name = 'add'
    usage = '''
add <short-name> - creates a new website
'''

    def consume_arguments(self, argv):
        if not argv:
            raise CommandArgumentError('short-name is required')
        self.website_name = argv.pop(0)

    def run(self):
        ws = {
            'name': self.website_name,
        }

        cfg = MainConfig.get(self.context)
        cfg.data['websites'].append(ws)
        cfg.save()

        logging.info('Website %s added', self.website_name)


@component(Command)
class ListWebsitesCommand(Command):
    name = 'list'
    usage = '''
list - lists websites
'''

    def run(self):
        cfg = MainConfig.get(self.context)
        for ws in cfg.data['websites']:
            print '- %s' % ws['name']


@component(Command)
class EditWebsiteCommand(Command):
    name = 'edit'
    usage = '''
edit <short-name> - launches config editor for a website
'''

    def consume_arguments(self, argv):
        if not argv:
            raise CommandArgumentError('short-name is required')
        self.website_name = argv.pop(0)

    def run(self):
        cfg = MainConfig.get(self.context)
        for ws in cfg.data['websites']:
            if ws['name'] == self.website_name:
                self.website = ws
                break
        else:
            logging.critical('Website "%s" not found', self.website_name)
            return

        tmp = tempfile.NamedTemporaryFile(delete=False)
        tmp.write(yaml.safe_dump(
            ws,
            default_flow_style=False,
            encoding='utf-8',
            allow_unicode=True,
        ))
        tmp.close()

        editor = os.environ.get('EDITOR', 'nano' if os.path.exists('/usr/bin/nano') else 'vi')

        while True:
            if subprocess.call([editor, tmp.name]) == 0:
                try:
                    new_config = yaml.load(open(tmp.name))
                except Exception as e:
                    logging.critical('Config content is invalid: %s', str(e))
                    logging.info('File is retained in %s', tmp.name)
                    logging.info('Press Enter to continue editing, Ctrl-C to abort')
                    try:
                        raw_input()
                    except KeyboardInterrupt:
                        logging.critical('Aborted')
                        return
                    continue

                ws.update(new_config)
                os.unlink(tmp.name)
                cfg.save()
                logging.info('Updated configuration for %s', self.website_name)
                break
            else:
                logging.critical('Editor exited with an erroneous exitcode')
                logging.info('File is retained in %s', tmp.name)

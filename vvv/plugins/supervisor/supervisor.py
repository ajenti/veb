import logging
import os
import subprocess
from jadi import component

from vvv.api.app import AppType
from vvv.api.aug import Augeas
from vvv.api.config import MainConfig, SystemConfig
from vvv.api.configurable import Configurable
from vvv.api.check import Check, CheckFailure
from vvv.api.restartable import Restartable

from .plugin import SupervisorImpl


@component(Check)
class AppsCheck(Check):
    def get_instances(self):
        for website in MainConfig.get(self.context).data['websites']:
            prefix = 'veb-app-%s-' % website['name']
            for app_config in website['apps']:
                app_type = AppType.by_name(self.context, app_config['type'])
                if not app_type:
                    logging.warn('Skipping unknown app type "%s"', app_config['type'])
                    continue
                process_info = app_type.get_process(website, app_config)
                if process_info:
                    full_name = prefix + app_config['name'] + process_info.get('suffix', '')
                    yield [{
                        'full_name': full_name,
                        'website': website,
                        'app': app_config,
                    }]

    def get_name(self, info):
        return 'app %s/%s is running' % (
            info['website']['name'],
            info['app']['name'],
        )

    def run(self, info):
        o = subprocess.check_output(
            ['supervisorctl', 'status', info['full_name']]
        )
        if 'RUNNING' not in o:
            raise CheckFailure(o)
        return True


@component(Check)
class SupervisorServiceCheck(Check):
    name = 'supervisor is running'

    def run(self):
        return subprocess.call(
            ['service', SupervisorImpl.any(self.context).service_name, 'status']
        ) == 0


@component(AppType)
class GenericAppType(AppType):
    name = 'generic'

    def get_access_type(self, website_config, app_config):
        return None

    def get_access_params(self, website_config, app_config):
        return {}

    def get_process(self, website_config, app_config):
        return {
            'command': app_config['params']['command'],
            'directory': app_config['params']['directory'] or website_config['root'],
            'environment': app_config['params']['environment'],
            'user': app_config['params']['user'],
        }


@component(Configurable)
class Supervisor(Configurable):
    name = 'supervisor'

    def configure(self):
        aug = Augeas(
            modules=[{
                'name': 'Supervisor',
                'lens': 'Supervisor.lns',
                'incl': [
                    SystemConfig.get(self.context).data['supervisor']['config_file'],
                ]
            }],
            loadpath=os.path.dirname(__file__),
        )
        aug_path = '/files' + SystemConfig.get(self.context).data['supervisor']['config_file']
        aug.load()

        for website in MainConfig.get(self.context).data['websites']:
            prefix = 'veb-app-%s-' % website['name']

            for path in aug.match(aug_path + '/*'):
                if prefix in path:
                    aug.remove(path)

            for app_config in website['apps']:
                app_type = AppType.by_name(self.context, app_config['type'])
                if not app_type:
                    logging.warn('Skipping unknown app type "%s"', app_config['type'])
                    continue

                process_info = app_type.get_process(website, app_config)
                if process_info:
                    full_name = prefix + app_config['name'] + process_info.get('suffix', '')
                    path = aug_path + '/program:%s' % full_name
                    aug.set(path, None)
                    aug.set(path + '/command', process_info['command'])
                    aug.set(path + '/directory', process_info['directory'] or website['root'])
                    if process_info['environment']:
                        aug.set(path + '/environment', process_info['environment'])
                    aug.set(path + '/user', process_info['user'])
                    aug.set(path + '/killasgroup', 'true')
                    aug.set(path + '/stopasgroup', 'true')
                    aug.set(path + '/stdout_logfile', '%s/%s/%s.stdout.log' % (
                        SystemConfig.get(self.context).data['log_dir'],
                        website['name'],
                        app_config['name'],
                    ))
                    aug.set(path + '/stderr_logfile', '%s/%s/%s.stderr.log' % (
                        SystemConfig.get(self.context).data['log_dir'],
                        website['name'],
                        app_config['name'],
                    ))

        aug.save()
        SupervisorRestartable.get(self.context).schedule_restart()


@component(Restartable)
class SupervisorRestartable(Restartable):
    name = 'supervisor'

    def do_restart(self):
        subprocess.check_call(['service', SupervisorImpl.any(self.context).service_name, 'restart'])

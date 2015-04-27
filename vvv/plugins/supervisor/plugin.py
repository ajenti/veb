import os
from jadi import component, interface

from vvv.api.config import SystemConfig, MainConfig
from vvv.api.plugin import Plugin


@interface
class SupervisorImpl(object):
    default_pidfile = None

    def __init__(self, context):
        pass


@component(SupervisorImpl)
class SupervisorDebian(SupervisorImpl):
    default_config_file = '/etc/supervisor/supervisord.conf'
    service_name = 'supervisor'

    @classmethod
    def __verify__(cls):
        return os.path.exists('/etc/debian_version')


@component(SupervisorImpl)
class SupervisorCentOS(SupervisorImpl):
    default_config_file = '/etc/supervisord.conf'
    service_name = 'supervisord'

    @classmethod
    def __verify__(cls):
        return os.path.exists('/etc/redhat-release')


@component(Plugin)
class SupervisorPlugin(Plugin):
    name = 'supervisor'

    def add_config_defaults(self, config):
        impl = SupervisorImpl.any(self.context)

        if isinstance(config, MainConfig):
            config.data.setdefault('websites', [])

            for ws in config.data['websites']:
                for app in ws['apps']:
                    if app['type'] == 'generic':
                        app['params'].setdefault('user', 'root')
                        app['params'].setdefault('environment', '')
                        app['params'].setdefault('directory', None)
                        app['params'].setdefault('command', None)

        if isinstance(config, SystemConfig):
            config.data.setdefault('supervisor', {})
            config.data['supervisor'].setdefault('config_file', impl.default_config_file)

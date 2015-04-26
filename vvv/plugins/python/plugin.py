from jadi import component

from vvv.api.config import MainConfig
from vvv.api.plugin import Plugin


@component(Plugin)
class PythonPlugin(Plugin):
    name = 'python'

    def add_config_defaults(self, config):
        if isinstance(config, MainConfig):
            config.data.setdefault('websites', [])

            for ws in config.data['websites']:
                for app in ws['apps']:
                    if app['type'] == 'python-wsgi':
                        app['params'].setdefault('module', 'wsgi')
                        app['params'].setdefault('virtualenv', None)
                        app['params'].setdefault('user', 'root')
                        app['params'].setdefault('workers', None)
                        app['params'].setdefault('environment', None)
                        app['params'].setdefault('custom_conf', None)

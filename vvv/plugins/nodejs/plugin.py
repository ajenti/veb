from jadi import component

from vvv.api.config import MainConfig
from vvv.api.plugin import Plugin


@component(Plugin)
class NodeJSPlugin(Plugin):
    name = 'nodejs'

    def add_config_defaults(self, config):
        if isinstance(config, MainConfig):
            config.data.setdefault('websites', [])

            for ws in config.data['websites']:
                if ws['enabled']:
                    for app in ws['apps']:
                        if app['type'] == 'nodejs':
                            app['params'].setdefault('script', 'app.js')
                            app['params'].setdefault('node_binary', 'node')
                            app['params'].setdefault('user', 'root')
                            app['params'].setdefault('port', 8000)
                            app['params'].setdefault('environment', None)

from jadi import component

from vvv.api.app import AppType


@component(AppType)
class NodeJSType(AppType):
    name = 'nodejs'

    def get_access_type(self, website_config, app_config):
        return 'proxy'

    def get_access_params(self, website_config, app_config):
        return {
            'url': 'http://127.0.0.1:%s' % app_config['params']['port']
        }

    def get_process(self, website_config, app_config):
        p = {
            'command': '%s %s' % (
                app_config['params']['node_binary'],
                app_config['params']['script'] or '.',
            ),
            'user': app_config['params']['user'],
            'environment': app_config['params']['environment'],
            'directory': app_config['path'],
        }
        return p

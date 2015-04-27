from jadi import component

from vvv.api.app import AppType
from vvv.api.util import absolute_path


@component(AppType)
class NodeJSType(AppType):
    name = 'nodejs'

    def get_access_type(self, website, app):
        return 'proxy'

    def get_access_params(self, website, app):
        return {
            'url': 'http://127.0.0.1:%s' % app['params']['port']
        }

    def get_process(self, website, app):
        p = {
            'command': '%s %s' % (
                app['params']['node_binary'],
                app['params']['script'] or '.',
            ),
            'user': app['params']['user'],
            'environment': app['params']['environment'],
            'directory': absolute_path(app['path'], website['root']),
        }
        return p

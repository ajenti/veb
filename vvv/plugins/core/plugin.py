from jadi import component

from vvv.api.plugin import Plugin
from vvv.api.config import MainConfig, SystemConfig


@component(Plugin)
class CorePlugin(Plugin):
    name = 'core'

    def add_config_defaults(self, config):
        if isinstance(config, MainConfig):
            config.data.setdefault('websites', [])

            for ws in config.data['websites']:
                ws.setdefault('name', 'unnamed')
                ws.setdefault('enabled', True)

                ws.setdefault('domains', [])
                for domain in ws['domains']:
                    domain.setdefault('domain', 'example.com')

                ws.setdefault('apps', [])
                for app in ws['apps']:
                    app.setdefault('path', '/srv')
                    app.setdefault('name', 'unnamed')
                    app.setdefault('type', 'php-fpm')
                    app.setdefault('params', {})

                ws.setdefault('ports', [])
                for port in ws['ports']:
                    port.setdefault('host', None)
                    port.setdefault('port', 80)
                    port.setdefault('default', False)
                    port.setdefault('ssl', False)
                    port.setdefault('spdy', False)

                ws.setdefault('ssl_cert_path', None)
                ws.setdefault('ssl_key_path', None)
                ws.setdefault('root', '/srv')

                ws.setdefault('custom_conf', None)
                ws.setdefault('custom_conf_toplevel', None)
                ws.setdefault('maintenance_mode', False)

                ws.setdefault('locations', [])
                for location in ws['locations']:
                    location.setdefault('pattern', '/')
                    location.setdefault('match', 'exact')
                    location.setdefault('type', 'static')
                    location.setdefault('params', {})
                    location.setdefault('custom_conf', None)
                    location.setdefault('custom_conf_override', False)
                    location.setdefault('path', ws['root'])
                    location.setdefault('path_append_pattern', False)

                    if location['type'] == 'static':
                        location['params'].setdefault('autoindex', False)

                    if location['type'] == 'proxy':
                        location['params'].setdefault('url', 'http://127.0.0.1')

                    if location['type'] == 'fcgi':
                        location['params'].setdefault('url', 'http://127.0.0.1:9000')

                    if location['type'] == 'app':
                        location['params'].setdefault('app', None)

        if isinstance(config, SystemConfig):
            config.data.setdefault('log_dir', '/var/log/veb')

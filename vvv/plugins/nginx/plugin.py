import multiprocessing
from jadi import component

from vvv.api.config import SystemConfig
from vvv.api.plugin import Plugin


@component(Plugin)
class NginxPlugin(Plugin):
    name = 'nginx'

    def add_config_defaults(self, config):
        if isinstance(config, SystemConfig):
            config.data.setdefault('nginx', {})
            config.data['nginx'].setdefault('config_root', '/etc/nginx')
            config.data['nginx'].setdefault('config_file', '/etc/nginx/nginx.conf')
            config.data['nginx'].setdefault('config_file_mime', '/etc/nginx/mime.conf')
            config.data['nginx'].setdefault('config_file_fastcgi', '/etc/nginx/fcgi.conf')
            config.data['nginx'].setdefault('config_file_proxy', '/etc/nginx/proxy.conf')
            config.data['nginx'].setdefault('config_vhost_root', '/etc/nginx/conf.d')
            config.data['nginx'].setdefault('config_custom_root', '/etc/nginx.custom.d')
            config.data['nginx'].setdefault('lib_path', '/var/lib/nginx')
            config.data['nginx'].setdefault('user', 'www-data')
            config.data['nginx'].setdefault('workers', multiprocessing.cpu_count())

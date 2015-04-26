import os
from jadi import component, interface, NoImplementationError

from vvv.api.config import SystemConfig, MainConfig
from vvv.api.plugin import Plugin


@interface
class PHPFPMImpl(object):
    default_pidfile = None

    def __init__(self, context):
        pass


@component(PHPFPMImpl)
class PHPFPMDebian(PHPFPMImpl):
    default_pidfile = '/var/run/php5-fpm.pid'
    default_config_file = '/etc/php5/fpm/php-fpm.conf'
    service_name = 'php5-fpm'

    @classmethod
    def __verify__(cls):
        return os.path.exists('/etc/debian_version')


@component(PHPFPMImpl)
class PHPFPMCentOS(PHPFPMImpl):
    default_pidfile = '/var/run/php-fpm/php-fpm.pid',
    default_config_file = '/etc/php-fpm.conf'
    service_name = 'php-fpm'

    @classmethod
    def __verify__(cls):
        return os.path.exists('/etc/rhel-release')


@component(Plugin)
class PHPFPMPlugin(Plugin):
    name = 'php-fpm'

    @classmethod
    def __verify__(cls):
        return len(PHPFPMImpl.classes()) > 0

    def add_config_defaults(self, config):
        impl = PHPFPMImpl.any(self.context)

        if isinstance(config, MainConfig):
            config.data.setdefault('websites', [])

            for ws in config.data['websites']:
                for app in ws['apps']:
                    if app['type'] == 'php-fpm':
                        app['params'].setdefault('pm_min', 1)
                        app['params'].setdefault('pm_max', 5)
                        app['params'].setdefault('spare_min', 1)
                        app['params'].setdefault('spare_max', 3)
                        app['params'].setdefault('user', 'www-data')
                        app['params'].setdefault('group', 'www-data')
                        app['params'].setdefault('php_admin_values', {})
                        app['params'].setdefault('php_flags', {})
                        app['params'].setdefault('pm', 'dynamic')
                        app['params'].setdefault('custom_conf', None)

        if isinstance(config, SystemConfig):
            config.data.setdefault('php-fpm', {})
            config.data['php-fpm'].setdefault('config_file', impl.default_config_file)
            config.data['php-fpm'].setdefault('pidfile', impl.default_pidfile)

import subprocess
from jadi import component

from vvv.api.app import AppType
from vvv.api.config import SystemConfig
from vvv.api.configurable import Configurable
from vvv.api.check import Check
from vvv.api.restartable import Restartable
from vvv.api.template import Template

from .plugin import PHPFPMImpl


@component(Check)
class PHPFPMServiceCheck(Check):
    name = 'php-fpm is running'

    def run(self):
        return subprocess.call(
            ['service', PHPFPMImpl.any(self.context).service_name, 'status']
        ) == 0


@component(AppType)
class PHPFPMAppType(AppType):
    name = 'php-fpm'

    def get_access_type(self, website_config, app_config):
        return 'fcgi'

    def get_access_params(self, website_config, app_config):
        return {
            'url': 'unix:/var/run/veb-app-%s-%s.sock' % (website_config['name'], app_config['name'])
        }


@component(Configurable)
class PHPFPM(Configurable):
    name = 'php-fpm'

    def configure(self):
        open(SystemConfig.get(self.context).data['php-fpm']['config_file'], 'w').write(
            Template.by_name(self.context, 'fpm.conf').render()
        )
        PHPFPMRestartable.get(self.context).schedule_restart()


@component(Restartable)
class PHPFPMRestartable(Restartable):
    name = 'php-fpm'

    def do_restart(self):
        subprocess.check_call(['service', PHPFPMImpl.any(self.context).service_name, 'restart'])

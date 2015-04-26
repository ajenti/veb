import os
from jadi import component

import vvv
from vvv.api.app import AppType
from vvv.api.config import MainConfig
from vvv.api.configurable import Configurable
from vvv.api.template import Template
from vvv.api.util import ensure_directory


@component(Template)
class ConfigFileTemplate(Template):
    name = 'gunicorn'
    data = """
import multiprocessing

bind = 'unix:/var/run/veb-app-${website['name']}-${app['name']}.sock'
user = '${app['params']['user']}'
chdir = '${app['path']}'
workers = ${app['params']['workers']} or (multiprocessing.cpu_count() * 2 + 1)
accesslog = '${system_config['log_dir']}/${website['name']}/${app['name']}.access.log'
errorlog =  '${system_config['log_dir']}/${website['name']}/${app['name']}.error.log'

${app['params']['custom_conf'] or ''}
    """


def _get_module_name(website, app):
    module_name = '%s-%s' % (website['name'], app['name'])
    return module_name.replace('-', '_').replace(' ', '_')


def _get_config_path(website, app):
    config_dir = os.path.join(vvv.config_dir, 'gunicorn')
    ensure_directory(config_dir)
    return os.path.join(config_dir, _get_module_name(website, app) + '.py')


@component(AppType)
class PythonAppType(AppType):
    name = 'python-wsgi'

    def get_access_type(self, website_config, app_config):
        return 'proxy'

    def get_access_params(self, website_config, app_config):
        return {
            'url': 'http://unix:/var/run/veb-app-%s-%s.sock' % (website_config['name'], app_config['name'])
        }

    def get_process(self, website_config, app_config):
        p = {
            'command': 'gunicorn -c %s %s' % (
                _get_config_path(website_config, app_config),
                app_config['params']['module'],
            ),
            'user': app_config['params']['user'],
            'environment': app_config['params']['environment'],
            'directory': app_config['path'],
        }
        virtualenv = app_config['params']['virtualenv']
        if virtualenv:
            p['environment'] = 'PATH="%s:%s"' % (
                os.path.join(virtualenv, 'bin'),
                os.environ['PATH'],
            )
            p['command'] = os.path.join(virtualenv, 'bin') + '/' + p['command']
        return p


@component(Configurable)
class GUnicorn(Configurable):
    name = 'gunicorn'

    def configure(self):
        for website in MainConfig.get(self.context).data['websites']:
            for app in website['apps']:
                if app['type'] == 'python-wsgi':
                    open(_get_config_path(website, app), 'w').write(
                        Template.by_name(self.context, 'gunicorn').render(data={
                            'website': website,
                            'app': app,
                        })
                    )

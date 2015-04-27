import os
import subprocess
from jadi import component

import vvv
from vvv.api.app import AppType
from vvv.api.check import Check, CheckFailure
from vvv.api.config import MainConfig
from vvv.api.configurable import Configurable
from vvv.api.template import Template
from vvv.api.util import ensure_directory, absolute_path

'''
@component(Check)
class WSGIModuleCheck(Check):
    def get_instances(self):
        for website in MainConfig.get(self.context).data['websites']:
            if website['enabled']:
                for app in website['apps']:
                    if app['type'] == 'python-wsgi':
                        mod = app['params']['module']
                        if ':' in mod:
                            mod, var = mod.split(':')
                        else:
                            var = 'application'
                        yield [mod, var, website, app]

    def get_name(self, mod, var, website, app):
        return 'wsgi module importable in %s/%s' % (
            website['name'],
            app['name'],
        )

    def run(self, mod, var, website, app):
        try:
            subprocess.check_output([
                'python', '-c',
                'import %s as wsgi; print wsgi.%s' % (
                    mod, var
                )
            ], cwd=absolute_path(app['path'], website['root']))
            return True
        except:
            raise CheckFailure('could not import %s from module %s' % (mod, var))
'''

@component(Template)
class ConfigFileTemplate(Template):
    name = 'gunicorn'
    data = """
import multiprocessing

bind = 'unix:/var/run/veb-app-${website['name']}-${app['name']}.sock'
user = '${app['params']['user']}'
chdir = '${path}'
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

    def get_access_type(self, website, app):
        return 'proxy'

    def get_access_params(self, website, app):
        return {
            'url': 'http://unix:/var/run/veb-app-%s-%s.sock' % (website['name'], app['name'])
        }

    def get_process(self, website, app):
        p = {
            'command': 'gunicorn -c %s %s' % (
                _get_config_path(website, app),
                app['params']['module'],
            ),
            'user': app['params']['user'],
            'environment': app['params']['environment'],
            'directory': absolute_path(app['path'], website['root']),
        }
        virtualenv = app['params']['virtualenv']
        if virtualenv:
            virtualenv = absolute_path(virtualenv, absolute_path(app['path'], website['root']))
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
            if website['enabled']:
                for app in website['apps']:
                    if app['type'] == 'python-wsgi':
                        open(_get_config_path(website, app), 'w').write(
                            Template.by_name(self.context, 'gunicorn').render(data={
                                'website': website,
                                'app': app,
                                'path': absolute_path(app['path'], website['root']),
                            })
                        )

import logging
import os
import shutil
import subprocess
from jadi import component

from vvv.api.app import AppType
from vvv.api.config import MainConfig, SystemConfig
from vvv.api.configurable import Configurable
from vvv.api.check import Check, CheckFailure
from vvv.api.restartable import Restartable
from vvv.api.template import Template
from vvv.api.util import ensure_directory


@component(Check)
class NginxConfigCheck(Check):
    name = 'nginx configuration passes test'

    def run(self):
        p = subprocess.Popen(['nginx', '-t'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        o, e = p.communicate()
        if p.returncode != 0:
            raise CheckFailure(o + e)
        return True


@component(Check)
class NginxServiceCheck(Check):
    name = 'nginx is running'

    def run(self):
        return subprocess.call(['service', 'nginx', 'status']) == 0


@component(Configurable)
class NginxWebserver(Configurable):
    name = 'nginx'

    '''
    def __generate_website_location(self, ws, location):
        params = location.backend.params

        if location.backend.type == 'static':
            content = TEMPLATE_LOCATION_CONTENT_STATIC % {
                'autoindex': 'autoindex on;' if params['autoindex'] else '',
            }

        if location.backend.type == 'proxy':
            content = TEMPLATE_LOCATION_CONTENT_PROXY % {
                'url': params.get('url', 'http://127.0.0.1/'),
            }

        if location.backend.type == 'fcgi':
            content = TEMPLATE_LOCATION_CONTENT_FCGI % {
                'url': params.get('url', '127.0.0.1:9000'),
            }

        if location.backend.type == 'php-fcgi':
            content = TEMPLATE_LOCATION_CONTENT_PHP_FCGI % {
                'id': location.backend.id,
            }

        if location.backend.type == 'python-wsgi':
            content = TEMPLATE_LOCATION_CONTENT_PYTHON_WSGI % {
                'id': location.backend.id,
            }

        if location.backend.type == 'ruby-unicorn':
            content = TEMPLATE_LOCATION_CONTENT_RUBY_UNICORN % {
                'id': location.backend.id,
            }

        if location.backend.type == 'ruby-puma':
            content = TEMPLATE_LOCATION_CONTENT_RUBY_PUMA % {
                'id': location.backend.id,
            }

        if location.backend.type == 'nodejs':
            content = TEMPLATE_LOCATION_CONTENT_NODEJS % {
                'port': location.backend.params.get('port', 8000) or 8000,
            }

        if location.custom_conf_override:
            content = ''

        path_spec = ''
        if location.path:
            if location.path_append_pattern:
                path_spec = 'root %s;' % location.path
            else:
                path_spec = 'alias %s;' % location.path

        return TEMPLATE_LOCATION % {
            'pattern': location.pattern,
            'custom_conf': location.custom_conf,
            'path': path_spec,
            'match': {
                'exact': '',
                'regex': '~',
                'force-regex': '^~',
            }[location.match],
            'content': content,
        }
    '''

    def __generate_website_config(self, website):
        location_info = []
        for location in website['locations']:
            if location['type'] in ['static', 'proxy', 'fcgi']:
                location_info.append(location)
            elif location['type'] == 'app':
                for app_config in website['apps']:
                    if app_config['name'] == location['params']['app']:
                        break
                else:
                    logging.warn('Skipping unknown app "%s"', location['params']['app'])
                    continue

                app_type = AppType.by_name(self.context, app_config['type'])
                if not app_type:
                    logging.warn('Skipping unknown app type "%s"', app_config['type'])
                    continue
                new_location = location.copy()
                new_location['type'] = app_type.get_access_type(website, app_config)
                new_location['params'].update(app_type.get_access_params(website, app_config))
                location_info.append(new_location)
            else:
                logging.warn('Skipped unknown location type "%s"', location['type'])

        return Template.by_name(self.context, 'nginx.website.conf').render(data={
            'website': website,
            'location_info': location_info,
        })

    def configure(self):
        cfg = MainConfig.get(self.context)
        system = SystemConfig.get(self.context)
        shutil.rmtree(system.data['nginx']['config_root'])

        ensure_directory(
            system.data['nginx']['config_root'],
            uid=system.data['nginx']['user'],
            mode=0755
        )
        ensure_directory(
            system.data['nginx']['config_vhost_root'],
            uid=system.data['nginx']['user'],
            mode=0755
        )
        ensure_directory(
            system.data['nginx']['config_custom_root'],
            uid=system.data['nginx']['user'],
            mode=0755
        )
        ensure_directory(
            system.data['log_dir'] + '/nginx',
            uid=system.data['nginx']['user'],
            mode=0755
        )

        open(system.data['nginx']['config_file'], 'w').write(
            Template.by_name(self.context, 'nginx.conf').render()
        )
        open(system.data['nginx']['config_file_mime'], 'w').write(
            Template.by_name(self.context, 'nginx.mime.conf').render()
        )
        open(system.data['nginx']['config_file_fastcgi'], 'w').write(
            Template.by_name(self.context, 'nginx.fcgi.conf').render()
        )
        open(system.data['nginx']['config_file_proxy'], 'w').write(
            Template.by_name(self.context, 'nginx.proxy.conf').render()
        )

        for website in cfg.data['websites']:
            if website['enabled']:
                path = os.path.join(system.data['nginx']['config_vhost_root'], website['name'] + '.conf')
                with open(path, 'w') as f:
                    f.write(self.__generate_website_config(website))

        subprocess.call([
            'chown', 'www-data:www-data', '-R', system.data['nginx']['lib_path'],
        ])

        NginxRestartable.get(self.context).schedule_restart()


@component(Restartable)
class NginxRestartable(Restartable):
    name = 'nginx'

    def do_restart(self):
        subprocess.check_call(['service', 'nginx', 'restart'])

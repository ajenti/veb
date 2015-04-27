from jadi import component

from vvv.api.template import Template

@component(Template)
class ConfigFileTemplate(Template):
    name = 'fpm.conf'
    data = """
[global]
pid = ${system_config['php-fpm']['pidfile']}
error_log = ${system_config['log_dir']}/php-fpm.log

[global-pool]
user = ${system_config['nginx']['user']}
group = ${system_config['nginx']['user']}

listen = /var/run/php-fpm.sock
listen.owner = ${system_config['nginx']['user']}
listen.group = ${system_config['nginx']['user']}
listen.mode = 0660

pm = dynamic
pm.start_servers = 1
pm.max_children = 5
pm.min_spare_servers = 1
pm.max_spare_servers = 5

% for website in enabled_websites:
    % for app in website['apps']:
        % if app['type'] == 'php-fpm':

[veb-app-${website['name']}-${app['name']}]
user = ${app['params']['user']}
group = ${app['params']['group']}

listen = /var/run/veb-app-${website['name']}-${app['name']}.sock
listen.owner = ${system_config['nginx']['user']}
listen.group = ${system_config['nginx']['user']}
listen.mode = 0660

pm = ${app['params']['pm']}
pm.start_servers = ${app['params']['pm_min']}
pm.max_children = ${app['params']['pm_max']}
pm.min_spare_servers = ${app['params']['spare_min']}
pm.max_spare_servers = ${app['params']['spare_max']}

% for k in app['params']['php_admin_values']:
php_admin_value[${k}] = ${app['params']['php_admin_values'][k]}
% endfor

% for k in app['params']['php_flags']:
php_flag[${k}] = ${app['params']['php_flags'][k]}
% endfor

${app['params']['custom_conf'] or ''}

        % endif
    % endfor
% endfor
    """

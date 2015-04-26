import os
import yaml
from jadi import service

import vvv
from vvv.api.plugin import Plugin


class ConfigFile(object):
    subpath = None

    def __init__(self, context):
        self.context = context
        self.path = os.path.join(vvv.config_dir, self.subpath)
        self.load()

    def load(self):
        if os.path.exists(self.path):
            self.data = yaml.load(open(self.path))
        else:
            self.data = {}

        for plugin in Plugin.all(self.context):
            plugin.add_config_defaults(self)

    def save(self):
        with open(self.path, 'w') as f:
            f.write(yaml.safe_dump(
                self.data,
                default_flow_style=False,
                encoding='utf-8',
                allow_unicode=True
            ))


@service
class MainConfig(ConfigFile):
    subpath = 'config.yml'


@service
class SystemConfig(ConfigFile):
    subpath = 'system.yml'

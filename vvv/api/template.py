from jadi import interface
from mako.template import Template as MakoTemplate

from .config import MainConfig, SystemConfig


@interface
class Template(object):
    name = None
    data = None

    @classmethod
    def by_name(cls, context, name):
        for template in cls.classes():
            if template.name == name:
                return template(context)

    def __init__(self, context):
        self.context = context
        self.template = MakoTemplate(self.data)

    def render(self, data={}):
        data.update({
            'main_config': MainConfig.get(self.context).data,
            'enabled_websites': [
                x for x in
                MainConfig.get(self.context).data['websites']
                if x['enabled']
            ],
            'system_config': SystemConfig.get(self.context).data,
        })
        return self.template.render(**data).replace('\n\n', '\n')

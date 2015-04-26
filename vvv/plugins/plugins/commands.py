from jadi import component

from vvv.api.command import Command
from vvv.api.plugin import Plugin


@component(Command)
class PluginsCommand(Command):
    name = 'plugins'
    usage = '''
plugins - lists available plugins
'''

    def run(self):
        plugins = sorted(Plugin.classes(), key=lambda x: x.name)
        for plugin in plugins:
            print plugin.name

from jadi import component

from vvv.api.plugin import Plugin


@component(Plugin)
class PluginsPlugin(Plugin):
    name = 'plugins'

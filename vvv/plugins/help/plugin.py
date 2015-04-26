from jadi import component

from vvv.api.plugin import Plugin


@component(Plugin)
class HelpPlugin(Plugin):
    name = 'help'
    
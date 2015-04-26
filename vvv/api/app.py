from jadi import interface


@interface
class AppType(object):
    name = None

    @classmethod
    def by_name(cls, context, name):
        for app in cls.classes():
            if app.name == name:
                return app(context)

    def __init__(self, context):
        self.context = context

    def get_access_type(self, website_config, app_config):
        raise NotImplementedError

    def get_access_params(self, website_config, app_config):
        raise NotImplementedError

    def get_process(self, website_config, app_config):
        return None
        
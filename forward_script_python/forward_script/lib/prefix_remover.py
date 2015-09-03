from werkzeug.wsgi import pop_path_info


class PrefixRemover(object):
    """
    Remove path prefix on tool labs, where every app is behind a proxy that
    adds the tool name as a path prefix, breaking the routes.
    """

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        pop_path_info(environ)
        return self.app(environ, start_response)
"""
This module defines a DjangoApp, a Connexion application to wrap a Django application.
"""
from connexion.apps.abstract import AbstractApp


class DjangoApp(AbstractApp):
    def create_app(self):
        """
        Creates the user framework application
        """

    def get_root_path(self):
        """
        Gets the root path of the user framework application
        """

    def set_errors_handlers(self):
        """
        Sets all errors handlers of the user framework application
        """

    def run(self, port=None, server=None, debug=None, host=None, **options):  # pragma: no cover
        """
        Runs the application on a local development server.
        :param host: the host interface to bind on.
        :type host: str
        :param port: port to listen to
        :type port: int
        :param server: which wsgi server to use
        :type server: str | None
        :param debug: include debugging information
        :type debug: bool
        :param options: options to be forwarded to the underlying server
        """

from abc import ABC
from server.config import Config


class Server(ABC):
    """
    Base Service
    """

    def __init__(self, config: Config, **kwargs):
        self._conf = config
        self._server_conf = self._conf.server

    def run(self, *args, **kwargs):
        raise NotImplementedError

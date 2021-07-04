from abc import ABC, abstractmethod


class Plugin(ABC):
    enabled = False

    @abstractmethod
    def __init__(self, url):
        pass

    def apply_on_feed(self, feed):
        pass

    def apply_on_item(self, item):
        pass

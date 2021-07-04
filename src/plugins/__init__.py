import importlib
import os
from abc import ABC, abstractmethod
from glob import glob


class Plugin(ABC):
    enabled = False

    @abstractmethod
    def __init__(self, url):
        pass

    def apply_on_feed(self, feed):
        pass

    def apply_on_item(self, item):
        pass


plugins = []

path = os.path.dirname(os.path.realpath(__file__))
for plugin_path in glob(path + os.path.sep + "*.py"):
    if plugin_path == __file__:
        continue
    plugin_path = plugin_path.replace(path, "")
    if plugin_path[0] == os.path.sep:
        plugin_path = plugin_path[1:]
    plugin_spec = plugin_path.replace(os.path.sep, ".").replace(".py", "")
    plugin_spec = "plugins." + plugin_spec
    plugin = importlib.import_module(plugin_spec)
    if "PLUGIN_CLASS" not in dir(plugin):
        raise Exception("Plugin missing constant PLUGIN_CLASS")
    plugins.append(plugin.PLUGIN_CLASS)

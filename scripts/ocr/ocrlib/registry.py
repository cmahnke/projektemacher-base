import importlib
import importlib.util
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class Registry:
    def __init__(self, kind):
        self.kind = kind
        self._items = {}

    def register(self, item):
        if item.name in self._items:
            raise ValueError(f"{self.kind} '{item.name}' is already registered")
        self._items[item.name] = item
        return item

    def get(self, name):
        if name not in self._items:
            raise KeyError(f"unknown {self.kind} '{name}', available: {', '.join(sorted(self._items))}")
        return self._items[name]

    def names(self):
        return sorted(self._items)

    def load_plugin(self, plugin):
        if plugin.endswith(".py"):
            spec = importlib.util.spec_from_file_location(Path(plugin).stem, plugin)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        else:
            importlib.import_module(plugin)
        logger.debug(f"Loaded {self.kind} plugin '{plugin}'")


def register_item(registry: Registry, item):
    return registry.register(item)

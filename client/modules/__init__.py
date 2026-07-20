import pkgutil
import importlib
import inspect

from .base import BaseModule

def get_all_modules():
    modules = []
    for loader, name, is_pkg in pkgutil.iter_modules(__path__):
        if name == "base":
            continue

        module = importlib.import_module(f".{name}", package=__name__)

        for _, cls in inspect.getmembers(module, inspect.isclass):
            if issubclass(cls, BaseModule) and cls is not BaseModule:
                modules.append(cls)

    return modules
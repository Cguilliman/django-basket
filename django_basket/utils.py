from typing import Callable, Any, Optional
from django.utils.module_loading import import_string


__all__ = ("load_module", "settings_function")


def load_module(
    path: str, 
    default: Any = None,
    check: Callable[[Any], bool] = None
) -> Optional[Any]:
    """Load custom or default module"""
    if path:
        module = import_string(path)
        is_valid = (check(module) if check else bool(module))
        if is_valid:
            return module
    return default


def settings_function(func_path):
    # TODO: Make collection of executable
    def wrapper(func):
        def wrapped(*args, **kwargs):
            _func = func
            if func_path:
                _func = load_module(
                    func_path,
                    default=func,
                    check=lambda module: callable(module),
                )
            return _func(*args, **kwargs)
        return wrapped
    return wrapper

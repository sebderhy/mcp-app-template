"""Auto-discovers widget modules and builds registries."""

from __future__ import annotations

import importlib
import pkgutil
from typing import Any, Callable, Coroutine, Dict, List

from ._base import Widget

WIDGETS: List[Widget] = []
WIDGETS_BY_ID: Dict[str, Widget] = {}
WIDGET_HANDLERS: Dict[str, Callable[..., Coroutine[Any, Any, Any]]] = {}
WIDGET_INPUT_MODELS: Dict[str, type] = {}
DATA_ONLY_HANDLERS: Dict[str, Callable[..., Coroutine[Any, Any, Any]]] = {}

for _, _name, _ in pkgutil.iter_modules(__path__):
    if _name.startswith("_"):
        continue
    _mod = importlib.import_module(f".{_name}", __package__)
    if hasattr(_mod, "WIDGET"):
        _w = _mod.WIDGET
        WIDGETS.append(_w)
        WIDGETS_BY_ID[_w.identifier] = _w
        WIDGET_HANDLERS[_w.identifier] = _mod.handle
        if hasattr(_mod, "INPUT_MODEL"):
            WIDGET_INPUT_MODELS[_w.identifier] = _mod.INPUT_MODEL
    if hasattr(_mod, "DATA_ONLY_TOOLS"):
        DATA_ONLY_HANDLERS.update(_mod.DATA_ONLY_TOOLS)

WIDGETS_BY_URI: Dict[str, Widget] = {w.template_uri: w for w in WIDGETS}

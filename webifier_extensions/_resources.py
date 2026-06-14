from __future__ import annotations

import importlib.util
import os


def package_path(package: str, *parts: str) -> str:
    spec = importlib.util.find_spec(package)
    if not spec or not spec.submodule_search_locations:
        raise ValueError(f"Cannot locate package resources for {package!r}.")
    return os.path.join(next(iter(spec.submodule_search_locations)), *parts)

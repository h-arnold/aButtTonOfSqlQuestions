from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

_implementation_path = Path(__file__).resolve().parent / "notebooks" / "sql_notebook_setup.py"
_spec = spec_from_file_location("notebooks.sql_notebook_setup", _implementation_path)

if _spec is None or _spec.loader is None:
    raise ImportError(f"Unable to load notebook setup helper from {_implementation_path}")

_module = module_from_spec(_spec)
_spec.loader.exec_module(_module)

setup_sql_notebook = _module.setup_sql_notebook
setup_uber_sql_notebook = _module.setup_uber_sql_notebook

__all__ = ["setup_sql_notebook", "setup_uber_sql_notebook"]
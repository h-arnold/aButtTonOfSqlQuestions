from __future__ import annotations

from importlib import import_module
from pathlib import Path
from shutil import copy2

DEFAULT_DATABASE_PATH = Path("/workspaces/aButtTonOfSqlQuestions/datasets/sqlite/uber_rideshare.db")
KAGGLE_DATASET_NAME = "rockyt07/uber-sql-database"
KAGGLE_DATABASE_FILE = "rideshare.db"


def _ensure_sql_magic(database_path: Path, *, verify: bool) -> Path:
    ipython = import_module("IPython").get_ipython()
    if ipython is None:
        raise RuntimeError("setup_uber_sql_notebook must be run inside a Jupyter/IPython kernel.")

    if "sql" in ipython.extension_manager.loaded:
        ipython.run_line_magic("reload_ext", "sql")
    else:
        ipython.run_line_magic("load_ext", "sql")

    ipython.run_line_magic("config", "SqlMagic.style = '_DEPRECATED_DEFAULT'")
    ipython.run_line_magic("sql", f"sqlite:////{database_path.as_posix().lstrip('/')}")

    if verify:
        ipython.run_line_magic("sql", "SELECT COUNT(*) AS table_count FROM sqlite_master WHERE type='table';")

    return database_path


def _download_uber_database(database_path: Path) -> Path:
    try:
        kagglehub = import_module("kagglehub")
    except ImportError as error:
        raise ImportError("kagglehub is required to download the Uber dataset.") from error

    source_database = Path(kagglehub.dataset_download(KAGGLE_DATASET_NAME)) / KAGGLE_DATABASE_FILE
    database_path.parent.mkdir(parents=True, exist_ok=True)
    copy2(source_database, database_path)
    return database_path


def setup_sql_notebook(
    database_path: str | Path = DEFAULT_DATABASE_PATH,
    *,
    verify: bool = True,
) -> Path:
    database_path = Path(database_path).expanduser().resolve()

    if not database_path.exists():
        _download_uber_database(database_path)

    if not database_path.exists():
        raise FileNotFoundError(f"SQLite database not found: {database_path}")

    _ensure_sql_magic(database_path, verify=verify)
    print("✓ Setup complete! Database ready.")
    return database_path


def setup_uber_sql_notebook(
    database_path: str | Path = DEFAULT_DATABASE_PATH,
    *,
    verify: bool = True,
) -> Path:
    return setup_sql_notebook(database_path=database_path, verify=verify)
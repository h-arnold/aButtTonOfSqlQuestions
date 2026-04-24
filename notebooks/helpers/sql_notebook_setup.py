"""Helpers for SQL notebook setup.

This module exists so notebook cells can stay small and focused on the
exercise content. It hides the repetitive notebook startup work behind one
generic entry point:

* locate or create the SQLite database file
* optionally download the Uber dataset when the file is missing
* load the `ipython-sql` extension inside the active IPython kernel
* connect the notebook session to the SQLite database
* optionally run a quick verification query so the notebook fails early if
  the database is not usable

The public API is intentionally small:

* `setup_sql_notebook(...)` for reusable notebook setup
* `setup_uber_sql_notebook(...)` as a dataset-specific convenience wrapper

Keeping the generic helper separate from the Uber wrapper makes it easy to
reuse this setup pattern in other projects that use a different SQLite file or
different download strategy.
"""

from __future__ import annotations

from importlib import import_module
from pathlib import Path
from shutil import copy2

DEFAULT_DATABASE_PATH = Path("/workspaces/aButtTonOfSqlQuestions/datasets/sqlite/uber_rideshare.db")
KAGGLE_DATASET_NAME = "rockyt07/uber-sql-database"
KAGGLE_DATABASE_FILE = "rideshare.db"
IMDB_DEFAULT_DATABASE_PATH = Path("/workspaces/aButtTonOfSqlQuestions/datasets/sqlite/imdb_movies.db")
IMDB_KAGGLE_DATASET_NAME = "poojapragatika/sql-based-imdb-data-for-analysis-projects"
IMDB_KAGGLE_DATABASE_FILE = "movies.sqlite"
SOCIAL_MEDIA_ADS_DEFAULT_DATABASE_PATH = Path(
    "/workspaces/aButtTonOfSqlQuestions/datasets/sqlite/social_media_advertisement_performance.db"
)
SOCIAL_MEDIA_ADS_KAGGLE_DATASET_NAME = "alperenmyung/social-media-advertisement-performance"
SOCIAL_MEDIA_ADS_KAGGLE_DATABASE_FILE = "ad_campaign_db.sqlite"


def _ensure_sql_magic(database_path: Path, *, verify: bool) -> Path:
    """Load or refresh ipython-sql and connect the current kernel to SQLite.

    The notebook cells depend on `%%sql` magic working before any exercise cell
    runs. This function performs the notebook-side wiring in a single place so
    the setup cell does not need to duplicate the same magic commands.
    """

    # Import IPython lazily so this module stays lightweight when inspected by
    # editors or imported outside a live notebook session.
    ipython = import_module("IPython").get_ipython()
    if ipython is None:
        raise RuntimeError("setup_sql_notebook must be run inside a Jupyter/IPython kernel.")

    # Reload the extension if it is already present so repeated notebook runs
    # stay consistent; otherwise load it for the first time.
    if "sql" in ipython.extension_manager.loaded:
        ipython.run_line_magic("reload_ext", "sql")
    else:
        ipython.run_line_magic("load_ext", "sql")

    # Match the formatting used by the existing notebooks so query output stays
    # familiar and compact.
    ipython.run_line_magic("config", "SqlMagic.style = '_DEPRECATED_DEFAULT'")

    # Point ipython-sql at the selected SQLite file.
    ipython.run_line_magic("sql", f"sqlite:////{database_path.as_posix().lstrip('/')}")

    # A tiny smoke test gives a fast failure if the file exists but is not a
    # valid SQLite database or the connection string is wrong.
    if verify:
        ipython.run_line_magic("sql", "SELECT COUNT(*) AS table_count FROM sqlite_master WHERE type='table';")

    return database_path


def _download_uber_database(database_path: Path) -> Path:
    """Download the Uber dataset and copy the SQLite database into place.

    The shared helper intentionally does not know about Kaggle or the Uber
    dataset. This private helper keeps that concern separate so other projects
    can reuse `setup_sql_notebook` without inheriting Uber-specific download
    logic.
    """

    try:
        kagglehub = import_module("kagglehub")
    except ImportError as error:
        raise ImportError("kagglehub is required to download the Uber dataset.") from error

    source_database = Path(kagglehub.dataset_download(KAGGLE_DATASET_NAME)) / KAGGLE_DATABASE_FILE
    database_path.parent.mkdir(parents=True, exist_ok=True)
    copy2(source_database, database_path)
    return database_path


def _download_imdb_database(database_path: Path) -> Path:
    """Download the IMDb dataset and copy the SQLite database into place."""

    try:
        kagglehub = import_module("kagglehub")
    except ImportError as error:
        raise ImportError("kagglehub is required to download the IMDb dataset.") from error

    source_database = Path(kagglehub.dataset_download(IMDB_KAGGLE_DATASET_NAME)) / IMDB_KAGGLE_DATABASE_FILE
    database_path.parent.mkdir(parents=True, exist_ok=True)
    copy2(source_database, database_path)
    return database_path


def _download_social_media_ads_database(database_path: Path) -> Path:
    """Download the social-media ads dataset and copy the SQLite database into place."""

    try:
        kagglehub = import_module("kagglehub")
    except ImportError as error:
        raise ImportError("kagglehub is required to download the social-media ads dataset.") from error

    source_database = (
        Path(kagglehub.dataset_download(SOCIAL_MEDIA_ADS_KAGGLE_DATASET_NAME))
        / SOCIAL_MEDIA_ADS_KAGGLE_DATABASE_FILE
    )
    database_path.parent.mkdir(parents=True, exist_ok=True)
    copy2(source_database, database_path)
    return database_path


def setup_sql_notebook(
    database_path: str | Path = DEFAULT_DATABASE_PATH,
    *,
    verify: bool = True,
) -> Path:
    """Prepare a notebook session for running SQL against a SQLite database.

    Parameters
    ----------
    database_path:
        Path to the SQLite database file that should back the notebook session.
        If the file is missing, the Uber-specific wrapper downloads it before
        this function is called.
    verify:
        When True, run a lightweight query against `sqlite_master` after the
        connection is created. This confirms that the database is reachable and
        that the SQL magic wiring succeeded.

    Returns
    -------
    pathlib.Path
        The resolved path to the database that was connected.
    """

    database_path = Path(database_path).expanduser().resolve()

    # The generic setup helper is responsible for connecting, not for knowing
    # where the database comes from. If the file is missing, try the Uber
    # download path before failing.
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
    """Convenience wrapper for the Uber rideshare notebooks.

    This keeps the notebook cell readable while preserving a reusable generic
    setup helper for other projects.
    """

    return setup_sql_notebook(database_path=database_path, verify=verify)


def setup_imdb_sql_notebook(
    database_path: str | Path = IMDB_DEFAULT_DATABASE_PATH,
    *,
    verify: bool = True,
) -> Path:
    """Convenience wrapper for the IMDb SQL notebooks."""

    database_path = Path(database_path).expanduser().resolve()
    if not database_path.exists():
        _download_imdb_database(database_path)

    return setup_sql_notebook(database_path=database_path, verify=verify)


def setup_social_media_ads_sql_notebook(
    database_path: str | Path = SOCIAL_MEDIA_ADS_DEFAULT_DATABASE_PATH,
    *,
    verify: bool = True,
) -> Path:
    """Convenience wrapper for social-media advertisement SQL notebooks."""

    database_path = Path(database_path).expanduser().resolve()
    if not database_path.exists():
        _download_social_media_ads_database(database_path)

    return setup_sql_notebook(database_path=database_path, verify=verify)
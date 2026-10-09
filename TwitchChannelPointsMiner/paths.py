"""Every file the miner writes lives under a single data folder (mount this one in Docker).

    <data>/cookies/<username>.pkl          login session
    <data>/database/<username>_drops.db    claimed drops database
    <data>/logs/<username>.log             log files
    <data>/analytics/<username>/*.json     analytics series

The folder is ``TCPM_DATA_DIR`` or ``./data`` when unset (``/data`` in the Docker image).
"""

import os
from pathlib import Path


def data_dir() -> Path:
    configured = os.environ.get("TCPM_DATA_DIR", "").strip()
    return Path(configured).absolute() if configured else Path().absolute() / "data"


def subdir(*names: str) -> Path:
    path = data_dir().joinpath(*names)
    path.mkdir(parents=True, exist_ok=True)
    return path

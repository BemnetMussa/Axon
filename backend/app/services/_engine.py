"""Load the curation and AI engine, or the community stubs when it is absent.

Search order:
  1. ``AXON_ENGINE_DIR`` — explicit override
  2. ``backend/engine/`` — the copy that ships in the Docker image. Render's
     build context is ``backend/``, so the gitignored ``private/services/``
     tree never reaches production. This directory does.
  3. ``/etc/secrets/`` — Render Secret Files, used when present
  4. ``<repo>/private/services/`` — local overlay, used when the shipped copy
     is not there

Inside the image the app lives at ``/app/app/services/``, so a path counted
from the repo root points at ``/`` and would miss the files. The shipped copy
is resolved from the backend root instead (``/app/engine`` in the container).
"""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path
from types import ModuleType

_BACKEND_ROOT = Path(__file__).resolve().parents[2]
_REPO_ROOT = _BACKEND_ROOT.parent


def _engine_dirs() -> list[Path]:
    dirs = []
    if os.getenv("AXON_ENGINE_DIR"):
        dirs.append(Path(os.environ["AXON_ENGINE_DIR"]))
    dirs += [
        _BACKEND_ROOT / "engine",
        Path("/etc/secrets"),
        _REPO_ROOT / "private" / "services",
    ]
    return dirs


def load_engine(name: str, community_module: str) -> ModuleType:
    """Return the private module named ``name``, or the community stub."""
    for directory in _engine_dirs():
        private_path = directory / f"{name}.py"
        if not private_path.is_file():
            continue
        mod_name = f"axon_private_{name}"
        spec = importlib.util.spec_from_file_location(mod_name, private_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load private engine at {private_path}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[mod_name] = module
        spec.loader.exec_module(module)
        print(f"AXON ENGINE: {name} loaded from {private_path}")
        return module

    print(f"AXON ENGINE: {name} NOT FOUND — running the community stub (no ingest / no AI)")
    return importlib.import_module(community_module)

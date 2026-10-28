"""Load proprietary engine modules from the local private overlay when present.

Layout (repo root):
  private/services/fetcher.py   # gitignored — full curation engine
  private/services/analyzer.py  # gitignored — AI analysis / prompts

In production the same two files are uploaded as Render Secret Files, which
appear at /etc/secrets/. ``AXON_ENGINE_DIR`` overrides both locations.

If those files are missing (public OSS clone), fall back to the community stubs.
"""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path
from types import ModuleType

_REPO_ROOT = Path(__file__).resolve().parents[3]


def _engine_dirs() -> list[Path]:
    dirs = []
    if os.getenv("AXON_ENGINE_DIR"):
        dirs.append(Path(os.environ["AXON_ENGINE_DIR"]))
    dirs += [_REPO_ROOT / "private" / "services", Path("/etc/secrets")]
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

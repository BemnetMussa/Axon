"""Load proprietary engine modules from the local private overlay when present.

Layout (repo root):
  private/services/fetcher.py   # gitignored — full curation engine
  private/services/analyzer.py  # gitignored — AI analysis / prompts

If those files are missing (public OSS clone), fall back to the community stubs.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

_REPO_ROOT = Path(__file__).resolve().parents[3]
_PRIVATE_DIR = _REPO_ROOT / "private" / "services"


def load_engine(name: str, community_module: str) -> ModuleType:
    """Return the private module named ``name``, or the community stub."""
    private_path = _PRIVATE_DIR / f"{name}.py"
    if private_path.is_file():
        mod_name = f"axon_private_{name}"
        spec = importlib.util.spec_from_file_location(mod_name, private_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load private engine at {private_path}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[mod_name] = module
        spec.loader.exec_module(module)
        return module

    return importlib.import_module(community_module)

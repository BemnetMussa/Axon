# Local engine override (gitignored)

Optional. Drop `services/fetcher.py` or `services/analyzer.py` here to run a
local variant of the engine instead of the copy in `backend/engine/`.

Load order is set in `backend/app/services/_engine.py`: `AXON_ENGINE_DIR`,
then `backend/engine/`, then `/etc/secrets/`, then this folder.

Do not commit secrets here.

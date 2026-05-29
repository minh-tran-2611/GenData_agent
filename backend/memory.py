import json
import os
import threading
from pathlib import Path
from datetime import datetime, timezone

from models import Memory, RunLogEntry

DATA_DIR = Path(__file__).parent / "data"
MEMORY_FILE = DATA_DIR / "memory.json"
_LOCK = threading.Lock()


def _ensure_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_memory() -> Memory:
    _ensure_dir()
    if not MEMORY_FILE.exists():
        mem = Memory()
        save_memory(mem)
        return mem
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            raw = json.load(f)
        return Memory(**raw)
    except Exception:
        # If file corrupted, back it up and start fresh
        backup = MEMORY_FILE.with_suffix(".corrupt.json")
        try:
            os.replace(MEMORY_FILE, backup)
        except Exception:
            pass
        mem = Memory()
        save_memory(mem)
        return mem


def save_memory(memory: Memory) -> None:
    _ensure_dir()
    with _LOCK:
        tmp = MEMORY_FILE.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(memory.model_dump(), f, ensure_ascii=False, indent=2)
        os.replace(tmp, MEMORY_FILE)


def append_log(memory: Memory, entry: RunLogEntry, max_logs: int = 5000) -> None:
    memory.logs.append(entry)
    if len(memory.logs) > max_logs:
        memory.logs = memory.logs[-max_logs:]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def reset_simulation(memory: Memory) -> Memory:
    """Reset simulation state but keep business + endpoints + settings."""
    from models import SimulationState
    memory.simulation = SimulationState()
    memory.logs = []
    memory.changes_from_last_run = []
    # Also clear the SQL sink counters/pool so a fresh run restarts IDs from the
    # base and never reuses user IDs from a previous (possibly deleted) run.
    memory.sql_sink = {}
    return memory

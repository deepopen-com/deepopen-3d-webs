from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXAMPLES_DIR = ROOT / "examples"
DATA_DIR = ROOT / "data"
HISTORY_FILE = DATA_DIR / "history.json"
SEED_FILE = DATA_DIR / "seed_tasks.json"
OUTPUTS_DIR = ROOT / "outputs"
RESULTS_DIR = ROOT / "results"


def ensure_dirs():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

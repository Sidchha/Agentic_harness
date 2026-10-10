from pathlib import Path
from config import MEMORY_FILE

MEMORY_FILE = Path(__file__).parent / MEMORY_FILE

def load_memory():
    if not MEMORY_FILE.exists():
        return ""

    return MEMORY_FILE.read_text(encoding="utf-8")

def load_memory_lines():
    if not MEMORY_FILE.exists():
        return []
    return MEMORY_FILE.read_text(encoding="utf-8").splitlines()

def save_memory(information: str):
    information = information.strip()
    if not information:
        return {"success":  False, "message": "No information provided to save."}
    MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)

    with MEMORY_FILE.open("w", encoding="utf-8") as f:
        f.write(f"{information}\n")

    return {"success": True, "message": "Information saved successfully."}
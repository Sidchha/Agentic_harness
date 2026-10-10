from pathlib import Path

WORKSPACE = Path(__file__).parent / "workspace"
WORKSPACE.mkdir(parents=True, exist_ok=True)


def list_files():
    return [
        str(path.relative_to(WORKSPACE))
        for path in WORKSPACE.rglob("*")
        if path.is_file()
    ]


def read_file(filename: str):
    path = WORKSPACE / filename

    if not path.exists():
        return {"error": f"File not found: {filename}"}

    return {
        "filename": filename,
        "content": path.read_text(encoding="utf-8"),
    }


def write_file(filename: str, content: str):
    path = WORKSPACE / filename

    path.parent.mkdir(parents=True, exist_ok=True)

    path.write_text(content, encoding="utf-8")

    return {
        "filename": filename,
        "message": f"Successfully wrote {filename}",
    }

def delete_file(filename: str):
    path = WORKSPACE / filename

    if not path.exists():
        return {"error": f"File not found: {filename}"}

    if not path.is_file():
        return {"error": f"Not a file: {filename}"}

    path.unlink()

    return {
        "filename": filename,
        "message": f"Successfully deleted {filename}",
    }
import json
from pathlib import Path

MANIFEST_PATH = Path(".agent-stack/manifest.json")


class OwnershipConflict(Exception):
    pass


class Ownership:
    """Tracks which project paths agent-stack wrote, so re-runs only replace its own files."""

    def __init__(self, project: Path):
        self._project = project
        manifest = project / MANIFEST_PATH
        previous = json.loads(manifest.read_text())["paths"] if manifest.exists() else []
        self._previously_owned = set(previous)
        self._claimed: set[str] = set()

    def claim(self, path: Path) -> None:
        relative = path.relative_to(self._project).as_posix()
        if (path.exists() or path.is_symlink()) and relative not in self._previously_owned:
            raise OwnershipConflict(
                f"{relative} already exists and was not created by agent-stack; "
                "move or remove it, then re-run init"
            )
        self._claimed.add(relative)

    def adopt(self, path: Path) -> None:
        self._claimed.add(path.relative_to(self._project).as_posix())

    def save(self, version: str) -> None:
        manifest = self._project / MANIFEST_PATH
        manifest.parent.mkdir(parents=True, exist_ok=True)
        content = {"version": version, "paths": sorted(self._claimed)}
        manifest.write_text(json.dumps(content, indent=2) + "\n")

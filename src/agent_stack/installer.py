import json
import os
import shutil
from pathlib import Path

from agent_stack.claude_md import ensure_agents_import
from agent_stack.hook_settings import merge_hooks, to_project_hooks
from agent_stack.managed_block import upsert_managed_block
from agent_stack.ownership import Ownership
from agent_stack.skill_metadata import CODEX_MANUAL_ONLY_POLICY, is_manual_only, read_frontmatter

STACK_ROOT = Path(__file__).resolve().parents[2]


def stack_version(stack: Path = STACK_ROOT) -> str:
    return json.loads((stack / ".claude-plugin/plugin.json").read_text())["version"]


def install(project: Path, stack: Path = STACK_ROOT) -> None:
    ownership = Ownership(project)
    install_instructions(project, stack)
    install_skills(project, stack, ownership)
    install_agents(project, stack, ownership)
    install_hooks(project, stack, ownership)
    ownership.save(stack_version(stack))


def install_instructions(project: Path, stack: Path) -> None:
    body = (stack / "instructions/AGENTS.md").read_text()
    _rewrite(project / "AGENTS.md", lambda text: upsert_managed_block(text, body))
    _rewrite(project / "CLAUDE.md", ensure_agents_import)


def install_skills(project: Path, stack: Path, ownership: Ownership) -> None:
    for source in sorted(p for p in (stack / "skills").iterdir() if p.is_dir()):
        vendored = project / ".agents/skills" / source.name
        _copy_tree(source, vendored, ownership)
        if is_manual_only(read_frontmatter((source / "SKILL.md").read_text())):
            sidecar = vendored / "agents/openai.yaml"
            sidecar.parent.mkdir(parents=True, exist_ok=True)
            sidecar.write_text(CODEX_MANUAL_ONLY_POLICY)
        _link(project / ".claude/skills" / source.name, vendored, ownership)


def install_agents(project: Path, stack: Path, ownership: Ownership) -> None:
    for source in sorted((stack / "agents").glob("*.md")):
        destination = project / ".claude/agents" / source.name
        ownership.claim(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def install_hooks(project: Path, stack: Path, ownership: Ownership) -> None:
    _copy_tree(stack / "hooks/scripts", project / ".agent-stack/hooks", ownership)
    plugin_hooks = json.loads((stack / "hooks/hooks.json").read_text())["hooks"]
    settings_path = project / ".claude/settings.json"
    settings = json.loads(settings_path.read_text()) if settings_path.exists() else {}
    merged = merge_hooks(settings, to_project_hooks(plugin_hooks))
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(json.dumps(merged, indent=2) + "\n")


def _rewrite(path: Path, transform) -> None:
    existing = path.read_text() if path.exists() else ""
    path.write_text(transform(existing))


def _copy_tree(source: Path, destination: Path, ownership: Ownership) -> None:
    ownership.claim(destination)
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(source, destination)


def _link(link: Path, target: Path, ownership: Ownership) -> None:
    relative_target = Path(os.path.relpath(target, link.parent))
    if link.is_symlink() and Path(os.readlink(link)) == relative_target:
        ownership.adopt(link)
        return
    ownership.claim(link)
    link.parent.mkdir(parents=True, exist_ok=True)
    if link.is_symlink():
        link.unlink()
    link.symlink_to(relative_target, target_is_directory=True)

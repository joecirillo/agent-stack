import json
import os

import pytest

from agent_stack.installer import install
from agent_stack.ownership import OwnershipConflict


def test_codex_and_claude_read_the_same_vendored_skill(tmp_path):
    install(tmp_path)

    vendored = tmp_path / ".agents/skills/new-branch/SKILL.md"
    claude_link = tmp_path / ".claude/skills/new-branch"
    assert vendored.is_file()
    assert claude_link.is_symlink()
    assert os.readlink(claude_link) == "../../.agents/skills/new-branch"
    assert (claude_link / "SKILL.md").read_text() == vendored.read_text()


def test_manual_only_skills_get_codex_invocation_policy(tmp_path):
    install(tmp_path)

    assert (tmp_path / ".agents/skills/prove-it/agents/openai.yaml").is_file()
    assert not (tmp_path / ".agents/skills/new-branch/agents/openai.yaml").exists()


def test_claude_md_imports_agents_md_with_stack_instructions(tmp_path):
    install(tmp_path)

    assert (tmp_path / "CLAUDE.md").read_text().startswith("@AGENTS.md")
    assert "## Code Design" in (tmp_path / "AGENTS.md").read_text()


def test_hooks_point_at_vendored_scripts_that_exist(tmp_path):
    install(tmp_path)

    settings = json.loads((tmp_path / ".claude/settings.json").read_text())
    commands = [
        hook["command"]
        for groups in settings["hooks"].values()
        for group in groups
        for hook in group["hooks"]
    ]
    for command in commands:
        script = command.split("/.agent-stack/hooks/")[1]
        assert (tmp_path / ".agent-stack/hooks" / script).is_file()


def test_rerun_is_idempotent(tmp_path):
    install(tmp_path)
    snapshot = {p: p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}

    install(tmp_path)

    assert {p: p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()} == snapshot


def test_refuses_to_overwrite_a_skill_the_project_already_owns(tmp_path):
    existing = tmp_path / ".agents/skills/new-branch"
    existing.mkdir(parents=True)
    (existing / "SKILL.md").write_text("project's own skill")

    with pytest.raises(OwnershipConflict):
        install(tmp_path)
    assert (existing / "SKILL.md").read_text() == "project's own skill"

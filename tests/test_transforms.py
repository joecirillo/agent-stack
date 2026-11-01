import pytest

from agent_stack.claude_md import ensure_agents_import
from agent_stack.hook_settings import merge_hooks, to_project_hooks
from agent_stack.managed_block import BEGIN_MARKER, END_MARKER, upsert_managed_block
from agent_stack.skill_metadata import is_manual_only, read_frontmatter


class TestUpsertManagedBlock:
    def test_appends_block_after_existing_project_content(self):
        result = upsert_managed_block("# Project rules\n", "stack rules")
        assert result == f"# Project rules\n\n{BEGIN_MARKER}\nstack rules\n{END_MARKER}\n"

    def test_replaces_only_the_block_and_keeps_surrounding_content(self):
        original = upsert_managed_block("before\n", "old")
        updated = upsert_managed_block(original + "after\n", "new")
        assert "old" not in updated
        assert updated.startswith("before\n")
        assert updated.endswith(f"{END_MARKER}\nafter\n")

    def test_is_idempotent(self):
        once = upsert_managed_block("", "rules")
        assert upsert_managed_block(once, "rules") == once

    def test_rejects_unterminated_block(self):
        with pytest.raises(ValueError):
            upsert_managed_block(f"{BEGIN_MARKER}\nrules\n", "rules")


class TestEnsureAgentsImport:
    def test_creates_import_for_empty_file(self):
        assert ensure_agents_import("") == "@AGENTS.md\n"

    def test_prepends_import_and_keeps_claude_specific_content(self):
        assert ensure_agents_import("Use pnpm.\n") == "@AGENTS.md\n\nUse pnpm.\n"

    def test_leaves_file_alone_when_import_present(self):
        text = "Notes\n@AGENTS.md\n"
        assert ensure_agents_import(text) == text


class TestSkillMetadata:
    def test_detects_manual_only_skill(self):
        skill = "---\nname: prove-it\ndisable-model-invocation: true\n---\nbody"
        assert is_manual_only(read_frontmatter(skill))

    def test_description_containing_colons_is_kept_whole(self):
        skill = "---\ndescription: Use when: things happen\n---\n"
        assert read_frontmatter(skill)["description"] == "Use when: things happen"

    def test_missing_frontmatter_means_model_invocable(self):
        assert not is_manual_only(read_frontmatter("# Just a body"))

    def test_rejects_unclosed_frontmatter(self):
        with pytest.raises(ValueError):
            read_frontmatter("---\nname: x\n")


PLUGIN_HOOKS = {
    "Stop": [
        {"hooks": [{"type": "command", "command": '"${CLAUDE_PLUGIN_ROOT}"/hooks/scripts/gate.sh'}]}
    ]
}


class TestHookSettings:
    def test_rewrites_plugin_paths_to_vendored_project_paths(self):
        command = to_project_hooks(PLUGIN_HOOKS)["Stop"][0]["hooks"][0]["command"]
        assert command == '"${CLAUDE_PROJECT_DIR}"/.agent-stack/hooks/gate.sh'

    def test_merge_preserves_project_hooks_and_other_settings(self):
        project_group = {"hooks": [{"type": "command", "command": "make lint"}]}
        settings = {"model": "opus", "hooks": {"Stop": [project_group]}}
        merged = merge_hooks(settings, to_project_hooks(PLUGIN_HOOKS))
        assert merged["model"] == "opus"
        assert merged["hooks"]["Stop"][0] == project_group
        assert len(merged["hooks"]["Stop"]) == 2

    def test_merge_is_idempotent(self):
        hooks = to_project_hooks(PLUGIN_HOOKS)
        once = merge_hooks({}, hooks)
        assert merge_hooks(once, hooks) == once

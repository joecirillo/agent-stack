PLUGIN_SCRIPTS_DIR = '"${CLAUDE_PLUGIN_ROOT}"/hooks/scripts'
PROJECT_SCRIPTS_DIR = '"${CLAUDE_PROJECT_DIR}"/.agent-stack/hooks'


def to_project_hooks(plugin_hooks: dict) -> dict:
    return {
        event: [_rewrite_group(group) for group in groups]
        for event, groups in plugin_hooks.items()
    }


def merge_hooks(settings: dict, hooks: dict) -> dict:
    merged = dict(settings)
    merged_hooks = {event: list(groups) for event, groups in settings.get("hooks", {}).items()}
    for event, groups in hooks.items():
        existing = merged_hooks.setdefault(event, [])
        existing.extend(group for group in groups if group not in existing)
    merged["hooks"] = merged_hooks
    return merged


def _rewrite_group(group: dict) -> dict:
    return {
        **group,
        "hooks": [
            {**hook, "command": hook["command"].replace(PLUGIN_SCRIPTS_DIR, PROJECT_SCRIPTS_DIR)}
            for hook in group["hooks"]
        ],
    }

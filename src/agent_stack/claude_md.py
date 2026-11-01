AGENTS_IMPORT = "@AGENTS.md"


def ensure_agents_import(existing: str) -> str:
    if any(line.strip() == AGENTS_IMPORT for line in existing.splitlines()):
        return existing
    if not existing:
        return f"{AGENTS_IMPORT}\n"
    return f"{AGENTS_IMPORT}\n\n{existing}"

CODEX_MANUAL_ONLY_POLICY = "policy:\n  allow_implicit_invocation: false\n"


def read_frontmatter(skill_md: str) -> dict[str, str]:
    lines = skill_md.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    fields: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return fields
        key, sep, value = line.partition(":")
        if sep:
            fields[key.strip()] = value.strip()
    raise ValueError("SKILL.md frontmatter is missing its closing '---'")


def is_manual_only(frontmatter: dict[str, str]) -> bool:
    return frontmatter.get("disable-model-invocation", "").lower() == "true"

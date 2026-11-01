BEGIN_MARKER = "<!-- agent-stack:begin (managed by agent-stack init; edits here are overwritten) -->"
END_MARKER = "<!-- agent-stack:end -->"


def upsert_managed_block(existing: str, body: str) -> str:
    block = f"{BEGIN_MARKER}\n{body.strip()}\n{END_MARKER}\n"
    start = existing.find(BEGIN_MARKER)
    if start == -1:
        separator = "\n" if existing and not existing.endswith("\n") else ""
        gap = "\n" if existing else ""
        return f"{existing}{separator}{gap}{block}"

    end = existing.find(END_MARKER, start)
    if end == -1:
        raise ValueError("Found agent-stack begin marker without a matching end marker")
    after = existing[end + len(END_MARKER):].removeprefix("\n")
    return f"{existing[:start]}{block}{after}"

#!/usr/bin/env python3
"""PreToolUse guard for `git commit` Bash calls.

Denies the commit outright when a staged file is itself secret-shaped (a
.env file, a private key, etc.) or when the staged diff adds secret-shaped
content -- these need a human to unstage/fix them, not a silent rewrite.
Separately, redacts secret-shaped strings found in the command itself
(covers the common mistake of pasting a real key into a -m message), and
rejects commit messages that violate the 50/72 convention so the agent can
rewrite them.
"""
import json
import re
import subprocess
import sys

SECRET_PATTERNS = [
    r"AKIA[0-9A-Z]{16}",                    # AWS access key ID
    r"ASIA[0-9A-Z]{16}",                    # AWS STS session key ID
    r"sk-ant-[A-Za-z0-9\-_]{20,}",          # Anthropic API key
    r"sk-[A-Za-z0-9]{20,}",                 # OpenAI-style API key
    r"gh[pousr]_[A-Za-z0-9]{36,}",          # GitHub token
    r"xox[baprs]-[A-Za-z0-9-]{10,}",        # Slack token
    r"AIza[0-9A-Za-z\-_]{35}",              # Google API key
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----",
    r"(?i)(api[_-]?key|secret|token|password|passwd)\s*[=:]\s*['\"][^'\"]{8,}['\"]",
]

ENV_FILENAME_PATTERNS = [
    r"(^|/)\.env$",
    r"(^|/)\.env\.(?!example$|sample$|template$)[^/]+$",
    r"(^|/)id_rsa$",
    r"(^|/)id_ed25519$",
    r"(^|/)[^/]*_rsa$",
    r"(^|/)[^/]*\.pem$",
    r"(^|/)credentials\.json$",
    r"(^|/)service-account.*\.json$",
]

SUMMARY_MAX = 50
BODY_MAX = 72


def redact(command: str) -> tuple[str, int]:
    redacted = command
    count = 0
    for pattern in SECRET_PATTERNS:
        redacted, n = re.subn(pattern, "***REDACTED***", redacted)
        count += n
    return redacted, count


def message_violations(command: str) -> list[str]:
    violations = []
    for raw in re.findall(r"-m\s+(\"(?:[^\"\\]|\\.)*\"|'(?:[^'\\]|\\.)*')", command):
        msg = raw[1:-1]
        lines = msg.split("\\n") if "\\n" in msg else msg.split("\n")
        if not lines:
            continue
        summary = lines[0]
        if len(summary) > SUMMARY_MAX:
            violations.append(f"summary line is {len(summary)} chars (max {SUMMARY_MAX}): {summary!r}")
        for line in lines[1:]:
            if len(line) > BODY_MAX:
                violations.append(f"body line is {len(line)} chars (max {BODY_MAX}): {line!r}")
    return violations


def _run_git(cwd: str, args: list[str]) -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=5,
            check=True,
        )
        return result.stdout
    except Exception:
        return ""


def staged_files(cwd: str) -> list[str]:
    out = _run_git(cwd, ["diff", "--cached", "--name-only"])
    return [line for line in out.splitlines() if line]


def flagged_filenames(files: list[str]) -> list[str]:
    flagged = []
    for f in files:
        if any(re.search(pattern, f) for pattern in ENV_FILENAME_PATTERNS):
            flagged.append(f)
    return flagged


def staged_diff_secrets(cwd: str) -> dict[str, set[str]]:
    diff = _run_git(cwd, ["diff", "--cached", "-U0"])
    findings: dict[str, set[str]] = {}
    current_file = "?"
    for line in diff.splitlines():
        if line.startswith("+++ "):
            path = line[4:]
            current_file = path[2:] if path.startswith(("a/", "b/")) else path
            continue
        if not line.startswith("+") or line.startswith("+++"):
            continue
        added = line[1:]
        for pattern in SECRET_PATTERNS:
            if re.search(pattern, added):
                findings.setdefault(current_file, set()).add(pattern)
    return findings


def main() -> None:
    data = json.load(sys.stdin)
    command = data.get("tool_input", {}).get("command", "")
    cwd = data.get("cwd", ".")

    files = staged_files(cwd)
    bad_filenames = flagged_filenames(files)
    diff_secrets = staged_diff_secrets(cwd)

    if bad_filenames or diff_secrets:
        reasons = []
        if bad_filenames:
            reasons.append(
                "Staged file(s) look like secrets/credentials, not source: "
                + ", ".join(bad_filenames)
            )
        if diff_secrets:
            reasons.append(
                "Staged changes add secret-shaped content in: "
                + ", ".join(sorted(diff_secrets))
            )
        reason = (
            "Refusing to commit -- unstage these first if they shouldn't be "
            "committed:\n- " + "\n- ".join(reasons)
        )
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": reason,
            }
        }))
        return

    redacted, secret_count = redact(command)

    if secret_count:
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "allow",
                "permissionDecisionReason": (
                    f"Redacted {secret_count} secret-shaped pattern(s) from the commit "
                    "command before execution."
                ),
                "updatedInput": {"command": redacted},
            }
        }))
        return

    violations = message_violations(command)
    if violations:
        reason = "Commit message violates the 50/72 convention:\n- " + "\n- ".join(violations)
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": reason,
            }
        }))
        return

    sys.exit(0)


if __name__ == "__main__":
    main()

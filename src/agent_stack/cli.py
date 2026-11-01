import argparse
import sys
from pathlib import Path

from agent_stack.installer import install, stack_version
from agent_stack.ownership import OwnershipConflict


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="agent-stack")
    commands = parser.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init", help="Vendor the agent stack into a project")
    init.add_argument("project", nargs="?", default=".", type=Path)
    args = parser.parse_args(argv)

    project = args.project.resolve()
    if not project.is_dir():
        print(f"agent-stack: {project} is not a directory", file=sys.stderr)
        return 1
    try:
        install(project)
    except OwnershipConflict as conflict:
        print(f"agent-stack: {conflict}", file=sys.stderr)
        return 1
    print(f"agent-stack {stack_version()} installed into {project}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

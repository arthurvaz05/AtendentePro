from __future__ import annotations

import sys

from AtendentePro.run_env import run as runner


def main() -> None:
    """Launch the AtendentePro CLI respecting any debug arguments."""
    original_argv = sys.argv[:]
    program = original_argv[0] if original_argv else "debug_flow"
    agent_args = original_argv[1:]
    try:
        sys.argv = [program, *agent_args]
        runner.main()
    finally:
        sys.argv = original_argv


if __name__ == "__main__":
    main()

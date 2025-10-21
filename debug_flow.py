from __future__ import annotations

import sys

from AtendentePro.run_env import run as runner


def main() -> None:
    """Launch the flow agent directly for debugging sessions."""
    sys.argv = []
    runner.main()


if __name__ == "__main__":
    main()

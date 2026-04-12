"""mse-ai CLI entry point."""

from __future__ import annotations

import json
import sys

from .baseline_demo import run_demo_baseline


def main(argv: list[str] | None = None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])
    if not args or args[0] in {"-h", "--help", "help"}:
        print("mse-ai — deterministic ML consumer for mse-cli substrate")
        print("commands:")
        print("  baseline    Fit the logistic baseline over the demo training matrix")
        return 0
    if args[0] == "baseline":
        payload = run_demo_baseline()
        print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))
        return 0
    print(f"unknown command: {args[0]}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

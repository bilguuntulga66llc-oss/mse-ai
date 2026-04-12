"""mse-ai CLI entry point."""

from __future__ import annotations

import json
import sys

from .baseline_demo import run_demo_baseline
from .signal_demo import run_demo_signal_backtest


def main(argv: list[str] | None = None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])
    if not args or args[0] in {"-h", "--help", "help"}:
        print("mse-ai — deterministic ML + alpha research consumer for mse-cli substrate")
        print("commands:")
        print("  baseline          Fit the logistic baseline over the demo training matrix")
        print("  signal [SYMBOL]   Run the demo signal backtest (default APU)")
        return 0
    if args[0] == "baseline":
        payload = run_demo_baseline()
        print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))
        return 0
    if args[0] == "signal":
        symbol = args[1] if len(args) > 1 else "APU"
        payload = run_demo_signal_backtest(symbol=symbol)
        print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))
        return 0
    print(f"unknown command: {args[0]}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

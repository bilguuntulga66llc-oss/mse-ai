"""mse-ai CLI entry point — real data only, no demos."""

from __future__ import annotations

import json
import sys

from .baseline import run_baseline_fit
from .signal import run_signal_backtest


def main(argv: list[str] | None = None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])
    if not args or args[0] in {"-h", "--help", "help"}:
        print("mse-ai — ML + alpha research consumer for mse-cli substrate")
        print()
        print("commands:")
        print("  baseline SYMBOL   Fit logistic baseline over real trade data")
        print("  signal SYMBOL     Run signal backtest over real trade data")
        print()
        print("examples:")
        print("  mse-ai baseline APU")
        print("  mse-ai signal GOBI --limit 60")
        return 0
    if args[0] == "baseline" and len(args) >= 2:
        symbol = args[1]
        payload = run_baseline_fit(symbol=symbol)
        print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))
        return 0
    if args[0] == "signal" and len(args) >= 2:
        symbol = args[1]
        limit = 120
        if "--limit" in args:
            idx = args.index("--limit")
            if idx + 1 < len(args):
                limit = int(args[idx + 1])
        payload = run_signal_backtest(symbol=symbol, limit=limit)
        print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))
        return 0
    print(f"unknown command or missing symbol: {' '.join(args)}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

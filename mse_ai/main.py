"""mse-ai CLI entry point — real data only, no demos."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from .baseline import run_baseline_fit
from .signal import run_signal_backtest
from .strategy import compare_strategies, render_comparison, run_strategy_backtest


def _positive_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be an integer") from exc
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be >= 1")
    return parsed


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mse-ai",
        description="ML + alpha research consumer for mse-cli substrate",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    baseline = subparsers.add_parser("baseline", help="Fit logistic baseline over real trade data")
    baseline.add_argument("symbol")
    baseline.add_argument("--limit", type=_positive_int, default=120)
    baseline.add_argument(
        "--model-kind",
        choices=("logistic_binary", "decision_stump_binary", "ranking_linear"),
        default="logistic_binary",
    )

    signal = subparsers.add_parser("signal", help="Run signal backtest over real trade data")
    signal.add_argument("symbol")
    signal.add_argument("--limit", type=_positive_int, default=120)
    signal.add_argument("--window", type=_positive_int, default=20)
    signal.add_argument("--threshold", type=float, default=2.0)
    signal.add_argument("--detector-period", type=_positive_int, default=20)
    signal.add_argument("--std-floor", type=float, default=0.0)
    signal.add_argument("--adaptive-threshold", action="store_true")
    signal.add_argument("--range-threshold", type=float, default=1.0)

    strategy = subparsers.add_parser("strategy", help="Run a single strategy baseline")
    strategy.add_argument("symbol")
    strategy.add_argument("--name", default="buy_and_hold")
    strategy.add_argument("--limit", type=_positive_int, default=120)
    strategy.add_argument("--period", default="1Y")
    strategy.add_argument("--short-window", type=_positive_int, default=10)
    strategy.add_argument("--long-window", type=_positive_int, default=30)
    strategy.add_argument("--bollinger-window", type=_positive_int, default=20)
    strategy.add_argument("--bollinger-num-std", type=float, default=2.0)

    compare = subparsers.add_parser("compare", help="Rank all baselines by final P&L")
    compare.add_argument("symbol")
    compare.add_argument("--limit", type=_positive_int, default=120)
    compare.add_argument("--period", default="1Y")
    compare.add_argument("--json", action="store_true")
    return parser


def _dump(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))


def main(argv: list[str] | None = None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])
    if not args or args[0] == "help":
        _parser().print_help()
        return 0

    try:
        parsed = _parser().parse_args(args)
    except SystemExit as exc:
        return int(exc.code or 0)

    try:
        if parsed.command == "baseline":
            _dump(run_baseline_fit(symbol=parsed.symbol, model_kind=parsed.model_kind, limit=parsed.limit))
            return 0
        if parsed.command == "signal":
            _dump(
                run_signal_backtest(
                    symbol=parsed.symbol,
                    limit=parsed.limit,
                    window=parsed.window,
                    threshold=parsed.threshold,
                    period=parsed.detector_period,
                    std_floor=parsed.std_floor,
                    adaptive_threshold=parsed.adaptive_threshold,
                    range_threshold=parsed.range_threshold,
                )
            )
            return 0
        if parsed.command == "strategy":
            _dump(
                run_strategy_backtest(
                    symbol=parsed.symbol,
                    strategy=parsed.name,
                    limit=parsed.limit,
                    period=parsed.period,
                    short_window=parsed.short_window,
                    long_window=parsed.long_window,
                    bollinger_window=parsed.bollinger_window,
                    bollinger_num_std=parsed.bollinger_num_std,
                )
            )
            return 0
        if parsed.command == "compare":
            payload = compare_strategies(symbol=parsed.symbol, limit=parsed.limit, period=parsed.period)
            if parsed.json:
                _dump(payload)
            else:
                print(render_comparison(payload))
            return 0
    except Exception as exc:  # noqa: BLE001 - CLI should not expose traceback by default.
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

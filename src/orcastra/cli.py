"""Small standard-library CLI for the safe initial scaffold."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from orcastra.service import run_mock_analysis


def _date_time(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise argparse.ArgumentTypeError("expected an ISO-8601 date-time") from exc
    if parsed.tzinfo is None:
        raise argparse.ArgumentTypeError("date-time must include a timezone")
    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="orcastra")
    subparsers = parser.add_subparsers(dest="command", required=True)
    run_mock = subparsers.add_parser(
        "run-mock", help="run one deterministic paper-only ticker analysis"
    )
    run_mock.add_argument("--ticker", required=True, help="US ticker, for example AAPL")
    run_mock.add_argument("--output", type=Path, default=Path("artifacts"))
    run_mock.add_argument("--decision-at", type=_date_time)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.command == "run-mock":
        trace, path = run_mock_analysis(
            ticker=args.ticker,
            output=args.output,
            decision_timestamp=args.decision_at,
        )
        print(f"run_id={trace.run_id}")
        print(f"decision={trace.proposed_decision.action.value}")
        print(f"risk_approved={str(trace.risk_guard.approved).lower()}")
        print(f"execution={trace.execution.status.value}")
        print(f"trace={path.resolve()}")


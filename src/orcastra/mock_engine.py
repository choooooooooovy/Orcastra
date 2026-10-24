"""Offline deterministic stand-in for the future TradingAgents adapter."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timedelta

from orcastra.contracts import (
    AgentStep,
    DebateRecord,
    DebateTurn,
    DecisionAction,
    ProposedDecision,
    SourceReference,
    StepStatus,
    ToolCall,
    Usage,
)


@dataclass(frozen=True)
class AnalysisBundle:
    sources: list[SourceReference]
    steps: list[AgentStep]
    debate: DebateRecord
    decision: ProposedDecision


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


class MockTradingAgentsEngine:
    """Produces a realistic trace shape without network, credentials, or LLMs."""

    name = "mock-tradingagents"
    version = "0.1"
    model_id = "deterministic-mock-v1"

    def analyze(self, ticker: str, decision_timestamp: datetime) -> AnalysisBundle:
        ticker = ticker.strip().upper()
        base = decision_timestamp - timedelta(seconds=2)
        price_id = f"mock-price-{ticker.lower()}"
        filing_id = f"mock-filing-{ticker.lower()}"
        news_id = f"mock-news-{ticker.lower()}"
        sources = [
            SourceReference(
                source_id=price_id,
                provider="mock-market-data",
                uri=f"mock://market/{ticker}/daily",
                title=f"{ticker} synthetic daily snapshot",
                retrieved_at=base,
                data_as_of=decision_timestamp - timedelta(minutes=5),
                content_sha256=_sha256(f"{ticker}:close=189.00:rsi=54.2"),
            ),
            SourceReference(
                source_id=filing_id,
                provider="mock-sec-edgar",
                uri=f"mock://filings/{ticker}/latest",
                title=f"{ticker} synthetic filing summary",
                retrieved_at=base + timedelta(milliseconds=50),
                data_as_of=decision_timestamp - timedelta(hours=2),
                content_sha256=_sha256(f"{ticker}:revenue_growth=8.0:cash_positive=true"),
            ),
            SourceReference(
                source_id=news_id,
                provider="mock-news",
                uri=f"mock://news/{ticker}/latest",
                title=f"{ticker} synthetic news summary",
                retrieved_at=base + timedelta(milliseconds=100),
                data_as_of=decision_timestamp - timedelta(minutes=30),
                content_sha256=_sha256(f"{ticker}:news=mixed-no-material-event"),
            ),
        ]

        reports = [
            ("market_analyst", [price_id], "Price trend is constructive; RSI is neutral."),
            (
                "fundamentals_analyst",
                [filing_id],
                "Growth is positive and cash generation is sound.",
            ),
            ("news_analyst", [news_id], "Recent synthetic headlines are mixed and non-material."),
            ("sentiment_analyst", [news_id], "Sentiment is neutral to mildly bullish."),
        ]
        steps: list[AgentStep] = []
        for sequence, (role, source_ids, report) in enumerate(reports):
            started = base + timedelta(milliseconds=sequence * 100)
            tool = ToolCall(
                tool_call_id=f"tool-{sequence}",
                tool_name="mock_lookup",
                started_at=started,
                completed_at=started + timedelta(milliseconds=20),
                status=StepStatus.SUCCEEDED,
                sanitized_input={"ticker": ticker, "source_ids": source_ids},
                sanitized_output={"records": len(source_ids)},
            )
            steps.append(
                AgentStep(
                    step_id=f"step-{sequence}",
                    sequence=sequence,
                    role=role,
                    started_at=started,
                    completed_at=started + timedelta(milliseconds=40),
                    status=StepStatus.SUCCEEDED,
                    model_id=self.model_id,
                    input={"ticker": ticker, "decision_timestamp": decision_timestamp.isoformat()},
                    output={"report": report},
                    source_ids=source_ids,
                    tool_calls=[tool],
                    usage=Usage(),
                )
            )

        debate = DebateRecord(
            turns=[
                DebateTurn(
                    speaker="bull_researcher",
                    stance="bull",
                    argument=(
                        "Constructive trend and positive cash generation support a small position."
                    ),
                    source_ids=[price_id, filing_id],
                ),
                DebateTurn(
                    speaker="bear_researcher",
                    stance="bear",
                    argument=(
                        "Mixed news and limited mock evidence argue against aggressive sizing."
                    ),
                    source_ids=[news_id],
                ),
                DebateTurn(
                    speaker="research_manager",
                    stance="manager",
                    argument=(
                        "The bullish case wins narrowly; cap the target weight at five percent."
                    ),
                    source_ids=[price_id, filing_id, news_id],
                ),
            ],
            synthesis="Open only a small paper position and retain room for contrary evidence.",
        )
        decision = ProposedDecision(
            ticker=ticker,
            action=DecisionAction.BUY,
            target_weight=0.05,
            confidence=0.62,
            rationale=(
                "Positive trend and fundamentals outweigh mixed news, with conservative sizing."
            ),
            evidence_source_ids=[price_id, filing_id, news_id],
        )
        return AnalysisBundle(sources=sources, steps=steps, debate=debate, decision=decision)

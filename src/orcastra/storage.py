"""Immutable local artifact persistence with trading/evaluation separation."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from pydantic import BaseModel

from orcastra.contracts import EvaluationResult, TradingRunTrace


class ArtifactAlreadyExistsError(FileExistsError):
    pass


class JsonArtifactStore:
    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.trace_dir = self.root / "traces"
        self.evaluation_dir = self.root / "evaluations"

    def save_trace(self, trace: TradingRunTrace) -> Path:
        return self._save_immutable(self.trace_dir, str(trace.run_id), trace)

    def save_evaluation(self, result: EvaluationResult) -> Path:
        return self._save_immutable(self.evaluation_dir, str(result.eval_run_id), result)

    def _save_immutable(self, directory: Path, identifier: str, value: BaseModel) -> Path:
        directory.mkdir(parents=True, exist_ok=True)
        destination = directory / f"{identifier}.json"
        if destination.exists():
            raise ArtifactAlreadyExistsError(f"artifact already exists: {destination}")
        payload = json.dumps(value.model_dump(mode="json"), indent=2, sort_keys=True) + "\n"
        fd, temporary_name = tempfile.mkstemp(prefix=f".{identifier}.", dir=directory)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            os.link(temporary_name, destination)
        except FileExistsError as exc:
            raise ArtifactAlreadyExistsError(f"artifact already exists: {destination}") from exc
        finally:
            Path(temporary_name).unlink(missing_ok=True)
        return destination


"""Skill data model used by the EvoTest replication pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json


TEST_PATTERNS = [
    "STATE_TEST",
    "INTERACTION_TEST",
    "MOCK_TEST",
    "STUB_TEST",
    "PARAMETRIC_TEST",
    "EXCEPTION_TEST",
    "PERFORMANCE_TEST",
    "CONCURRENCY_TEST",
]

SKILL_TYPES = [
    "bug-detection",
    "regression-prevention",
    "edge-case",
]


@dataclass
class SkillSource:
    dataset: str
    bug_id: str
    focal_method_idx: int


@dataclass
class FocalMethod:
    class_name: str
    method: str
    signature: str


@dataclass
class Skill:
    """In-memory representation of a SkillBank entry."""

    id: str
    name: str
    description: str
    guidance: str
    code_tags: list[str]
    test_pattern: str
    focal_class: str
    focal_method: str
    focal_method_sig: str
    confidence: float
    source: SkillSource

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "guidance": self.guidance,
            "code_tags": self.code_tags,
            "test_pattern": self.test_pattern,
            "focal_class": self.focal_class,
            "focal_method": self.focal_method,
            "focal_method_sig": self.focal_method_sig,
            "confidence": self.confidence,
            "source": {
                "dataset": self.source.dataset,
                "bug_id": self.source.bug_id,
                "focal_method_idx": self.source.focal_method_idx,
            },
        }

    @classmethod
    def from_dict(cls, d: dict) -> Skill:
        src = d.get("source", {})
        if not isinstance(src, dict):
            src = {}
        fm = d.get("focal_method", {})
        if isinstance(fm, dict):
            focal_class = fm.get("class", "")
            focal_method = fm.get("method", "")
            focal_method_sig = fm.get("signature", "")
        else:
            focal_class = d.get("focal_class", "")
            focal_method = str(fm) if fm else d.get("focal_method", "")
            focal_method_sig = d.get("focal_method_sig", "")
        return cls(
            id=d.get("id", ""),
            name=d["name"],
            description=d["description"],
            guidance=d.get("guidance", d.get("test_strategy", "")),
            code_tags=d.get("code_tags", d.get("code_function_tags", [])),
            test_pattern=d.get("test_pattern", "PARAMETRIC_TEST"),
            focal_class=d.get("focal_class", focal_class),
            focal_method=d.get("focal_method", focal_method),
            focal_method_sig=d.get("focal_method_sig", focal_method_sig),
            confidence=d.get("confidence", 0.8),
            source=SkillSource(
                dataset=src.get("dataset", ""),
                bug_id=src.get("bug_id", ""),
                focal_method_idx=src.get("focal_method_idx", 0),
            ),
        )

    def to_json(self, path: Path) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def from_json(cls, path: Path) -> Skill:
        with open(path, encoding="utf-8") as f:
            return cls.from_dict(json.load(f))

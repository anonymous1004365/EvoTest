"""Shared code-tag registry used by initial SkillBank construction."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import json
import threading


@dataclass
class CodeTag:
    name: str
    description: str
    examples: list[str]
    created_by: str
    source_bug_id: str | None = None


class CodeTagRegistry:
    """Process-local registry of canonical code tags."""

    _instance: CodeTagRegistry | None = None

    def __init__(self):
        self._tags: dict[str, CodeTag] = {}
        self._name_to_key: dict[str, str] = {}
        self._lock = threading.RLock()
        self._init_builtin_tags()

    @classmethod
    def get_instance(cls) -> CodeTagRegistry:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        cls._instance = None

    def _init_builtin_tags(self) -> None:
        builtins = [
            CodeTag(
                name="NULL_CHECK",
                description="Missing or incorrect null handling before dereference.",
                examples=["x.do() when x may be null", "return x.field without null check"],
                created_by="builtin",
            ),
            CodeTag(
                name="BOUNDARY_CHECK",
                description="Missing or incorrect index, size, or range boundary check.",
                examples=["arr[i] without i < arr.length", "list.get(i) without i >= 0"],
                created_by="builtin",
            ),
            CodeTag(
                name="VALIDATION",
                description="Missing or incorrect validation of user input or parameters.",
                examples=["use raw user input", "missing parameter validation"],
                created_by="builtin",
            ),
            CodeTag(
                name="EXCEPTION_HANDLING",
                description="Incorrect exception handling, recovery, or propagation.",
                examples=["catch without handling", "swallowing a parsing error"],
                created_by="builtin",
            ),
            CodeTag(
                name="STATE_MUTATION",
                description="Incorrect mutation or preservation of object state.",
                examples=["modifying shared state", "inconsistent internal state"],
                created_by="builtin",
            ),
            CodeTag(
                name="CONCURRENCY",
                description="Thread-safety, race-condition, or ordering issue.",
                examples=["unsynchronized shared write", "race condition on counter"],
                created_by="builtin",
            ),
            CodeTag(
                name="RESOURCE_MANAGEMENT",
                description="Incorrect management of files, streams, connections, or other resources.",
                examples=["stream not closed", "connection leak"],
                created_by="builtin",
            ),
            CodeTag(
                name="TYPE_CONVERSION",
                description="Incorrect cast, conversion, boxing, unboxing, or generic type handling.",
                examples=["ClassCastException", "Integer vs int boxing"],
                created_by="builtin",
            ),
            CodeTag(
                name="OVERFLOW",
                description="Arithmetic overflow, underflow, or numeric precision issue.",
                examples=["max int + 1", "sum overflow"],
                created_by="builtin",
            ),
            CodeTag(
                name="ORDER_DEPENDENCY",
                description="Behavior depends on call order, initialization order, or hidden ordering assumptions.",
                examples=["method call order matters", "undocumented dependency"],
                created_by="builtin",
            ),
        ]
        for tag in builtins:
            self._tags[tag.name] = tag
            self._name_to_key[tag.name.upper()] = tag.name

    def all_tags(self) -> list[CodeTag]:
        with self._lock:
            return list(self._tags.values())

    def get(self, name: str) -> CodeTag | None:
        with self._lock:
            return self._tags.get(name)

    def find_similar(self, name: str, threshold: float = 0.7) -> list[tuple[CodeTag, float]]:
        import difflib

        name_upper = name.upper()
        candidates = []
        with self._lock:
            for tag_name in self._tags:
                ratio = difflib.SequenceMatcher(None, name_upper, tag_name.upper()).ratio()
                if ratio >= threshold:
                    candidates.append((self._tags[tag_name], ratio))
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates

    def match_existing(self, tag_name: str) -> CodeTag | None:
        with self._lock:
            if tag_name in self._tags:
                return self._tags[tag_name]
            key = tag_name.upper()
            if key in self._name_to_key:
                return self._tags[self._name_to_key[key]]
            return None

    def register(
        self,
        name: str,
        description: str,
        examples: list[str],
        created_by: str,
        source_bug_id: str | None = None,
    ) -> CodeTag:
        with self._lock:
            canonical = self._canonical_name(name)
            if canonical in self._tags:
                return self._tags[canonical]
            tag = CodeTag(
                name=canonical,
                description=description,
                examples=examples,
                created_by=created_by,
                source_bug_id=source_bug_id,
            )
            self._tags[canonical] = tag
            self._name_to_key[canonical.upper()] = canonical
            return tag

    def _canonical_name(self, name: str) -> str:
        import re

        cleaned = re.sub(r"[\s_-]+", "_", name.strip())
        cleaned = "".join(c for c in cleaned if c.isalnum() or c == "_")
        return cleaned.upper()

    def to_dict(self) -> dict:
        with self._lock:
            return {name: asdict(tag) for name, tag in self._tags.items()}

    @classmethod
    def from_dict(cls, data: dict) -> CodeTagRegistry:
        instance = cls()
        instance._tags.clear()
        instance._name_to_key.clear()
        for name, tag_dict in data.items():
            tag = CodeTag(**tag_dict)
            instance._tags[name] = tag
            instance._name_to_key[name.upper()] = name
        return instance

    def save(self, path: Path) -> None:
        data = self.to_dict()
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @classmethod
    def load(cls, path: Path) -> CodeTagRegistry:
        if not path.exists():
            return cls.get_instance()
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)

    def list_for_prompt(self) -> str:
        lines = []
        for tag in sorted(self.all_tags(), key=lambda t: t.name):
            examples = "; ".join(tag.examples[:2]) if tag.examples else "none"
            lines.append(f"- {tag.name}: {tag.description} (e.g. {examples})")
        return "\n".join(lines)

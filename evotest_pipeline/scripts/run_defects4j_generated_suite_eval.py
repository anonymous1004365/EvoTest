#!/usr/bin/env python3
"""Multi-method Defects4J generated-suite evaluation runner.

Asks an LLM to generate a complete JUnit4 test class containing many ``@Test``
methods, packages the generated class as a Defects4J ``-s`` suite archive, and
evaluates the same suite on fixed and buggy versions.

Optional Skill Bank support (--skill-bank <path>): when enabled, later same-run
attempts can access deterministic skill checklists via list_skills() and
read_skill() tools. Skills are matched by code static analysis plus a strict
tier-metadata gate for non-PASS_BOTH retries, not by loose body-text keywords.
Early attempts can remain no-skill via --skill-start-attempt.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import run_defects4j_eval as d4j  # noqa: E402


DEFAULT_WORKSPACE = Path(
    os.environ.get(
        "D4J_SUITE_WORKSPACE",
        str(d4j.TMP_DIR / "d4j-generated-suite-eval"),
    )
)
DEFAULT_OUTPUT = Path(
    os.environ.get(
        "D4J_SUITE_OUTPUT",
        str(d4j.DATA_DIR / "output" / "d4j_generated_suite_eval"),
    )
)
DEFAULT_MAX_SOURCE_CHARS = int(os.environ.get("D4J_SUITE_MAX_SOURCE_CHARS", "22000"))
DEFAULT_MAX_REPAIR_ROUNDS = int(os.environ.get("D4J_SUITE_REPAIR_ROUNDS", "2"))
DEFAULT_GENERATION_REPAIR_ROUNDS = int(os.environ.get("D4J_SUITE_GENERATION_REPAIR_ROUNDS", "2"))
DEFAULT_MAX_ATTEMPTS = int(os.environ.get("D4J_SUITE_MAX_ATTEMPTS", "1"))
DEFAULT_SKILL_START_ATTEMPT = int(os.environ.get("D4J_SUITE_SKILL_START_ATTEMPT", "4"))
DEFAULT_TEST_METHODS = int(os.environ.get("D4J_SUITE_TEST_METHODS", "10"))
DEFAULT_TEST_TIMEOUT = int(os.environ.get("D4J_SUITE_TEST_TIMEOUT", "500"))
DEFAULT_LLM_TIMEOUT = int(os.environ.get("D4J_SUITE_LLM_TIMEOUT", "180"))
DEFAULT_LLM_MAX_RETRIES = int(os.environ.get("D4J_SUITE_LLM_MAX_RETRIES", "6"))
DEFAULT_TOOL_STEPS = int(os.environ.get("D4J_SUITE_TOOL_STEPS", "8"))
DEFAULT_CONTEXT_COMPACT_EVERY = int(os.environ.get("D4J_SUITE_CONTEXT_COMPACT_EVERY", "100"))
TOOL_OBSERVATION_MAX_CHARS = int(os.environ.get("D4J_SUITE_TOOL_OBSERVATION_MAX_CHARS", "5000"))
GREP_MAX_RESULTS = int(os.environ.get("D4J_SUITE_GREP_MAX_RESULTS", "80"))
GREP_TIMEOUT_SECONDS = int(os.environ.get("D4J_SUITE_GREP_TIMEOUT_SECONDS", "30"))
SKILL_MAX_MATCHED_TAGS = int(os.environ.get("D4J_SKILL_MAX_MATCHED_TAGS", "3"))
SKILL_MAX_STEPS_AFTER_READ = int(os.environ.get("D4J_SKILL_MAX_STEPS_AFTER_READ", "10"))
SKILL_TIER_GATE_DEFAULT = os.environ.get("D4J_SKILL_TIER_GATE", "1").strip().lower() not in {"0", "false", "no"}
_D4J_TESTGEN_RUNTIME_READY = False
TRANSIENT_LLM_ERROR_PATTERNS = (
    "429",
    "503",
    "rate limit",
    "rate_limit",
    "too busy",
    "temporarily",
    "timeout",
    "timed out",
    "connection",
    "server error",
    "service unavailable",
)


def _is_transient_llm_error(exc: Exception) -> bool:
    text = str(exc).lower()
    return any(pattern in text for pattern in TRANSIENT_LLM_ERROR_PATTERNS)


def _chat_completion_with_retry(
    client: Any,
    kwargs: dict[str, Any],
    *,
    max_retries: int = DEFAULT_LLM_MAX_RETRIES,
) -> Any:
    last_exc: Exception | None = None
    for attempt in range(max(1, max_retries)):
        try:
            return client.chat.completions.create(**kwargs)
        except Exception as exc:
            last_exc = exc
            if attempt >= max_retries - 1 or not _is_transient_llm_error(exc):
                raise
            delay = min(90, 5 * (2 ** attempt))
            print(
                f"[llm-retry] transient LLM error; retry {attempt + 2}/{max_retries} after {delay}s: {str(exc)[:220]}",
                flush=True,
            )
            time.sleep(delay)
    if last_exc is not None:
        raise last_exc
    raise RuntimeError("LLM retry loop exited unexpectedly")


# ---------------------------------------------------------------------------
# Skill Bank helpers
# ---------------------------------------------------------------------------

TIER_RECOVERY_TIERS = {"FAIL_ON_FIXED", "COMPILE_FAIL", "NO_TEST_GENERATED"}
KNOWN_RESULT_TIERS = {"BUG_DETECTED", "PASS_BOTH", "FAIL_ON_FIXED", "COMPILE_FAIL", "NO_TEST_GENERATED"}


def _normalize_result_tier(value: Any) -> str:
    tier = re.sub(r"[^A-Z0-9]+", "_", str(value or "").strip().upper()).strip("_")
    aliases = {
        "PASS_PASS": "PASS_BOTH",
        "NO_TEST": "NO_TEST_GENERATED",
        "NO_TESTS": "NO_TEST_GENERATED",
        "NO_TEST_GENERATION": "NO_TEST_GENERATED",
        "NOTEST": "NO_TEST_GENERATED",
        "COMPILE": "COMPILE_FAIL",
        "COMPILATION_FAIL": "COMPILE_FAIL",
        "COMPILE_ERROR": "COMPILE_FAIL",
        "COMPILATION_ERROR": "COMPILE_FAIL",
        "FAIL_FIXED": "FAIL_ON_FIXED",
        "FIXED_FAIL": "FAIL_ON_FIXED",
    }
    return aliases.get(tier, tier)


def _frontmatter_from_markdown(content: str) -> dict[str, Any]:
    if not str(content or "").lstrip().startswith("---"):
        return {}
    match = re.match(r"\s*---\s*\n(.*?)\n---\s*(?:\n|$)", content or "", flags=re.DOTALL)
    if not match:
        return {}
    try:
        import yaml as _yaml

        meta = _yaml.safe_load(match.group(1)) or {}
        return meta if isinstance(meta, dict) else {}
    except Exception:
        return {}


def _as_string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        return [str(item).strip() for item in value if str(item).strip()]
    return [str(value).strip()] if str(value).strip() else []


def _skill_is_active(meta: dict[str, Any]) -> bool:
    evolution = meta.get("evolution") if isinstance(meta.get("evolution"), dict) else {}
    active = evolution.get("active", True) if isinstance(evolution, dict) else True
    return str(active).strip().lower() not in {"0", "false", "no", "deprecated", "inactive"}


def _skill_matches_tier(name: str, meta: dict[str, Any], tier: str) -> bool:
    """Strict metadata-only tier match.

    This intentionally ignores the skill body and loose description keywords.
    Static skills often mention words such as "failed" or "assertion" in their
    prose, which must not make them COMPILE_FAIL/FAIL_ON_FIXED recovery skills.
    """
    tier = _normalize_result_tier(tier)
    if tier not in KNOWN_RESULT_TIERS:
        return False
    if not _skill_is_active(meta):
        return False

    retrieval = meta.get("retrieval") if isinstance(meta.get("retrieval"), dict) else {}
    applicable = {
        _normalize_result_tier(item)
        for item in _as_string_list(retrieval.get("applicable_tiers") if isinstance(retrieval, dict) else [])
    }
    if tier in applicable:
        return True

    code_tags = {
        _normalize_result_tier(item)
        for item in _as_string_list(meta.get("code_tags") or meta.get("tags"))
    }
    if tier in code_tags:
        return True
    if "TIER_RECOVERY" in code_tags and tier in code_tags:
        return True

    slug = re.sub(r"[^a-z0-9]+", "-", str(name or "").lower()).strip("-")
    controlled = {
        "PASS_BOTH": ("pass-both", "pass-pass"),
        "FAIL_ON_FIXED": ("fail-on-fixed", "fixed-fail"),
        "COMPILE_FAIL": ("compile-fail", "compilation-fail", "compile-error"),
        "NO_TEST_GENERATED": ("no-test-generated", "no-test", "notest"),
    }
    return any(token in slug for token in controlled.get(tier, ()))


def _tier_matched_skill_names(skill_bank: dict[str, Any] | None, tier: str) -> list[str]:
    if not skill_bank:
        return []
    tier = _normalize_result_tier(tier)
    metas = skill_bank.get("skill_meta") or {}
    names = [
        name
        for name, meta in metas.items()
        if isinstance(meta, dict) and _skill_matches_tier(str(name), meta, tier)
    ]
    return sorted(names)


def _skill_bank_allowed_for_tier(skill_bank: dict[str, Any] | None, tier: str, *, tier_gate: bool = True) -> tuple[bool, list[str]]:
    """Return whether skills should be exposed for a retry targeting ``tier``.

    PASS_BOTH remains the default skill-use case: the static bank was built from
    code/bug-pattern knowledge and is still useful there even if it lacks
    explicit PASS_BOTH metadata. For lower tiers, expose skills only when the
    bank has explicit tier-recovery metadata.
    """
    if not skill_bank:
        return False, []
    tier = _normalize_result_tier(tier)
    if not tier_gate or tier == "PASS_BOTH":
        return True, _tier_matched_skill_names(skill_bank, tier)
    if tier in TIER_RECOVERY_TIERS:
        matches = _tier_matched_skill_names(skill_bank, tier)
        return bool(matches), matches
    return False, []


def _augment_level1_index_from_skill_meta(index: dict[str, Any], skill_meta: dict[str, dict[str, Any]]) -> dict[str, Any]:
    index = dict(index or {})
    level1 = dict(index.get("level1_tags") or {})
    for name, meta in sorted(skill_meta.items()):
        if not isinstance(meta, dict):
            continue
        desc = str(meta.get("description") or "")
        for tag in _as_string_list(meta.get("code_tags") or meta.get("tags")):
            tag = tag.strip()
            if not tag:
                continue
            entry = level1.setdefault(tag, {"level2_skills": []})
            l2 = entry.setdefault("level2_skills", [])
            if not any(item.get("name") == name for item in l2 if isinstance(item, dict)):
                l2.append({
                    "name": name,
                    "title": str(meta.get("title") or name),
                    "description": desc,
                    "sources": _as_string_list((meta.get("evolution") or {}).get("sources") if isinstance(meta.get("evolution"), dict) else []),
                })
    index["level1_tags"] = level1
    return index


def _load_skill_bank(skill_bank_path: str) -> dict[str, Any] | None:
    """Load a skill bank index, skill markdown contents, and frontmatter metadata.

    Returns a dict with keys:
      - index: parsed/derived Level 1 tag -> Level 2 skill summaries
      - skills: dict of skill_name -> full markdown content
      - skill_meta: dict of skill_name -> YAML frontmatter
    Or None if the path doesn't exist or is malformed.
    """
    import yaml as _yaml

    bp = Path(skill_bank_path)
    index_file = bp / "_index.yaml"
    model_index_file = bp / "_index_model.yaml"
    skills_dir = bp / "skills"
    if not skills_dir.is_dir():
        print(f"[skill-bank] Warning: {skill_bank_path} is not a valid skill bank (missing skills/)")
        return None
    index: dict[str, Any] = {}
    if index_file.exists():
        try:
            with open(index_file) as f:
                parsed = _yaml.safe_load(f) or {}
                index = parsed if isinstance(parsed, dict) else {}
        except Exception as exc:
            print(f"[skill-bank] Warning: failed to load _index.yaml: {exc}")
            index = {}
    elif model_index_file.exists():
        try:
            with open(model_index_file) as f:
                parsed = _yaml.safe_load(f) or {}
                index = parsed if isinstance(parsed, dict) else {}
        except Exception as exc:
            print(f"[skill-bank] Warning: failed to load _index_model.yaml: {exc}")
            index = {}
    skills: dict[str, str] = {}
    skill_meta: dict[str, dict[str, Any]] = {}
    for fname in sorted(skills_dir.glob("*.md")):
        try:
            content = fname.read_text(encoding="utf-8")
        except Exception:
            continue
        meta = _frontmatter_from_markdown(content)
        match = re.search(r"^name:\s*(.+)$", content, re.MULTILINE)
        skill_name = str(meta.get("name") or (match.group(1).strip() if match else fname.stem)).strip()
        if skill_name:
            skills[skill_name] = content
            skill_meta[skill_name] = meta
    index = _augment_level1_index_from_skill_meta(index, skill_meta)
    tier_counts = {tier: len(_tier_matched_skill_names({"skill_meta": skill_meta}, tier)) for tier in sorted(KNOWN_RESULT_TIERS)}
    print(f"[skill-bank] Loaded {len(skills)} skills from {skill_bank_path}; tier metadata counts={tier_counts}")
    return {"index": index, "skills": skills, "skill_meta": skill_meta, "tier_counts": tier_counts}


def _extract_level1_tags(focal_source: str, focal_method_name: str) -> list[str]:
    """Deterministic code static analysis — extract Level 1 tags from focal source.

    No LLM involved. Rules are based on observable method characteristics:
    method name, parameter types, return type, visibility, and overload count.
    """
    tags: set[str] = set()
    if not focal_source or not focal_method_name:
        return []
    source_lower = focal_source.lower()
    method_lower = focal_method_name.lower()
    method_escaped = re.escape(focal_method_name)

    # --- method name pattern matching ---
    # A1: equals/hashCode — only match when the focal method IS literally equals/hashCode,
    #     NOT when the source file merely contains an equals() method somewhere.
    if method_lower in ("equals", "hashcode"):
        tags.add("equals")  # hashCode folded under equals (always tested together)
    if method_lower == "clone":
        tags.add("clone")
    if any(kw in method_lower for kw in ["copy", "duplicate", "deepcopy", "shallowcopy"]):
        tags.add("copy")
    # A3: parse — added create*, from*, valueOf (evidenced by Lang-27 createNumber)
    if (any(method_lower.startswith(kw) for kw in ["create", "from"]) or
        any(kw in method_lower for kw in ["parse", "tokenize", "scan", "decode", "token", "valueof"])):
        tags.add("parse")
    if any(kw in method_lower for kw in ["serialize", "deserialize", "write", "read", "encode",
                                          "format", "marshal", "unmarshal"]):
        tags.add("serialize")
    if method_lower == "compareto" or "comparator" in source_lower or "comparable" in source_lower:
        tags.add("compare")
    if any(kw in method_lower for kw in ["validate", "check", "verify", "ensure", "assert"]):
        tags.add("validate")
    # A2: arithmetic method names → numeric (evidenced by Math-53 add)
    if any(kw in method_lower for kw in ["add", "subtract", "multiply", "divide",
                                          "increment", "decrement", "pow", "sqrt", "cross", "dot", "norm"]):
        tags.add("numeric")

    # --- parameter type matching from method signature ---
    sig_pat = re.compile(
        rf'(?:public|protected|private|static|\s)+[\w\<\>\[\],\s]+\s+{method_escaped}\s*\(([^)]*)\)',
        re.IGNORECASE,
    )
    sig_match = sig_pat.search(focal_source)
    sig = sig_match.group(1) if sig_match else ""

    if any(t in sig for t in ["InputStream", "OutputStream", "Reader", "Writer", "Stream", "Channel"]):
        tags.add("stream")
        tags.add("input_representation")
    if any(t in sig for t in ["int ", "long ", "double ", "float ", "Number", "Integer", "Long", "Double", "Float"]):
        tags.add("numeric")
    if any(t in sig for t in ["List<", "Set<", "Map<", "Collection<", "[]", "Iterable", "Iterator"]):
        tags.add("collection")

    # --- visibility ---
    vis_pat = re.compile(
        rf'(private|protected)\s+[\w\<\>\[\],\s]+\s+{method_escaped}\s*\(',
    )
    if vis_pat.search(focal_source):
        tags.add("private_method")

    # --- overload detection (count method DECLARATIONS only) ---
    overload_matches = re.findall(
        rf'(?:public|protected|private|static|\s)+[\w\<\>\[\],\s]+\s+{method_escaped}\s*\(',
        focal_source,
    )
    if len(overload_matches) > 1:
        tags.add("overload")

    # --- void + field assignment -> state_mutate ---
    if re.search(rf'\bvoid\s+{method_escaped}\s*\(', focal_source):
        if re.search(r'\bthis\.\w+\s*(?:=|\+=|-=|\*=|/=|%=)', focal_source):
            tags.add("state_mutate")

    # --- complex constructor / builder chain ---
    if re.search(rf'(?:public|protected)\s+\w+\s*\([^)]*\)\s*(?:throws\s+\w+)?\s*\{{\s*(?:this\.\w+\s*=\s*\w+\s*;?\s*){{3,}}', focal_source):
        tags.add("complex_init")
    if any(kw in method_lower for kw in ["init", "initialize", "setup", "configure", "build"]):
        tags.add("complex_init")

    # --- D4J failure-mode routing ---
    order_signals = [
        "append", "prepend", "insert", "before", "after", "order", "sort", "index",
        "position", "child", "sibling", "first", "last", "next", "previous",
    ]
    if any(kw in method_lower or kw in source_lower for kw in order_signals):
        tags.add("order_sensitive_oracle")

    input_representation_signals = [
        "bytebuffer", "byte[]", "inputstream", "reader", "charset", "encoding",
        "bom", "utf", "decode", "encode", "url", "uri", "raw", "stream",
    ]
    if any(kw in method_lower or kw in source_lower for kw in input_representation_signals):
        tags.add("input_representation")

    parser_path_signals = [
        "parser", "parse", "token", "selector", "evaluator", "queryparser",
        "html", "css", "json", "csv", "syntax", "grammar", "state",
    ]
    if any(kw in method_lower or kw in source_lower for kw in parser_path_signals):
        tags.add("parser_path_trigger")

    numeric_stability_signals = [
        "safe_min", "epsilon", "nan", "infinity", "overflow", "underflow",
        "scalb", "getexponent", "rint", "round", "double", "float",
        "precision", "cosh", "sinh", "norm", "crossproduct", "dotproduct",
    ]
    if "numeric" in tags or any(kw in method_lower or kw in source_lower for kw in numeric_stability_signals):
        tags.add("numeric_stability")

    mutation_signals = [
        "clone", "copy", "cache", "classnames", "add", "remove", "clear",
        "update", "reset", "set", "mutable", "iterator", "sublist", "view",
    ]
    if any(kw in method_lower or kw in source_lower for kw in mutation_signals):
        tags.add("mutation_isolation")

    serialization_signals = [
        "json", "jackson", "gson", "objectmapper", "jsonnode", "typefactory",
        "serialize", "deserialize", "readvalue", "writevalue", "typevariable",
        "polymorphic", "yaml", "xml",
    ]
    if any(kw in method_lower or kw in source_lower for kw in serialization_signals):
        tags.add("type_serialization")

    exception_signals = [
        "throw", "exception", "invalid", "malformed", "null", "empty", "validate",
        "unchecked", "ioexception", "illegalargumentexception",
    ]
    if any(kw in method_lower or kw in source_lower for kw in exception_signals):
        tags.add("exception_contract")

    return sorted(tags)


def _rank_level1_tags(
    tags: list[str],
    focal_source: str,
    focal_method_name: str,
    skill_bank: dict[str, Any] | None,
) -> list[str]:
    """Rank and cap Level 1 tags before exposing skills to the TG.

    The static extractor intentionally over-recalls. This function keeps only
    skill-bank-backed tags and ranks D4J failure-mode tags by stronger local
    signals so the agent does not receive an overwhelming menu.
    """
    if not tags:
        return []
    available: set[str] | None = None
    if skill_bank is not None:
        available = set(((skill_bank.get("index") or {}).get("level1_tags") or {}).keys())
    source_lower = (focal_source or "").lower()
    method_lower = (focal_method_name or "").lower()
    scores: dict[str, int] = {}
    for tag in tags:
        if available is not None and tag not in available:
            continue
        score = 1
        if tag == "input_representation":
            if any(k in source_lower or k in method_lower for k in ["bytebuffer", "bom", "charset", "encoding", "inputstream", "reader"]):
                score += 14
            if any(k in method_lower for k in ["decode", "encode", "read", "write"]):
                score += 5
            if any(k in source_lower or k in method_lower for k in ["url", "uri", "raw"]):
                score += 2
        elif tag == "parser_path_trigger":
            if any(k in method_lower for k in ["parse", "token", "selector", "query", "clean"]):
                score += 14
            if any(k in source_lower for k in ["queryparser", "evaluator.", "selector", "tokenqueue", "htmltreebuilder"]):
                score += 10
            if any(k in source_lower for k in ["parser", "parse", "token", "html", "css", "json", "csv"]):
                score += 3
        elif tag == "numeric_stability":
            if any(k in method_lower for k in ["add", "subtract", "multiply", "divide", "pow", "sqrt", "cross", "dot", "norm", "cosh"]):
                score += 14
            if any(k in source_lower for k in ["safe_min", "epsilon", "nan", "infinity", "scalb", "getexponent", "overflow", "underflow", "crossproduct", "dotproduct"]):
                score += 12
            if any(k in source_lower for k in ["double", "float"]):
                score += 2
        elif tag == "mutation_isolation":
            if any(k in method_lower for k in ["clone", "copy", "reset", "remove", "add", "clear", "update"]):
                score += 15
            if any(k in source_lower for k in ["cache", "classnames", "sublist", "iterator", "mutable", "shallow"]):
                score += 10
        elif tag == "order_sensitive_oracle":
            if any(k in method_lower for k in ["append", "prepend", "insert", "sort", "index", "first", "last", "next", "previous"]):
                score += 12
            if any(k in source_lower for k in ["append", "prepend", "insert", "order", "sort", "child", "sibling"]):
                score += 7
        elif tag == "type_serialization":
            if any(k in source_lower or k in method_lower for k in ["jackson", "gson", "jsonnode", "objectmapper", "typefactory", "serialize", "deserialize"]):
                score += 8
        elif tag == "exception_contract":
            if any(k in source_lower or k in method_lower for k in ["throw", "exception", "invalid", "malformed", "null", "empty"]):
                score += 5
        elif tag == "api_reality":
            score += 2
        scores[tag] = score
    ranked = sorted(scores, key=lambda t: (-scores[t], t))
    if SKILL_MAX_MATCHED_TAGS > 0:
        ranked = ranked[:SKILL_MAX_MATCHED_TAGS]
    return ranked


def _skill_tool_specs() -> list[dict[str, Any]]:
    """Tool definitions for list_skills() and read_skill(name)."""
    return [
        {
            "type": "function",
            "function": {
                "name": "list_skills",
                "description": (
                    "List available testing guides (skills) for the current focal method type. "
                    "Returns a summary of each skill: name, title, one-line description, and source training cases. "
                    "Call this when a guide may help; then use read_skill(name) to load any specific guide worth inspecting."
                ),
                "parameters": {"type": "object", "properties": {}, "required": []},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "read_skill",
                "description": (
                    "Read the full checklist content of a specific testing guide. "
                    "The guide contains WHEN/THEN/DON'T instructions for testing this type of method. "
                    "You can call this multiple times to load different guides."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "The skill name, e.g. 'equals-1'. Get names from list_skills() first.",
                        },
                    },
                    "required": ["name"],
                },
            },
        },
    ]


def _execute_skill_tool(
    tool_name: str,
    args: dict[str, Any],
    skill_bank: dict[str, Any],
    matched_tags: list[str],
    tier_skill_names: list[str] | None = None,
    target_tier: str = "",
) -> str:
    """Execute a skill-related tool call. Returns the observation string."""
    if tool_name == "list_skills":
        index = skill_bank.get("index", {})
        l1_tags = index.get("level1_tags", {})
        lines: list[str] = []
        lines.append(f"Available testing guides for focal method (matched tags: {', '.join(matched_tags)}):")
        lines.append("")
        listed_names: set[str] = set()
        tier_name_set = set(tier_skill_names or [])
        normalized_target = _normalize_result_tier(target_tier)
        for tag in matched_tags:
            if tag.startswith("tier:"):
                continue
            tag_info = l1_tags.get(tag, {})
            l2_list = tag_info.get("level2_skills", [])
            if tier_name_set and tag in {normalized_target, "TIER_RECOVERY"}:
                l2_list = [item for item in l2_list if str(item.get("name") or "") in tier_name_set]
            l2_list = [item for item in l2_list if str(item.get("name") or "") not in listed_names]
            if not l2_list:
                continue
            lines.append(f"## {tag}")
            for l2 in l2_list:
                name = l2.get("name", "?")
                listed_names.add(str(name))
                title = l2.get("title", "")
                desc = l2.get("description", "")
                sources = l2.get("sources", [])[:3]
                src_str = ", ".join(sources) if sources else "training data"
                lines.append(f"  - **{name}**: {title}")
                lines.append(f"    {desc}")
                lines.append(f"    Sources: {src_str}")
            lines.append("")
        extra_tier_names = [name for name in (tier_skill_names or []) if name not in listed_names]
        if extra_tier_names:
            metas = skill_bank.get("skill_meta") or {}
            lines.append(f"## Tier recovery skills for {normalized_target}")
            for name in extra_tier_names:
                meta = metas.get(name) or {}
                lines.append(f"  - **{name}**: {meta.get('title') or name}")
                if meta.get("description"):
                    lines.append(f"    {meta.get('description')}")
            lines.append("")
        if len(lines) <= 2:
            return "No testing guides matched the current focal method."
        return "\n".join(lines)

    if tool_name == "read_skill":
        name = str(args.get("name", "")).strip()
        if not name:
            return "Error: 'name' parameter is required for read_skill."
        skills = skill_bank.get("skills", {})
        content = skills.get(name)
        if content is None:
            available = sorted(skills.keys())
            return f"Skill '{name}' not found. Available skills: {', '.join(available[:20])}{'...' if len(available) > 20 else ''}"
        # Return the body (after YAML frontmatter)
        parts = content.split("---", 2)
        body = parts[2].strip() if len(parts) >= 3 else content
        return body

    return f"Unknown skill tool: {tool_name}"


def _skill_tools_for_record(
    *,
    fixed_dir: str,
    record: dict[str, Any],
    skill_bank: dict[str, Any] | None,
    log_label: str,
    target_tier: str = "",
    precomputed_tier_skill_names: list[str] | None = None,
) -> tuple[list[dict[str, Any]] | None, Any, list[str]]:
    if skill_bank is None:
        return None, None, []
    _focal_file, focal_source = _focal_file_and_source(
        fixed_dir,
        record,
        DEFAULT_MAX_SOURCE_CHARS,
    )
    method_name = d4j._method_name_from_signature(
        str(record.get("method_name") or record.get("focal_method") or ""),
    )
    matched_tags = _rank_level1_tags(
        _extract_level1_tags(focal_source or "", method_name),
        focal_source or "",
        method_name,
        skill_bank,
    )
    tier_skill_names = list(precomputed_tier_skill_names or _tier_matched_skill_names(skill_bank, target_tier))
    available = set(((skill_bank.get("index") or {}).get("level1_tags") or {}).keys())
    tier_tags: list[str] = []
    normalized_target = _normalize_result_tier(target_tier)
    if tier_skill_names:
        for preferred in (normalized_target, "TIER_RECOVERY"):
            if preferred in available and preferred not in tier_tags:
                tier_tags.append(preferred)
        metas = skill_bank.get("skill_meta") or {}
        for name in tier_skill_names:
            meta = metas.get(name) or {}
            for tag in _as_string_list(meta.get("code_tags") or meta.get("tags")):
                if tag in available and tag not in tier_tags:
                    tier_tags.append(tag)
                if len(tier_tags) >= max(2, SKILL_MAX_MATCHED_TAGS):
                    break
            if len(tier_tags) >= max(2, SKILL_MAX_MATCHED_TAGS):
                break
    matched_tags = list(dict.fromkeys(tier_tags + matched_tags))
    if tier_skill_names and not matched_tags:
        matched_tags = [f"tier:{normalized_target}"]
    print(
        f"[skill-bank] {log_label}: target_tier={normalized_target or 'NA'} "
        f"matched_tags={matched_tags} tier_skill_count={len(tier_skill_names)}"
    )
    if not matched_tags:
        return None, None, []

    def _exec(name: str, args: dict[str, Any]) -> str | None:
        if name in ("list_skills", "read_skill"):
            return _execute_skill_tool(
                name,
                args,
                skill_bank,
                matched_tags,
                tier_skill_names=tier_skill_names,
                target_tier=target_tier,
            )
        return None

    return _skill_tool_specs(), _exec, matched_tags


def _strip_code_fences(text: str) -> str:
    text = (text or "").strip()
    text = re.sub(r"^```(?:json|java)?\s*\n?", "", text)
    text = re.sub(r"\n?```\s*$", "", text)
    return text.strip()


def _extract_java_package(source: str) -> str:
    match = re.search(r"(?m)^\s*package\s+([\w.]+)\s*;", source or "")
    return match.group(1) if match else ""


def _extract_java_imports(source: str) -> list[str]:
    imports: list[str] = []
    for match in re.finditer(r"(?m)^\s*import\s+([^;]+)\s*;", source or ""):
        item = match.group(1).strip()
        if item and item not in imports:
            imports.append(item)
    return imports


def _sanitize_identifier(value: str, default: str = "Generated") -> str:
    token = d4j._sanitize_java_identifier(str(value or ""), default=default)
    return token if token else default


def _test_package_for(source_package: str, mode: str) -> str:
    if mode == "same":
        return source_package
    if source_package:
        return f"gentest.{source_package}.tests"
    return "gentest.tests"


def _method_blocks(code: str) -> list[tuple[str, str]]:
    blocks: list[tuple[str, str]] = []
    for name, start, end in d4j._find_java_void_method_blocks(code):
        method = _strip_code_fences(code)[start:end].strip()
        if re.search(r"@(?:[\w.]+\.)?Test\b", method):
            blocks.append((name, method))
    return blocks


def _parse_json_object_robust(text: str) -> dict[str, Any]:
    """Parse a JSON object from prose-heavy model output.

    Prefer the last object that contains ``test_methods``. This avoids the
    greedy ``{.*}`` failure mode when earlier Java snippets contain braces.
    """
    text = (text or "").strip()
    if not text:
        return {}
    candidates: list[tuple[int, dict[str, Any]]] = []
    decoder = json.JSONDecoder()

    def try_add(candidate: str, offset: int) -> None:
        candidate = _strip_code_fences(candidate)
        try:
            obj = json.loads(candidate)
            if isinstance(obj, dict):
                candidates.append((offset, obj))
                return
        except Exception:
            pass
        for match in re.finditer(r"\{", candidate):
            try:
                obj, end = decoder.raw_decode(candidate[match.start():])
            except Exception:
                continue
            if isinstance(obj, dict):
                candidates.append((offset + match.start() + end, obj))

    try_add(text, 0)
    for match in re.finditer(r"```(?:json)?\s*(.*?)```", text, flags=re.DOTALL | re.IGNORECASE):
        try_add(match.group(1), match.start())
    for marker in ('{"class_name"', '{"test_class_name"', '{"test_methods"'):
        idx = text.rfind(marker)
        if idx >= 0:
            try_add(text[idx:], idx)

    if not candidates:
        return {}
    with_methods = [(pos, obj) for pos, obj in candidates if isinstance(obj.get("test_methods"), list)]
    if with_methods:
        return sorted(with_methods, key=lambda item: item[0])[-1][1]
    return sorted(candidates, key=lambda item: item[0])[-1][1]


def _extract_test_methods_from_response(content: str) -> list[dict[str, str]]:
    """Extract generated ``test_methods`` from JSON or Java output."""
    content = content or ""
    parsed: dict[str, Any] = {}
    try:
        parsed = _parse_json_object_robust(content)
    except Exception:
        parsed = {}

    methods: list[dict[str, str]] = []
    raw_methods = parsed.get("test_methods") if isinstance(parsed, dict) else None
    if isinstance(raw_methods, list):
        for item in raw_methods:
            if not isinstance(item, dict):
                continue
            code = str(item.get("pure_test_method") or item.get("test_method") or item.get("code") or "").strip()
            if not code:
                continue
            code = _strip_code_fences(code)
            name = str(item.get("test_method_name") or item.get("name") or "").strip()
            if not name:
                match = re.search(r"\bvoid\s+(\w+)\s*\(", code)
                name = match.group(1) if match else "testGenerated"
            methods.append({"test_method_name": name, "pure_test_method": code})
    if methods:
        return methods

    # Fallback: parse Java code blocks or a whole class returned by the model.
    candidates = re.findall(r"```java\s*(.*?)```", content, flags=re.DOTALL | re.IGNORECASE)
    if not candidates:
        candidates = [content]
    for candidate in candidates:
        for name, method in _method_blocks(candidate):
            methods.append({"test_method_name": name, "pure_test_method": method})
    return methods


def _ensure_unique_test_method_names(methods: list[dict[str, str]]) -> list[dict[str, str]]:
    used: set[str] = set()
    unique: list[dict[str, str]] = []
    for idx, item in enumerate(methods, 1):
        code = _strip_code_fences(str(item.get("pure_test_method") or ""))
        match = re.search(r"\bvoid\s+(\w+)\s*\(", code)
        raw_name = str(item.get("test_method_name") or (match.group(1) if match else "") or f"testGenerated{idx}")
        base = re.sub(r"\W+", "_", raw_name).strip("_") or f"testGenerated{idx}"
        if base[0].isdigit():
            base = f"test_{base}"
        name = base
        suffix = 2
        while name in used:
            name = f"{base}{suffix}"
            suffix += 1
        used.add(name)

        if not re.search(r"@(?:[\w.]+\.)?Test\b", code):
            code = "@Test\n" + code
        if not re.search(r"\bpublic\s+void\s+", code):
            code = re.sub(r"\bvoid\s+", "public void ", code, count=1)
        if match and match.group(1) != name:
            code = re.sub(rf"\b{re.escape(match.group(1))}\s*\(", f"{name}(", code, count=1)
        unique.append({"test_method_name": name, "pure_test_method": code})
    return unique


def assemble_generated_suite_class(
    *,
    test_class_name: str,
    test_package: str,
    focal_package: str,
    source_imports: list[str],
    test_methods: list[dict[str, str]],
) -> str:
    """Assemble one JUnit4 generated-suite class."""
    imports = [
        "org.junit.Test",
        "org.junit.Rule",
        "org.junit.rules.ExpectedException",
        "static org.junit.Assert.*",
        "java.lang.reflect.Method",
        "java.lang.reflect.Field",
        "java.lang.reflect.Constructor",
        "java.lang.reflect.*",
        "java.util.ArrayList",
        "java.util.List",
        "java.io.ByteArrayInputStream",
        "java.io.ByteArrayOutputStream",
    ]
    if focal_package:
        imports.append(f"{focal_package}.*")
    imports.extend(source_imports)

    seen: set[str] = set()
    lines: list[str] = []
    if test_package:
        lines.append(f"package {test_package};")
    for item in imports:
        item = item.strip().rstrip(";")
        if not item or item in seen:
            continue
        seen.add(item)
        lines.append(f"import {item};")
    lines.extend(["", f"public class {test_class_name} {{", "    @Rule", "    public ExpectedException thrown = ExpectedException.none();", ""])
    for method in _ensure_unique_test_method_names(test_methods):
        code = method["pure_test_method"].strip()
        for line in code.splitlines():
            lines.append("    " + line if line.strip() else "")
        lines.append("")
    lines.append("}")
    lines.append("")
    return "\n".join(lines)


def _java_code_body_without_imports(code: str) -> str:
    lines = []
    for line in str(code or "").splitlines():
        if re.match(r"\s*(?:package|import)\b", line):
            continue
        lines.append(line)
    return "\n".join(lines)


def _import_simple_name(import_target: str) -> str:
    item = import_target.strip().rstrip(";")
    if item.startswith("static "):
        item = item[len("static "):].strip()
    if item.endswith(".*"):
        return "*"
    return item.rsplit(".", 1)[-1]


def _prune_generated_imports(code: str, compiler_output: str = "") -> tuple[str, list[str]]:
    """Remove imports that are clearly unused or reported missing by javac."""
    body = _java_code_body_without_imports(code)
    missing_packages = set(re.findall(r"error:\s+package\s+([\w.]+)\s+does not exist", compiler_output or ""))
    notes: list[str] = []
    kept: list[str] = []
    for line in str(code or "").splitlines():
        match = re.match(r"(\s*import\s+)(static\s+)?([^;]+)(;\s*)$", line)
        if not match:
            kept.append(line)
            continue
        is_static = bool(match.group(2))
        target = match.group(3).strip()
        simple = _import_simple_name(("static " if is_static else "") + target)
        remove_reason = ""
        if any(target == pkg or target.startswith(pkg + ".") for pkg in missing_packages):
            remove_reason = f"javac reported package {target} missing"
        elif target in {"org.mockito.junit.MockitoJUnitRunner", "org.junit.runner.RunWith"} and simple not in body:
            remove_reason = f"unused generated import {target}"
        elif target == "org.mockito.Mockito.*" and not re.search(r"\b(?:Mockito|mock|when|verify|spy|any|eq)\s*\(", body):
            remove_reason = "unused generated Mockito static import"
        elif not is_static and simple != "*" and not re.search(rf"\b{re.escape(simple)}\b", body):
            remove_reason = f"unused import {target}"
        if remove_reason:
            notes.append(remove_reason)
            continue
        kept.append(line)
    return "\n".join(kept) + ("\n" if code.endswith("\n") else ""), notes


def _extract_java_file_from_response(content: str) -> str:
    code_blocks = re.findall(r"```java\s*(.*?)```", content or "", flags=re.DOTALL | re.IGNORECASE)
    if code_blocks:
        return _strip_code_fences(code_blocks[-1])
    text = _strip_code_fences(content or "")
    starts = [
        pos for pos in [
            text.find("package "),
            text.find("import "),
            text.find("public class "),
            text.find("class "),
        ] if pos >= 0
    ]
    if starts:
        text = text[min(starts):]
    return text.strip()


def _assemble_repaired_class_from_methods(
    current_code: str,
    *,
    test_class_name: str,
    test_package: str,
    methods: list[dict[str, str]],
) -> str:
    """Rebuild a complete test class when repair returns method JSON/snippets."""
    current_code = current_code or ""
    package_match = re.search(r"^\s*package\s+([\w.]+)\s*;", current_code, flags=re.MULTILINE)
    package_name = test_package or (package_match.group(1) if package_match else "")

    imports: list[str] = []
    seen_imports: set[str] = set()
    for match in re.finditer(r"^\s*import\s+(?:static\s+)?[^;]+;", current_code, flags=re.MULTILINE):
        line = match.group(0).strip()
        if line not in seen_imports:
            imports.append(line)
            seen_imports.add(line)

    class_header_members: list[str] = []
    class_match = re.search(r"\bclass\s+\w+[^{]*\{", current_code)
    first_test = current_code.find("@Test")
    if class_match and first_test > class_match.end():
        prefix = current_code[class_match.end():first_test]
        if "ExpectedException" in prefix or "@Rule" in prefix:
            class_header_members = [line.rstrip() for line in prefix.strip().splitlines() if line.strip()]

    lines: list[str] = []
    if package_name:
        lines.append(f"package {package_name};")
    lines.extend(imports)
    if lines:
        lines.append("")
    lines.append(f"public class {test_class_name} {{")
    if class_header_members:
        for line in class_header_members:
            lines.append("    " + line.lstrip())
        lines.append("")
    for method in _ensure_unique_test_method_names(methods):
        code = _strip_code_fences(str(method.get("pure_test_method") or "")).strip()
        if not code:
            continue
        for line in code.splitlines():
            lines.append("    " + line if line.strip() else "")
        lines.append("")
    lines.append("}")
    lines.append("")
    return "\n".join(lines)


def _looks_like_complete_java_test_class(source: str) -> bool:
    return bool(re.search(r"\bclass\s+\w+[^{]*\{", source or "")) and "@Test" in (source or "")


def _build_test_class_name(record: dict[str, Any], focal_idx: int) -> str:
    _pkg, simple = d4j._focal_package_and_simple_class(record)
    method = d4j._method_name_from_signature(str(record.get("method_name") or record.get("focal_method") or "Method"))
    project = str(record.get("project") or "P")
    bug_id = str(record.get("bug_id") or "0")
    return (
        f"{_sanitize_identifier(simple)}"
        f"{_sanitize_identifier(method or 'Method')}"
        f"{_sanitize_identifier(project)}{_sanitize_identifier(bug_id)}F{focal_idx}Test"
    )


def _call_llm(messages: list[dict[str, str]], *, max_tokens: int = 4096) -> str:
    client = d4j._build_client()
    kwargs: dict[str, Any] = {
        "model": d4j.MODEL,
        "messages": messages,
        "temperature": 0.4,
        "max_tokens": max_tokens,
        "timeout": DEFAULT_LLM_TIMEOUT,
    }
    if d4j.MODEL in {"deepseek-v4-flash", "deepseek-v4-pro"}:
        kwargs["extra_body"] = {"thinking": {"type": "disabled"}}
    response = _chat_completion_with_retry(client, kwargs)
    return response.choices[0].message.content or ""


def _generation_tool_specs() -> list[dict[str, Any]]:
    return [
        {
            "type": "function",
            "function": {
                "name": "list_files",
                "description": "List files under a checkout subdirectory. Results are truncated.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "subpath": {
                            "type": "string",
                            "description": "Relative directory path from checkout root, default '.'.",
                        },
                    },
                    "required": [],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "grep_code",
                "description": "Search fixed-version checkout files with ripgrep. Results are truncated.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Regex or literal pattern to search for.",
                        },
                        "file_pattern": {
                            "type": "string",
                            "description": "Glob such as '*.java', '**/Foo.java', or 'src/main/**/*.java'.",
                        },
                    },
                    "required": ["query"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": "Read a file from the fixed-version checkout with optional 1-based line range. Output is truncated.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "relative_path": {
                            "type": "string",
                            "description": "Relative file path from checkout root.",
                        },
                        "start_line": {
                            "type": "integer",
                            "description": "Optional 1-based start line.",
                        },
                        "end_line": {
                            "type": "integer",
                            "description": "Optional 1-based end line.",
                        },
                    },
                    "required": ["relative_path"],
                },
            },
        },
    ]


def _truncate_observation(text: str, limit: int = TOOL_OBSERVATION_MAX_CHARS) -> str:
    text = str(text or "")
    if len(text) <= limit:
        return text
    return text[:limit] + f"\n... [tool output truncated, total {len(text)} chars]"


def _suite_grep_code(work_dir: str, query: str, file_pattern: str = "*.java") -> str:
    query = str(query or "")
    file_pattern = str(file_pattern or "*.java")
    if not query:
        return "Error: query is required."

    cmd = [
        "rg",
        "--line-number",
        "--color",
        "never",
        "--glob",
        file_pattern,
        "--glob",
        "!.git/**",
        "--max-count",
        str(GREP_MAX_RESULTS),
        query,
        ".",
    ]
    try:
        proc = subprocess.run(
            cmd,
            cwd=work_dir,
            capture_output=True,
            text=True,
            timeout=GREP_TIMEOUT_SECONDS,
        )
        if proc.returncode == 2:
            proc = subprocess.run(
                [
                    "rg",
                    "--fixed-strings",
                    "--line-number",
                    "--color",
                    "never",
                    "--glob",
                    file_pattern,
                    "--glob",
                    "!.git/**",
                    "--max-count",
                    str(GREP_MAX_RESULTS),
                    query,
                    ".",
                ],
                cwd=work_dir,
                capture_output=True,
                text=True,
                timeout=GREP_TIMEOUT_SECONDS,
            )
        text = (proc.stdout or "").strip()
        if not text:
            if proc.stderr:
                return _truncate_observation(proc.stderr.strip())
            return f"No matches found for '{query}' in {file_pattern} files."

        blocked = set()
        try:
            blocked = {p.replace("\\", "/") for p in d4j._get_blocked_test_files(work_dir)}
        except Exception:
            blocked = set()
        kept: list[str] = []
        for line in text.splitlines():
            rel = line.split(":", 1)[0].lstrip("./").replace("\\", "/")
            if blocked and any(rel.endswith(bp) or bp.endswith(rel) for bp in blocked):
                continue
            kept.append("./" + line.lstrip("./"))
            if len(kept) >= GREP_MAX_RESULTS:
                break
        if not kept:
            return f"No unrestricted matches found for '{query}' in {file_pattern} files."
        return _truncate_observation("\n".join(kept))
    except FileNotFoundError:
        return d4j.tg_grep_code(work_dir, query, file_pattern)
    except subprocess.TimeoutExpired:
        return f"Error: grep_code timed out after {GREP_TIMEOUT_SECONDS}s."
    except Exception as exc:
        return f"Error: grep_code failed: {exc}"


def _execute_generation_tool(work_dir: str, name: str, arguments: dict[str, Any]) -> str:
    arguments = arguments or {}
    if name == "list_files":
        return _truncate_observation(d4j.tg_list_files(work_dir, str(arguments.get("subpath") or ".")))
    if name == "grep_code":
        return _truncate_observation(
            _suite_grep_code(
                work_dir,
                str(arguments.get("query") or ""),
                str(arguments.get("file_pattern") or "*.java"),
            )
        )
    if name == "read_file":
        start = arguments.get("start_line")
        end = arguments.get("end_line")
        return _truncate_observation(
            d4j.tg_read_file(
                work_dir,
                str(arguments.get("relative_path") or ""),
                int(start) if start is not None else None,
                int(end) if end is not None else None,
            )
        )
    return f"Error: unknown tool {name}"


def _append_agent_trace(trace_path: str | None, event: dict[str, Any]) -> None:
    if not trace_path:
        return
    try:
        path = Path(trace_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = dict(event)
        payload.setdefault("ts", time.time())
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False, default=str) + "\n")
    except Exception:
        return


def _call_generation_agent(
    messages: list[dict[str, Any]],
    *,
    work_dir: str,
    max_tool_steps: int,
    max_tokens: int = 4096,
    final_instruction: str | None = None,
    context_compact_every: int = DEFAULT_CONTEXT_COMPACT_EVERY,
    extra_tools: list[dict[str, Any]] | None = None,
    extra_tool_executor: Any = None,  # callable(tool_name, args) -> str | None
    trace_path: str | None = None,
    require_extra_tool_read_skill: bool = True,
    skill_max_steps_after_read: int | None = None,
    initial_trajectory: list[dict[str, Any]] | None = None,
    initial_steps_since_compaction: int = 0,
    compaction_base_messages: list[dict[str, Any]] | None = None,
    return_state: bool = False,
) -> tuple[Any, ...]:
    if max_tool_steps <= 0:
        content = _call_llm(messages, max_tokens=max_tokens)
        base_trajectory = list(initial_trajectory or [])
        if return_state:
            return content, base_trajectory, {
                "conversation": list(messages) + [{"role": "assistant", "content": content}],
                "steps_since_compaction": max(0, int(initial_steps_since_compaction)),
                "compaction_base_messages": compaction_base_messages if compaction_base_messages is not None else messages,
            }
        return content, base_trajectory

    _append_agent_trace(trace_path, {
        "event": "start",
        "work_dir": work_dir,
        "max_tool_steps": max_tool_steps,
        "max_tokens": max_tokens,
        "has_extra_tools": bool(extra_tools),
        "context_compact_every": context_compact_every,
    })
    client = d4j._build_client()
    tools = list(_generation_tool_specs())
    if extra_tools:
        tools.extend(extra_tools)
    conversation: list[dict[str, Any]] = list(messages)
    trajectory: list[dict[str, Any]] = list(initial_trajectory or [])
    final_content = ""
    steps_since_compaction = max(0, int(initial_steps_since_compaction))
    first_read_skill_step: int | None = None
    max_steps_after_skill = SKILL_MAX_STEPS_AFTER_READ if skill_max_steps_after_read is None else skill_max_steps_after_read

    for step_idx in range(max_tool_steps + 1):
        step_no = len(trajectory) + 1
        force_submit_after_skill = (
            bool(extra_tools)
            and first_read_skill_step is not None
            and max_steps_after_skill >= 0
            and (step_idx + 1 - first_read_skill_step) > max_steps_after_skill
        )
        allow_tools = step_idx < max_tool_steps and not force_submit_after_skill
        if not allow_tools:
            if force_submit_after_skill:
                instruction = (
                    "You have already read a testing guide and used the allowed follow-up "
                    "tool budget. Stop exploring. Apply the guide's Fast path now and submit "
                    "one SMALL complete Java test class. Do not preserve the whole previous "
                    "suite. Include only 2-4 focused @Test methods that directly exercise the "
                    "guide's bug-revealing hypothesis. Return ONLY the Java file, starting "
                    "with package/imports and ending with the final closing brace. Do not "
                    "include analysis, markdown fences, or prose."
                )
                _append_agent_trace(trace_path, {
                    "event": "force_submit_after_skill",
                    "step": step_idx + 1,
                    "first_read_skill_step": first_read_skill_step,
                    "skill_max_steps_after_read": max_steps_after_skill,
                })
            else:
                instruction = final_instruction or (
                    "Tool budget is exhausted. Do not request or mention any more tool calls. "
                    "Now submit the generated tests. Return ONLY compact JSON with this schema: "
                    '{"class_name":"...","test_class_name":"...","test_methods":['
                    '{"test_method_name":"...","pure_test_method":"@Test\\npublic void ..."}]}. '
                    "Do not include markdown fences, explanations, or analysis."
                )
            conversation.append({
                "role": "user",
                "content": instruction,
            })
        kwargs: dict[str, Any] = {
            "model": d4j.MODEL,
            "messages": conversation,
            "temperature": 0.4,
            "max_tokens": max_tokens,
            "timeout": DEFAULT_LLM_TIMEOUT,
        }
        if allow_tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"
        if d4j.MODEL in {"deepseek-v4-flash", "deepseek-v4-pro"}:
            kwargs["extra_body"] = {"thinking": {"type": "disabled"}}
        response = _chat_completion_with_retry(client, kwargs)
        message = response.choices[0].message
        content = message.content or ""
        tool_calls = list(message.tool_calls or [])
        step_record: dict[str, Any] = {
            "step": step_no,
            "model_output": content,
            "tool_calls": [],
        }
        _append_agent_trace(trace_path, {
            "event": "llm_response",
            "step": step_no,
            "allow_tools": allow_tools,
            "model_output": content,
            "tool_call_count": len(tool_calls),
            "tool_names": [call.function.name for call in tool_calls],
        })

        if not tool_calls:
            if extra_tools and require_extra_tool_read_skill and allow_tools:
                read_skill_seen = any(
                    call.get("name") == "read_skill"
                    for step in trajectory
                    for call in (step.get("tool_calls") or [])
                )
                if not read_skill_seen:
                    step_record["blocked_missing_read_skill"] = True
                    trajectory.append(step_record)
                    _append_agent_trace(trace_path, {
                        "event": "blocked_missing_read_skill",
                        "step": step_no,
                        "step_record": step_record,
                    })
                    conversation.append({"role": "assistant", "content": content})
                    conversation.append({
                        "role": "user",
                        "content": (
                            "Testing guides are available and you have not read any full guide yet. "
                            "Before submitting the Java test class, call read_skill(name) for the most "
                            "relevant guide from list_skills(), then use it to revise your test plan."
                        ),
                    })
                    continue
            final_content = content
            conversation.append({"role": "assistant", "content": content})
            trajectory.append(step_record)
            _append_agent_trace(trace_path, {"event": "step", "step_record": step_record})
            _append_agent_trace(trace_path, {"event": "finish", "reason": "no_tool_calls", "steps": len(trajectory)})
            break

        if not allow_tools:
            final_content = content
            conversation.append({"role": "assistant", "content": content})
            trajectory.append(step_record)
            _append_agent_trace(trace_path, {"event": "step", "step_record": step_record})
            _append_agent_trace(trace_path, {"event": "finish", "reason": "tool_budget_exhausted", "steps": len(trajectory)})
            break

        assistant_msg: dict[str, Any] = {
            "role": "assistant",
            "content": content,
            "tool_calls": [],
        }
        tool_messages: list[dict[str, Any]] = []
        for call in tool_calls:
            function = call.function
            name = function.name
            try:
                args = json.loads(function.arguments or "{}")
            except Exception:
                args = {}
            if name == "read_skill" and first_read_skill_step is None:
                first_read_skill_step = step_idx + 1
            if extra_tool_executor is not None:
                obs = extra_tool_executor(name, args)
                if obs is not None:
                    observation = obs
                else:
                    observation = _execute_generation_tool(work_dir, name, args)
            else:
                observation = _execute_generation_tool(work_dir, name, args)
            assistant_msg["tool_calls"].append({
                "id": call.id,
                "type": "function",
                "function": {
                    "name": name,
                    "arguments": json.dumps(args, ensure_ascii=False),
                },
            })
            tool_messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "name": name,
                "content": observation,
            })
            step_record["tool_calls"].append({
                "id": call.id,
                "name": name,
                "arguments": args,
                "observation": observation,
            })
            _append_agent_trace(trace_path, {
                "event": "tool_call",
                "step": step_no,
                "name": name,
                "arguments": args,
                "observation": observation,
            })
        conversation.append(assistant_msg)
        conversation.extend(tool_messages)
        trajectory.append(step_record)
        _append_agent_trace(trace_path, {"event": "step", "step_record": step_record})
        steps_since_compaction += 1
        if context_compact_every > 0 and steps_since_compaction >= context_compact_every:
            base_for_compaction = compaction_base_messages if compaction_base_messages is not None else messages
            conversation = _compact_generation_conversation(
                base_for_compaction,
                trajectory,
                final_instruction=final_instruction,
            )
            step_record["context_compacted_after"] = True
            step_record["context_compact_every"] = context_compact_every
            _append_agent_trace(trace_path, {
                "event": "context_compacted",
                "step": step_no,
                "context_compact_every": context_compact_every,
            })
            steps_since_compaction = 0
    else:
        final_content = ""
        _append_agent_trace(trace_path, {"event": "finish", "reason": "loop_exhausted", "steps": len(trajectory)})

    if return_state:
        return final_content, trajectory, {
            "conversation": conversation,
            "steps_since_compaction": steps_since_compaction,
            "compaction_base_messages": compaction_base_messages if compaction_base_messages is not None else messages,
        }
    return final_content, trajectory


def _summarize_tool_trajectory_for_repair(tool_trajectory: list[dict[str, Any]], *, limit: int = 9000) -> str:
    lines: list[str] = []
    for step in tool_trajectory[-12:]:
        step_no = step.get("step", "?")
        model_output = str(step.get("model_output") or "").strip()
        if model_output:
            lines.append(f"Step {step_no} model note:\n{model_output[:900]}")
        for call in list(step.get("tool_calls") or [])[:4]:
            name = call.get("name", "")
            args = call.get("arguments", {})
            observation = str(call.get("observation") or "").strip()
            lines.append(f"Step {step_no} tool {name}({args}) ->\n{observation[:900]}")
    text = "\n\n".join(lines)
    if len(text) > limit:
        return text[-limit:]
    return text


def _build_generation_context_compaction_summary(
    trajectory: list[dict[str, Any]],
    *,
    final_instruction: str | None,
    limit: int = 12000,
) -> str:
    """Build a deterministic compact memory for long generated-suite tool sessions."""
    lines: list[str] = [
        "Context compaction summary for the Test Generator.",
        "Continue from this summary; do not repeat broad exploration unless a specific API fact is missing.",
        "The original task still applies: generate fixed-version-correct JUnit4 tests.",
    ]
    if final_instruction:
        lines.append("Final submission instruction remains active when tool budget ends.")
    for step in trajectory[-40:]:
        step_no = step.get("step", "?")
        model_output = str(step.get("model_output") or "").strip()
        if model_output:
            compact_note = re.sub(r"\s+", " ", model_output)[:700]
            lines.append(f"- Step {step_no} note: {compact_note}")
        for call in list(step.get("tool_calls") or [])[:5]:
            name = str(call.get("name") or "")
            args = call.get("arguments", {})
            observation = str(call.get("observation") or "").strip()
            observation = re.sub(r"\s+", " ", observation)[:900]
            lines.append(f"- Step {step_no} {name}({args}): {observation}")
    text = "\n".join(lines)
    if len(text) > limit:
        return text[-limit:]
    return text


def _compact_generation_conversation(
    base_messages: list[dict[str, Any]],
    trajectory: list[dict[str, Any]],
    *,
    final_instruction: str | None,
) -> list[dict[str, Any]]:
    summary = _build_generation_context_compaction_summary(
        trajectory,
        final_instruction=final_instruction,
    )
    return list(base_messages) + [
        {
            "role": "user",
            "content": (
                "The previous tool-call context has been compacted to prevent context overflow.\n\n"
                f"{summary}"
            ),
        }
    ]


def repair_generation_submission(
    record: dict[str, Any],
    *,
    fixed_dir: str,
    previous_response: str,
    tool_trajectory: list[dict[str, Any]],
    test_class_name: str,
    test_package: str,
    methods_per_class: int,
    repair_round: int,
    repair_tool_steps: int,
    generation_max_tokens: int,
) -> dict[str, Any]:
    """Repair a non-parseable generation response into JSON test methods."""
    if repair_tool_steps <= 0:
        system = (
            "You are a Test Generator submission repair model. "
            "You cannot call tools or inspect files. Use only the prompt context, "
            "the previous response, and the provided trajectory summary to produce "
            "valid JUnit4 test-method JSON."
        )
        api_rule = (
            "- You cannot inspect additional files or call tools. Do not mention tool use. "
            "If uncertain, prefer simpler public APIs and conservative assertions."
        )
        observations_label = "Previous model notes"
    else:
        system = (
            "You are a Test Generator submission repair agent. The prior agent already inspected "
            "the fixed checkout, but you may inspect the same fixed-version checkout with tools "
            "to verify APIs before producing valid JUnit4 test-method JSON."
        )
        api_rule = "- Use tools if constructor signatures, visibility, constants, helper APIs, or existing test patterns are uncertain."
        observations_label = "Recent tool observations and model notes"
    user = f"""
The previous Test Generator response could not be parsed into JUnit test methods.
Create a valid final submission from the existing analysis.

Focal class: {record.get('class_name') or record.get('focal_class') or ''}
Focal method: {record.get('method_name') or record.get('focal_method') or ''}
Generated test class name: {test_class_name}
Target test package: {test_package}
Desired number of methods: {methods_per_class}
Repair round: {repair_round}

Rules:
- Return ONLY compact JSON, no markdown fences.
- Use this exact top-level schema:
  {{"class_name":"...","test_class_name":"{test_class_name}","test_methods":[{{"test_method_name":"...","pure_test_method":"@Test\\npublic void ..."}}]}}
- Each pure_test_method must be a complete JUnit4 test method, not a whole class.
- Use Java 8 and JUnit 4 only; no assertThrows.
- Fixed-version correctness is mandatory. If uncertain, prefer simpler assertions or fewer methods over invalid code.
- Do not invent inaccessible constructors or non-public APIs. Use reflection only when needed.
{api_rule}

{observations_label}:
```
{_summarize_tool_trajectory_for_repair(tool_trajectory)}
```

Previous unparseable response:
```
{str(previous_response or '')[:9000]}
```
"""
    content, repair_tool_trajectory = _call_generation_agent(
        [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        work_dir=fixed_dir,
        max_tool_steps=repair_tool_steps,
        max_tokens=generation_max_tokens,
        final_instruction=(
            "Tool budget is exhausted. Do not request or mention any more tool calls. "
            "Now submit repaired generated tests. Return ONLY compact JSON with this schema: "
            '{"class_name":"...","test_class_name":"...","test_methods":['
            '{"test_method_name":"...","pure_test_method":"@Test\\npublic void ..."}]}. '
            "Do not include markdown fences, explanations, or analysis."
        ),
    )
    methods = _extract_test_methods_from_response(content)
    if not methods:
        return {
            "ok": False,
            "error": "Generation repair response did not contain test methods",
            "raw_response": content[:4000],
            "raw_response_full": content,
            "tool_trajectory": repair_tool_trajectory,
        }
    return {
        "ok": True,
        "methods": methods,
        "raw_response": content[:4000],
        "raw_response_full": content,
        "tool_trajectory": repair_tool_trajectory,
    }


def _read_java_text(path: str) -> str:
    try:
        return Path(path).read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def _find_method_source_span(source: str, method_name: str) -> tuple[int, int] | None:
    """Best-effort Java method span extraction for prompt construction."""
    if not source or not method_name:
        return None
    method_escaped = re.escape(method_name)
    header_pat = re.compile(
        rf"(?m)^[ \t]*(?:@[^\n]*\n[ \t]*)*"
        rf"(?:(?:public|protected|private|static|final|synchronized|native|abstract|strictfp|default)\s+)*"
        rf"[\w$<>\[\]., ?&]+\s+{method_escaped}\s*\(",
    )
    for match in header_pat.finditer(source):
        search_end = min(len(source), match.end() + 4000)
        brace = source.find("{", match.end(), search_end)
        semi = source.find(";", match.end(), search_end)
        if semi >= 0 and (brace < 0 or semi < brace):
            line_end = source.find("\n", semi)
            return match.start(), len(source) if line_end < 0 else line_end
        if brace < 0:
            continue
        depth = 0
        for pos in range(brace, len(source)):
            ch = source[pos]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return match.start(), pos + 1
    # Fallback: center a window on any textual occurrence of methodName(.
    call = re.search(rf"\b{method_escaped}\s*\(", source)
    if not call:
        return None
    return max(0, call.start() - 2500), min(len(source), call.end() + 2500)


def _java_header_for_prompt(source: str) -> str:
    lines: list[str] = []
    for line in source.splitlines():
        if re.match(r"\s*(?:package|import)\b", line):
            lines.append(line)
    return "\n".join(lines).strip()


def _focused_focal_source_for_prompt(source: str, method_name: str, max_chars: int) -> str:
    """Return a prompt-sized source view that preserves the focal method when possible."""
    if len(source) <= max_chars:
        return source
    span = _find_method_source_span(source, method_name)
    if not span:
        return source[:max_chars] + f"\n... [source truncated, total {len(source)} chars]"

    header = _java_header_for_prompt(source)
    start, end = span
    context_each_side = 1800
    snippet_start = max(0, start - context_each_side)
    snippet_end = min(len(source), end + context_each_side)
    snippet = source[snippet_start:snippet_end].strip()

    pieces: list[str] = []
    if header:
        pieces.append(header)
    if snippet_start > 0:
        pieces.append("/* ... earlier source omitted; focal-method-centered view ... */")
    pieces.append(snippet)
    if snippet_end < len(source):
        pieces.append("/* ... later source omitted ... */")
    focused = "\n\n".join(pieces)
    if len(focused) <= max_chars:
        return focused

    budget = max(1000, max_chars - len(header) - 260)
    method_block = source[start:end].strip()
    if len(method_block) > budget:
        method_block = (
            method_block[:budget]
            + f"\n/* ... focal method truncated, method chars {end - start}; total source chars {len(source)} ... */"
        )
    pieces = []
    if header:
        pieces.append(header)
    pieces.append("/* ... source omitted; focal method follows ... */")
    pieces.append(method_block)
    focused = "\n\n".join(pieces)
    if len(focused) > max_chars:
        focused = focused[:max_chars] + f"\n... [focused source truncated, total {len(focused)} chars]"
    return focused


def _focal_file_and_source(
    fixed_dir: str,
    record: dict[str, Any],
    max_chars: int,
    *,
    focus_method: bool = False,
) -> tuple[str, str]:
    focal_file = d4j._find_focal_file_in_checkout(fixed_dir, record)
    if not focal_file:
        candidates: list[Path] = []
        raw_file = str(record.get("file_path") or record.get("focal_file") or "").replace("\\", "/").lstrip("./")
        hint = d4j._focal_source_hint(record)
        source_roots = [
            d4j.d4j_export(fixed_dir, "dir.src.classes"),
            "src/main/java",
            "src/java",
            "source",
            "src",
            "",
        ]
        for rel in [raw_file, hint]:
            if not rel or rel.startswith("("):
                continue
            candidates.append(Path(fixed_dir) / rel)
            stripped = re.sub(r"^(src/main/java|src/java|source|src)/", "", rel)
            for root in source_roots:
                if root:
                    candidates.append(Path(fixed_dir) / root / stripped)
        class_name = str(record.get("class_name") or record.get("focal_class") or "").replace("$", ".")
        if class_name:
            parts = [part for part in class_name.split(".") if part]
            if len(parts) >= 2 and parts[-1][:1].isupper() and parts[-2][:1].isupper():
                outer_simple = parts[-2]
            else:
                outer_simple = parts[-1] if parts else ""
            for root, _dirs, files in os.walk(fixed_dir):
                if ".git" in root.split(os.sep):
                    continue
                if f"{outer_simple}.java" in files:
                    candidates.append(Path(root) / f"{outer_simple}.java")
                    break
        seen: set[str] = set()
        for candidate in candidates:
            key = str(candidate)
            if key in seen:
                continue
            seen.add(key)
            if candidate.exists():
                focal_file = key
                break
    if not focal_file:
        return "", ""
    if focus_method:
        method_name = d4j._method_name_from_signature(
            str(record.get("method_name") or record.get("focal_method") or "")
        )
        text = _focused_focal_source_for_prompt(_read_java_text(focal_file), method_name, max_chars)
    else:
        text = d4j._read_text_limited(focal_file, max_chars)
    return focal_file, text


def _write_fixed_output_diagnostics(fixed_dir: str, output: str) -> str:
    path = Path(fixed_dir) / ".generated_suite_fixed_output_latest.txt"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(output or "", encoding="utf-8", errors="replace")
    return path.name


def _extract_fixed_failure_summary(output: str, *, limit: int = 5000) -> str:
    """Extract javac/failing-test details from Defects4J output for repair prompts."""
    lines = (output or "").splitlines()
    selected: list[str] = []
    for idx, line in enumerate(lines):
        low = line.lower()
        interesting = (
            "error:" in low
            or "cannot find symbol" in low
            or "does not exist" in low
            or "not public" in low
            or "cannot be accessed" in low
            or "no suitable" in low
            or "incompatible types" in low
            or "method " in low and "cannot be applied" in low
            or line.startswith("--- ")
            or "detailed failing_tests" in low
        )
        if not interesting:
            continue
        start = max(0, idx - 2)
        end = min(len(lines), idx + 6)
        for item in lines[start:end]:
            if item not in selected:
                selected.append(item)
    if not selected:
        tail = "\n".join(lines[-60:])
        return tail[-limit:]
    text = "\n".join(selected)
    if len(text) > limit:
        return text[-limit:]
    return text


def generate_initial_test_class(
    record: dict[str, Any],
    fixed_dir: str,
    *,
    focal_idx: int,
    methods_per_class: int,
    package_mode: str,
    max_source_chars: int,
    tool_steps: int,
    generation_max_tokens: int,
    generation_repair_rounds: int = DEFAULT_GENERATION_REPAIR_ROUNDS,
) -> dict[str, Any]:
    focal_file, source = _focal_file_and_source(
        fixed_dir,
        record,
        max_source_chars,
        focus_method=(tool_steps <= 0),
    )
    if not source:
        return {"ok": False, "error": "Could not locate/read focal source file", "test_code": ""}

    focal_package = _extract_java_package(source)
    source_imports = _extract_java_imports(source)
    test_package = _test_package_for(focal_package, package_mode)
    test_class_name = _build_test_class_name(record, focal_idx)
    method_name = d4j._method_name_from_signature(str(record.get("method_name") or record.get("focal_method") or ""))
    focal_sig = str(record.get("focal_method") or record.get("focal_method_sig") or record.get("method_name") or "")

    if tool_steps <= 0:
        system = (
            "You are a Test Generator for Defects4J. "
            "Generate JUnit4 test methods that compile on the fixed version and cover many edge cases. "
            "You cannot call tools or inspect additional files. "
            "Return only JSON."
        )
        context_rule = (
            "- You cannot call tools, inspect files, grep code, or read existing tests. "
            "Use only the focal method/source shown in this prompt."
        )
        api_rule = (
            "- Do not rely on unavailable project details. Prefer public APIs visible from the focal source, "
            "standard Java/JUnit APIs, conservative assertions, and simple fixtures."
        )
    else:
        system = (
            "You are a Test Generator for Defects4J. "
            "Generate JUnit4 test methods that compile on the fixed version and cover many edge cases. "
            "You may inspect the fixed-version checkout with tools before generating tests. "
            "Return only JSON when you are ready to submit."
        )
        context_rule = (
            "- Before writing tests, use tools when needed to verify exact constructors, method signatures, "
            "visibility, helper APIs, constants, and existing class behavior."
        )
        api_rule = (
            "- Prefer reading production source and build files. Do not rely on memory for non-public constructors, "
            "abstract method signatures, protected/package-private members, or complex stubs."
        )
    user = f"""
Generate a JUnit4 test class plan for this Defects4J fixed-version source.

Focal class: {record.get('class_name') or record.get('focal_class') or ''}
Focal method: {method_name}
Focal signature: {focal_sig}
Generated test class name: {test_class_name}
Target test package: {test_package}

Rules:
- Produce {methods_per_class} distinct @Test methods when possible.
- Use Java 8 and JUnit 4 only. Do not use JUnit 5 APIs such as assertThrows.
- Mockito 3 and java.lang.reflect are allowed.
- Prefer a broad suite: normal cases, boundary cases, null/error cases, state transitions, equality/hash/clone/serialization-style contracts when relevant.
- Fixed-version correctness is mandatory. Assertions must follow the fixed source or API contract.
- Each test method must be self-contained: declare local variables inside the method.
{context_rule}
{api_rule}
- Return compact JSON with this schema:
  {{"class_name":"...","test_class_name":"{test_class_name}","test_methods":[{{"test_method_name":"...","pure_test_method":"@Test\\npublic void ..."}}]}}

Fixed-version focal source file: {os.path.relpath(focal_file, fixed_dir)}
```java
{source}
```
"""
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    content, tool_trajectory = _call_generation_agent(
        messages,
        work_dir=fixed_dir,
        max_tool_steps=tool_steps,
        max_tokens=generation_max_tokens,
    )
    methods = _extract_test_methods_from_response(content)
    generation_repair_attempts: list[dict[str, Any]] = []
    final_content = content
    for repair_round in range(1, generation_repair_rounds + 1):
        if methods:
            break
        repaired_generation = repair_generation_submission(
            record,
            fixed_dir=fixed_dir,
            previous_response=final_content,
            tool_trajectory=tool_trajectory,
            test_class_name=test_class_name,
            test_package=test_package,
            methods_per_class=methods_per_class,
            repair_round=repair_round,
            repair_tool_steps=tool_steps,
            generation_max_tokens=generation_max_tokens,
        )
        generation_repair_attempts.append({
            "round": repair_round,
            "ok": bool(repaired_generation.get("ok")),
            "error": repaired_generation.get("error", ""),
            "raw_response": str(repaired_generation.get("raw_response") or "")[:4000],
            "tool_trajectory": repaired_generation.get("tool_trajectory", []),
        })
        final_content = str(repaired_generation.get("raw_response_full") or "")
        if repaired_generation.get("ok"):
            methods = list(repaired_generation.get("methods") or [])
    if not methods:
        return {
            "ok": False,
            "error": "LLM response did not contain test methods",
            "raw_response": content[:4000],
            "raw_response_full": content,
            "final_raw_response_full": final_content,
            "tool_trajectory": tool_trajectory,
            "generation_repair_rounds_used": len(generation_repair_attempts),
            "generation_repair_attempts": generation_repair_attempts,
            "test_code": "",
        }
    test_code = assemble_generated_suite_class(
        test_class_name=test_class_name,
        test_package=test_package,
        focal_package=focal_package,
        source_imports=source_imports,
        test_methods=methods,
    )
    return {
        "ok": True,
        "error": "",
        "raw_response": content[:4000],
        "raw_response_full": content,
        "final_raw_response_full": final_content,
        "tool_trajectory": tool_trajectory,
        "generation_repair_rounds_used": len(generation_repair_attempts),
        "generation_repair_attempts": generation_repair_attempts,
        "test_code": test_code,
        "test_class_name": test_class_name,
        "test_package": test_package,
        "full_test_class": f"{test_package}.{test_class_name}" if test_package else test_class_name,
        "num_methods": len(methods),
        "focal_file": os.path.relpath(focal_file, fixed_dir),
    }


def repair_test_class(
    record: dict[str, Any],
    current_code: str,
    fixed_output: str,
    *,
    fixed_dir: str,
    test_class_name: str,
    test_package: str,
    repair_tool_steps: int,
    extra_tools: list[dict[str, Any]] | None = None,
    extra_tool_executor: Any = None,
    extra_tool_hint: str = "",
    require_extra_tool_read_skill: bool = True,
    skill_max_steps_after_read: int | None = None,
    framework_rule: str = "",
    session_messages: list[dict[str, Any]] | None = None,
    session_base_messages: list[dict[str, Any]] | None = None,
    session_trajectory: list[dict[str, Any]] | None = None,
    session_steps_since_compaction: int = 0,
    repair_max_tokens: int = 4096,
) -> dict[str, Any]:
    diagnostic_file = _write_fixed_output_diagnostics(fixed_dir, fixed_output)
    failure_summary = _extract_fixed_failure_summary(fixed_output)
    framework_rule = framework_rule or "Keep JUnit4, Java 8, and fixed-version correctness."
    system = (
        "You are a test repair agent. Fix a generated Java test class so it compiles "
        "and passes on the fixed version. Return only one complete Java file. "
        "Treat javac diagnostics as ground truth: if the error reports a required method "
        "signature, copy that exact signature instead of relying on memory. "
        "You may inspect the fixed-version checkout with tools before submitting the repair."
    )
    user = f"""
The generated test class failed on the fixed version. Repair it without changing the production code.

Focal class: {record.get('class_name') or record.get('focal_class') or ''}
Test class: {test_package}.{test_class_name}

Repair priorities:
1. Fix every javac error shown below exactly.
2. For anonymous subclasses, match the exact abstract method signatures reported by javac.
3. Add missing imports when the current test uses helper classes.
4. Remove or simplify tests that cannot be made fixed-version correct.
5. Keep the same package and public class name.
6. Use tools to verify constructors, visibility, helper APIs, existing tests, and exact assertion behavior when needed.
7. If javac reports an import/package/class does not exist and the test does not need it, remove that import.
8. {framework_rule}
{extra_tool_hint}

High-signal fixed-version failure summary:
```
{failure_summary}
```

Full fixed-version output was saved in the checkout as:
{diagnostic_file}
Use read_file("{diagnostic_file}") if the summary is insufficient.

Fixed-version compiler/test output:
```
{fixed_output[:12000]}
```

Current test class:
```java
{current_code[:18000]}
```

Return the complete corrected Java test class. {framework_rule}
"""
    if session_messages:
        messages = list(session_messages) + [
            {
                "role": "user",
                "content": (
                    "Repair phase: the submitted test class failed on the fixed version. "
                    "Continue this same session and repair the test class using the diagnostics below.\n\n"
                    + user
                ),
            }
        ]
        compaction_base = session_base_messages
    else:
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]
        compaction_base = None
    content, repair_tool_trajectory, session_state = _call_generation_agent(
        messages,
        work_dir=fixed_dir,
        max_tool_steps=repair_tool_steps,
        max_tokens=repair_max_tokens,
        final_instruction=(
            "Tool budget is exhausted. Do not request or mention any more tool calls. "
            "Now submit the repaired test class. Return ONLY one complete Java file, starting "
            "with its package/imports and ending with the final closing brace. "
            "Do not include explanations, markdown fences, analysis, or prose."
        ),
        extra_tools=extra_tools,
        extra_tool_executor=extra_tool_executor,
        require_extra_tool_read_skill=require_extra_tool_read_skill,
        skill_max_steps_after_read=skill_max_steps_after_read,
        initial_trajectory=session_trajectory,
        initial_steps_since_compaction=session_steps_since_compaction,
        compaction_base_messages=compaction_base,
        return_state=True,
    )
    repaired = _extract_java_file_from_response(content)
    if not _looks_like_complete_java_test_class(repaired):
        repaired_methods = _extract_test_methods_from_response(content)
        if repaired_methods:
            repaired = _assemble_repaired_class_from_methods(
                current_code,
                test_class_name=test_class_name,
                test_package=test_package,
                methods=repaired_methods,
            )
    if not _looks_like_complete_java_test_class(repaired):
        return {
            "ok": False,
            "error": "Repair response did not contain a complete test class",
            "raw_response": content[:4000],
            "tool_trajectory": repair_tool_trajectory,
            "_session_state": session_state,
        }
    return {
        "ok": True,
        "test_code": repaired,
        "raw_response": content[:4000],
        "tool_trajectory": repair_tool_trajectory,
        "_session_state": session_state,
    }


def expand_pass_both_test_class(
    record: dict[str, Any],
    current_code: str,
    *,
    fixed_dir: str,
    test_class_name: str,
    test_package: str,
    repair_tool_steps: int,
    retry_round: int,
    skill_bank: dict[str, Any] | None = None,
    tier_skill_names: list[str] | None = None,
    trace_path: str | None = None,
    target_tier: str = "PASS_BOTH",
) -> dict[str, Any]:
    """Generate a same-run continuation test class for any non-detected tier."""
    extra_tools, extra_tool_executor, matched_tags = _skill_tools_for_record(
        fixed_dir=fixed_dir,
        record=record,
        skill_bank=skill_bank,
        log_label=f"continuation attempt {retry_round}",
        target_tier=target_tier,
        precomputed_tier_skill_names=tier_skill_names,
    )

    target_tier = str(target_tier or "PASS_BOTH").upper()
    if target_tier == "COMPILE_FAIL":
        system = (
            "You are a Test Generator continuation agent. The previous generated suite "
            "failed to compile on the fixed version. Use only fixed-version code/context. "
            "Repair or replace the test class so it is syntactically complete, uses APIs "
            "visible from the generated test package, and compiles under the project's "
            "Java/JUnit version. Once it compiles and respects the fixed-version contract, "
            "try to make it discriminating."
        )
        tier_feedback = """
The current generated test suite did not compile on the fixed version, so it cannot be used to detect a real bug yet.
Write a new complete Java test class that compiles on the fixed checkout first, then tries to expose a buggy-version-only failure.

Use the javac diagnostics, previous repair attempts, and fixed-version source as feedback about what was wrong. Prefer a shorter, cleaner test class over preserving long broken code.
"""
        code_label = "Current compile-failing test class"
    elif target_tier == "FAIL_ON_FIXED":
        system = (
            "You are a Test Generator continuation agent. The previous generated suite "
            "failed on the fixed version, so its assertion, fixture, API use, or oracle "
            "was invalid for the fixed code. Use only fixed-version code/context. Replace "
            "or repair invalid tests, then add discriminating scenarios that still respect "
            "the fixed-version contract."
        )
        tier_feedback = """
The current generated test suite failed on the fixed version, so it cannot be used to detect a real bug yet.
Write a new complete Java test class that first satisfies the fixed-version API contract and then tries to expose a buggy-version-only failure.

Do not preserve invalid assertions merely because they were in the previous suite. Treat the fixed failure output and repair attempts as feedback about what was wrong with the previous tests.
"""
        code_label = "Current fixed-failing test class"
    else:
        system = (
            "You are a Test Generator continuation agent. The previous generated suite "
            "compiled and passed on the fixed version but did not expose the bug. "
            "Use only fixed-version code/context. Add or replace tests with different, "
            "more discriminating scenarios while keeping the suite fixed-version correct."
        )
        tier_feedback = """
The current generated test suite passed on both fixed and buggy versions, so it did not detect the bug.
Write a new complete Java test class that keeps fixed-version correctness but explores different bug-revealing scenarios.
"""
        code_label = "Current fixed-passing but non-detecting test class"

    if extra_tools:
        skill_hint = (
            "Testing guides (skills) are available for this focal method type. "
            "You may call list_skills() and read_skill(name) to inspect one or more "
            "concrete guides that look relevant. Treat skills as optional references, "
            "not as requirements: fixed-version source, compiler diagnostics, and test "
            "results remain authoritative. If a guide is relevant, use it to target a "
            "different failure mode or repair direction; otherwise continue from the code."
        )
    else:
        skill_hint = ""

    user = f"""
{tier_feedback}
Focal class: {record.get('class_name') or record.get('focal_class') or ''}
Focal method: {record.get('method_name') or record.get('focal_method') or ''}
Test class: {test_package}.{test_class_name}
Retry round: {retry_round}
Original target tier: {target_tier}

Rules:
- Return one complete Java file with the same package and public class name.
- Prefer a small focused retry suite over a large broad suite. You may replace the previous tests.
- Include only the old tests that are directly needed for the new bug-revealing hypothesis; otherwise write 2-4 focused new @Test methods.
- Consider alternative boundary cases, object states, parser/control-flow paths, nested structures, error paths, locale/encoding/order/state interactions, and API contracts suggested by the fixed code.
- The suite must still pass on the fixed version. Do not assert behavior that contradicts the fixed source/API contract.
- If the previous suite failed on fixed or failed to compile, diagnose and avoid that invalid oracle/API/fixture/import/visibility pattern before trying new bug-revealing scenarios.
- For compile failures, do not emit markdown fences, prose, ellipses, or partial files. Avoid Java features unsupported by the project source level, qualify ambiguous class names, and do not call package-private APIs from a different package.
- Use tools to inspect fixed-version source, existing tests, constructors, visibility, and helper APIs.
- Do not mention or request buggy-version details.
{skill_hint}
{code_label}:
```java
{current_code[:22000]}
```
"""
    content, tool_trajectory = _call_generation_agent(
        [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        work_dir=fixed_dir,
        max_tool_steps=repair_tool_steps,
        max_tokens=4096,
        final_instruction=(
            "Tool budget is exhausted. Do not request or mention any more tool calls. "
            "Now submit the expanded test class. Return ONLY one complete Java file, "
            "starting with its package/imports and ending with the final closing brace. "
            "Do not include explanations, markdown fences, analysis, or prose."
        ),
        extra_tools=extra_tools,
        extra_tool_executor=extra_tool_executor,
        require_extra_tool_read_skill=False,
        skill_max_steps_after_read=-1,
        trace_path=trace_path,
    )
    expanded = _extract_java_file_from_response(content)
    if "class " not in expanded or "@Test" not in expanded:
        return {
            "ok": False,
            "error": "Continuation response did not contain a complete test class",
            "raw_response": content[:4000],
            "tool_trajectory": tool_trajectory,
            "matched_tags": matched_tags,
        }
    return {
        "ok": True,
        "test_code": expanded,
        "raw_response": content[:4000],
        "tool_trajectory": tool_trajectory,
        "matched_tags": matched_tags,
    }


def _write_generated_test(fixed_dir: str, test_code: str, full_test_class: str) -> str:
    package = full_test_class.rsplit(".", 1)[0] if "." in full_test_class else ""
    simple = full_test_class.rsplit(".", 1)[-1]
    test_root = d4j._find_test_source_root(fixed_dir)
    out_dir = Path(test_root) / package.replace(".", os.sep)
    out_dir.mkdir(parents=True, exist_ok=True)
    test_file = out_dir / f"{simple}.java"
    test_file.write_text(test_code, encoding="utf-8")
    return str(test_file)


def _ensure_d4j_testgen_runtime_classpath() -> None:
    """Make D4J's generated-test runtime classpath include JUnit4+Hamcrest.

    Some Defects4J projects (for example older Cli bugs) use JUnit 3 in the
    project build. The generated-suite Ant target runs JUnit4 tests, but the
    forked runner can still miss Hamcrest unless it is also present in the
    test-generation runtime path. The target already includes ``*-rt.jar`` from
    ``framework/lib/test_generation/runtime``, so a stable symlink/copy there
    fixes the classpath without modifying project checkouts.
    """
    global _D4J_TESTGEN_RUNTIME_READY
    if _D4J_TESTGEN_RUNTIME_READY:
        return
    source = d4j.D4J_HOME / "framework" / "projects" / "lib" / "junit-4.12-hamcrest-1.3.jar"
    runtime_dir = d4j.D4J_HOME / "framework" / "lib" / "test_generation" / "runtime"
    target = runtime_dir / "junit-4.12-hamcrest-1.3-rt.jar"
    try:
        if source.exists():
            runtime_dir.mkdir(parents=True, exist_ok=True)
            if not target.exists():
                try:
                    target.symlink_to(source)
                except Exception:
                    shutil.copy2(source, target)
        _D4J_TESTGEN_RUNTIME_READY = True
    except Exception as exc:
        print(f"[WARN] Could not prepare D4J generated-test runtime classpath: {exc}", flush=True)


def _run_d4j_suite(work_dir: str, archive_path: str, timeout: int) -> tuple[bool, int | None, str]:
    _ensure_d4j_testgen_runtime_classpath()
    rc, stdout, stderr = d4j._d4j("test", "-w", work_dir, "-s", archive_path, timeout=timeout)
    output = (stdout + "\n" + stderr).strip()
    failing_tests = Path(work_dir) / "failing_tests"
    if failing_tests.exists():
        details = failing_tests.read_text(encoding="utf-8", errors="replace").strip()
        if details:
            output = f"{output}\n\nDetailed failing_tests:\n{details}"
    match = re.search(r"Failing tests:\s*(\d+)", output)
    if match:
        failures = int(match.group(1))
        return failures == 0, failures, output
    return False, None, output


def _ensure_fixed_passing_suite(
    *,
    result: dict[str, Any],
    record: dict[str, Any],
    fixed_dir: str,
    current_code: str,
    full_test_class: str,
    archive_path: Path,
    repair_rounds: int,
    repair_tool_steps: int,
    test_timeout: int,
    attempt_kind: str,
    repair_extra_tools: list[dict[str, Any]] | None = None,
    repair_extra_tool_executor: Any = None,
    repair_extra_tool_hint: str = "",
    repair_require_extra_tool_read_skill: bool = True,
    repair_skill_max_steps_after_read: int | None = None,
    session_messages: list[dict[str, Any]] | None = None,
    session_base_messages: list[dict[str, Any]] | None = None,
    session_trajectory: list[dict[str, Any]] | None = None,
    session_steps_since_compaction: int = 0,
) -> tuple[str, bool, str]:
    test_package = full_test_class.rsplit(".", 1)[0] if "." in full_test_class else ""
    test_class_name = full_test_class.rsplit(".", 1)[-1]
    fixed_output = ""
    llm_repairs_used = 0
    compile_attempt = 0
    current_session_messages = session_messages
    current_session_base_messages = session_base_messages
    current_session_trajectory = session_trajectory
    current_session_steps_since_compaction = session_steps_since_compaction

    while True:
        compile_attempt += 1
        test_file = _write_generated_test(fixed_dir, current_code, full_test_class)
        result["generated_test_file"] = test_file
        d4j.pack_generated_suite(fixed_dir, [test_file], str(archive_path))
        result["suite_archive"] = str(archive_path)
        fixed_ok, fixed_failures, fixed_output = _run_d4j_suite(fixed_dir, str(archive_path), test_timeout)
        result["fixed_output"] = fixed_output[:12000]
        result["fixed_failure_summary"] = _extract_fixed_failure_summary(fixed_output)
        result["fixed_diagnostic_file"] = _write_fixed_output_diagnostics(fixed_dir, fixed_output)
        result["fixed_failures"] = fixed_failures
        result["fixed_passed"] = fixed_ok
        if fixed_ok:
            return current_code, True, fixed_output

        cleaned_code, cleanup_notes = _prune_generated_imports(current_code, fixed_output)
        if cleanup_notes and cleaned_code != current_code:
            current_code = cleaned_code
            result["deterministic_repair_attempts"].append({
                "kind": attempt_kind,
                "compile_attempt": compile_attempt,
                "notes": cleanup_notes,
                "fixed_failure_summary": result["fixed_failure_summary"],
            })
            continue

        p0_code, p0_notes = apply_p0_postprocess(current_code, fixed_output)
        if p0_notes and p0_code != current_code:
            current_code = p0_code
            result["deterministic_repair_attempts"].append({
                "kind": f"{attempt_kind}_p0",
                "compile_attempt": compile_attempt,
                "notes": p0_notes,
                "fixed_failure_summary": result["fixed_failure_summary"],
            })
            continue

        if llm_repairs_used >= repair_rounds:
            return current_code, False, fixed_output
        repaired = repair_test_class(
            record,
            current_code,
            fixed_output,
            fixed_dir=fixed_dir,
            test_class_name=test_class_name,
            test_package=test_package,
            repair_tool_steps=repair_tool_steps,
            extra_tools=repair_extra_tools,
            extra_tool_executor=repair_extra_tool_executor,
            extra_tool_hint=repair_extra_tool_hint,
            require_extra_tool_read_skill=repair_require_extra_tool_read_skill,
            skill_max_steps_after_read=repair_skill_max_steps_after_read,
            session_messages=current_session_messages,
            session_base_messages=current_session_base_messages,
            session_trajectory=current_session_trajectory,
            session_steps_since_compaction=current_session_steps_since_compaction,
        )
        repaired_session_state = repaired.get("_session_state") or {}
        if isinstance(repaired_session_state, dict):
            current_session_messages = repaired_session_state.get("conversation") or current_session_messages
            current_session_base_messages = repaired_session_state.get("compaction_base_messages") or current_session_base_messages
            current_session_trajectory = repaired.get("tool_trajectory") or current_session_trajectory
            current_session_steps_since_compaction = int(
                repaired_session_state.get("steps_since_compaction") or 0
            )
            result["_session_state"] = {
                "conversation": current_session_messages,
                "compaction_base_messages": current_session_base_messages,
                "steps_since_compaction": current_session_steps_since_compaction,
            }
        if not repaired.get("ok"):
            result["repair_error"] = repaired.get("error", "")
            result["repair_attempts"].append({
                "kind": attempt_kind,
                "round": llm_repairs_used + 1,
                "ok": False,
                "error": repaired.get("error", ""),
                "raw_response": repaired.get("raw_response", "")[:4000],
                "tool_trajectory": repaired.get("tool_trajectory", []),
                "fixed_failure_summary": result["fixed_failure_summary"],
            })
            return current_code, False, fixed_output
        current_code = str(repaired.get("test_code") or current_code)
        current_code, post_cleanup_notes = _prune_generated_imports(current_code, fixed_output)
        llm_repairs_used += 1
        result["repair_rounds_used"] = int(result.get("repair_rounds_used") or 0) + 1
        result["repair_attempts"].append({
            "kind": attempt_kind,
            "round": llm_repairs_used,
            "ok": True,
            "raw_response": repaired.get("raw_response", "")[:4000],
            "tool_trajectory": repaired.get("tool_trajectory", []),
            "fixed_failure_summary": result["fixed_failure_summary"],
            "post_cleanup_notes": post_cleanup_notes,
        })


def evaluate_generated_suite(
    *,
    record: dict[str, Any],
    fixed_dir: str,
    buggy_dir: str,
    output_dir: Path,
    test_code: str,
    full_test_class: str,
    repair_rounds: int,
    repair_tool_steps: int,
    max_attempts: int,
    skill_start_attempt: int,
    test_timeout: int,
    skill_bank: dict[str, Any] | None = None,
    skill_tier_gate: bool = True,
) -> dict[str, Any]:
    tier_rank = {
        "BUG_DETECTED": 5,
        "PASS_BOTH": 4,
        "FAIL_ON_FIXED": 3,
        "COMPILE_FAIL": 2,
        "NO_TEST_GENERATED": 1,
        "UNKNOWN": 0,
    }

    def _rank(tier: str) -> int:
        return tier_rank.get(str(tier or "UNKNOWN"), 0)

    result: dict[str, Any] = {
        "tier": "UNKNOWN",
        "passed": False,
        "generated_test_class": full_test_class,
        "attempts": [],
        "max_attempts": max_attempts,
        "skill_start_attempt": skill_start_attempt,
    }
    current_code = test_code
    previous_tier = "INITIAL"

    test_package = full_test_class.rsplit(".", 1)[0] if "." in full_test_class else ""
    test_class_name = full_test_class.rsplit(".", 1)[-1]
    best_attempt: dict[str, Any] | None = None

    for attempt_no in range(1, max(1, max_attempts) + 1):
        active_skill_bank = None
        tier_skill_names: list[str] = []
        skill_gate_reason = "before_skill_start_attempt"
        if skill_bank is not None and attempt_no >= skill_start_attempt:
            allowed, tier_skill_names = _skill_bank_allowed_for_tier(
                skill_bank,
                previous_tier,
                tier_gate=skill_tier_gate,
            )
            if allowed:
                active_skill_bank = skill_bank
                skill_gate_reason = "enabled"
            else:
                skill_gate_reason = f"disabled_no_{_normalize_result_tier(previous_tier).lower()}_metadata"
        attempt: dict[str, Any] = {
            "attempt": attempt_no,
            "skill_enabled": active_skill_bank is not None,
            "skill_gate_reason": skill_gate_reason,
            "skill_tier_matches": tier_skill_names,
            "target_tier": previous_tier,
            "tier": "UNKNOWN",
            "passed": False,
            "generated_test_class": full_test_class,
            "generated_test_file": "",
            "suite_archive": "",
            "fixed_passed": False,
            "buggy_passed": False,
            "fixed_failures": None,
            "buggy_failures": None,
            "fixed_output": "",
            "fixed_failure_summary": "",
            "fixed_diagnostic_file": "",
            "buggy_output": "",
            "repair_rounds_used": 0,
            "repair_attempts": [],
            "deterministic_repair_attempts": [],
        }

        if attempt_no > 1:
            expanded = expand_pass_both_test_class(
                record,
                current_code,
                fixed_dir=fixed_dir,
                test_class_name=test_class_name,
                test_package=test_package,
                repair_tool_steps=repair_tool_steps,
                retry_round=attempt_no,
                skill_bank=active_skill_bank,
                tier_skill_names=tier_skill_names,
                target_tier=previous_tier,
            )
            attempt["continuation_generation"] = {
                "ok": bool(expanded.get("ok")),
                "error": expanded.get("error", ""),
                "raw_response": str(expanded.get("raw_response") or "")[:4000],
                "tool_trajectory": expanded.get("tool_trajectory", []),
                "matched_tags": expanded.get("matched_tags", []),
            }
            if not expanded.get("ok"):
                attempt["tier"] = "NO_TEST_GENERATED"
                attempt["feedback"] = expanded.get("error", "")
                result["attempts"].append(attempt)
                if best_attempt is None or _rank(attempt["tier"]) > _rank(best_attempt.get("tier", "UNKNOWN")):
                    best_attempt = attempt
                break
            current_code = str(expanded.get("test_code") or current_code)
            current_code, cleanup_notes = _prune_generated_imports(current_code, "")
            if cleanup_notes:
                attempt["pre_fixed_cleanup_notes"] = cleanup_notes

        archive_path = output_dir / "suites" / (
            f"{record.get('project')}-{record.get('bug_id')}-{test_class_name}-attempt{attempt_no}.tar.bz2"
        )
        repair_extra_tools = None
        repair_extra_tool_executor = None
        repair_skill_hint = ""
        repair_matched_tags: list[str] = []
        if active_skill_bank is not None:
            repair_extra_tools, repair_extra_tool_executor, repair_matched_tags = _skill_tools_for_record(
                fixed_dir=fixed_dir,
                record=record,
                skill_bank=active_skill_bank,
                log_label=f"attempt {attempt_no} repair",
                target_tier=previous_tier,
                precomputed_tier_skill_names=tier_skill_names,
            )
            if repair_extra_tools:
                repair_skill_hint = (
                    "Testing guides are available through list_skills() and read_skill(name). "
                    "Use them if they help diagnose or redirect this retry, but fixed-version "
                    "correctness and compiler diagnostics remain authoritative."
                )
        attempt["repair_matched_tags"] = repair_matched_tags

        current_code, fixed_ok, fixed_output = _ensure_fixed_passing_suite(
            result=attempt,
            record=record,
            fixed_dir=fixed_dir,
            current_code=current_code,
            full_test_class=full_test_class,
            archive_path=archive_path,
            repair_rounds=repair_rounds,
            repair_tool_steps=repair_tool_steps,
            test_timeout=test_timeout,
            attempt_kind=f"attempt_{attempt_no}",
            repair_extra_tools=repair_extra_tools,
            repair_extra_tool_executor=repair_extra_tool_executor,
            repair_extra_tool_hint=repair_skill_hint,
            repair_require_extra_tool_read_skill=False,
            repair_skill_max_steps_after_read=-1,
        )
        attempt["test_code"] = current_code

        if not attempt["fixed_passed"]:
            attempt["tier"] = "COMPILE_FAIL" if attempt["fixed_failures"] is None else "FAIL_ON_FIXED"
            attempt["feedback"] = fixed_output[:4000]
        else:
            buggy_ok, buggy_failures, buggy_output = _run_d4j_suite(buggy_dir, str(archive_path), test_timeout)
            attempt["buggy_output"] = buggy_output[:12000]
            attempt["buggy_failures"] = buggy_failures
            attempt["buggy_passed"] = buggy_ok
            if not buggy_ok:
                attempt["tier"] = "BUG_DETECTED"
                attempt["passed"] = True
                attempt["feedback"] = f"Attempt {attempt_no} produced a fixed-pass suite that failed on buggy version."
            else:
                attempt["tier"] = "PASS_BOTH"
                attempt["feedback"] = "Generated suite passed on both fixed and buggy versions."

        result["attempts"].append(attempt)
        if best_attempt is None or _rank(attempt["tier"]) > _rank(best_attempt.get("tier", "UNKNOWN")):
            best_attempt = attempt
        previous_tier = str(attempt.get("tier") or "UNKNOWN")
        if attempt["tier"] == "BUG_DETECTED":
            break

    if best_attempt is None:
        result["tier"] = "NO_TEST_GENERATED"
        result["feedback"] = "No attempts were executed."
        return result

    for key, value in best_attempt.items():
        if key not in {"attempts"}:
            result[key] = value
    result["tier"] = best_attempt.get("tier", "UNKNOWN")
    result["passed"] = best_attempt.get("tier") == "BUG_DETECTED"
    result["best_attempt"] = best_attempt.get("attempt")
    result["attempts_used"] = len(result["attempts"])
    return result


def run_single_focal(
    record: dict[str, Any],
    *,
    fixed_dir: str,
    buggy_dir: str,
    output_dir: Path,
    focal_idx: int,
    methods_per_class: int,
    package_mode: str,
    max_source_chars: int,
    tool_steps: int,
    generation_max_tokens: int,
    generation_repair_rounds: int,
    repair_rounds: int,
    max_attempts: int,
    skill_start_attempt: int,
    test_timeout: int,
    skill_bank: dict[str, Any] | None = None,
    skill_tier_gate: bool = True,
) -> dict[str, Any]:
    record = d4j._normalize_d4j_record(record)
    record_key = d4j._record_display_key(record, focal_idx)
    generated = generate_initial_test_class(
        record,
        fixed_dir,
        focal_idx=focal_idx,
        methods_per_class=methods_per_class,
        package_mode=package_mode,
        max_source_chars=max_source_chars,
        tool_steps=tool_steps,
        generation_max_tokens=generation_max_tokens,
        generation_repair_rounds=generation_repair_rounds,
    )
    result: dict[str, Any] = {
        "record_key": record_key,
        "project": record.get("project"),
        "bug_id": record.get("bug_id"),
        "class_name": record.get("class_name"),
        "method_name": record.get("method_name"),
        "generation": {k: v for k, v in generated.items() if k not in {"test_code"}},
        "final_tier": "NO_TEST_GENERATED",
    }
    if not generated.get("ok"):
        result["feedback"] = generated.get("error", "")
        return result

    verify = evaluate_generated_suite(
        record=record,
        fixed_dir=fixed_dir,
        buggy_dir=buggy_dir,
        output_dir=output_dir,
        test_code=str(generated["test_code"]),
        full_test_class=str(generated["full_test_class"]),
        repair_rounds=repair_rounds,
        repair_tool_steps=tool_steps,
        max_attempts=max_attempts,
        skill_start_attempt=skill_start_attempt,
        test_timeout=test_timeout,
        skill_bank=skill_bank,
        skill_tier_gate=skill_tier_gate,
    )
    result["verification"] = verify
    result["final_tier"] = verify.get("tier", "UNKNOWN")
    return result


def run_single_bug(
    bug_group: list[dict[str, Any]],
    *,
    output_dir: Path,
    workspace_base: Path,
    stop_on_detect: bool,
    max_focal_per_bug: int,
    methods_per_class: int,
    package_mode: str,
    max_source_chars: int,
    tool_steps: int,
    generation_max_tokens: int,
    generation_repair_rounds: int,
    repair_rounds: int,
    max_attempts: int,
    skill_start_attempt: int,
    test_timeout: int,
    skill_bank: dict[str, Any] | None = None,
    skill_tier_gate: bool = True,
) -> dict[str, Any]:
    first = d4j._normalize_d4j_record(bug_group[0])
    project = str(first["project"])
    bug_id = str(first["bug_id"])
    bug_key = f"{project}-{bug_id}"
    workspace = workspace_base / f"{project}-{bug_id}"
    fixed_dir = str(workspace / "fixed")
    buggy_dir = str(workspace / "buggy")
    result: dict[str, Any] = {
        "bug_key": bug_key,
        "project": project,
        "bug_id": bug_id,
        "focal_results": [],
        "final_tier": "UNKNOWN",
    }

    if workspace.exists():
        shutil.rmtree(workspace, ignore_errors=True)
    workspace.mkdir(parents=True, exist_ok=True)

    fixed_ok, fixed_msg = d4j.checkout_fixed(project, bug_id, fixed_dir)
    if not fixed_ok:
        result["final_tier"] = "CHECKOUT_FIXED_FAIL"
        result["feedback"] = fixed_msg
        return result
    buggy_ok, buggy_msg = d4j.checkout_buggy(project, bug_id, buggy_dir)
    if not buggy_ok:
        result["final_tier"] = "CHECKOUT_BUGGY_FAIL"
        result["feedback"] = buggy_msg
        return result

    focal_records = bug_group[:max_focal_per_bug] if max_focal_per_bug > 0 else bug_group
    for focal_idx, record in enumerate(focal_records):
        print(f"[{bug_key}] generated-suite focal {focal_idx+1}/{len(focal_records)}")
        focal_result = run_single_focal(
            record,
            fixed_dir=fixed_dir,
            buggy_dir=buggy_dir,
            output_dir=output_dir,
            focal_idx=focal_idx,
            methods_per_class=methods_per_class,
            package_mode=package_mode,
            max_source_chars=max_source_chars,
            tool_steps=tool_steps,
            generation_max_tokens=generation_max_tokens,
            generation_repair_rounds=generation_repair_rounds,
            repair_rounds=repair_rounds,
            max_attempts=max_attempts,
            skill_start_attempt=skill_start_attempt,
            skill_bank=skill_bank,
            skill_tier_gate=skill_tier_gate,
            test_timeout=test_timeout,
        )
        result["focal_results"].append(focal_result)
        print(f"[{bug_key}] focal {focal_idx}: {focal_result.get('final_tier')}")
        if stop_on_detect and focal_result.get("final_tier") == "BUG_DETECTED":
            break

    result["final_tier"] = d4j._aggregate_bug_tier(result["focal_results"])
    return result


def _select_bug_groups(args: argparse.Namespace, output_dir: Path) -> list[list[dict[str, Any]]]:
    bug_specs = list(args.bugs or [])
    if args.bug_list_file:
        bug_specs.extend(d4j.read_bug_list_file(args.bug_list_file))
    dataset = Path(args.dataset)
    if bug_specs:
        selected = d4j.select_bug_groups_by_specs(dataset, bug_specs)
    elif args.all_bugs:
        selected = d4j.select_all_bug_groups(dataset, output_dir)
    else:
        selected = d4j.select_17_bug_groups(dataset, output_dir)
    if args.skip_completed_from:
        completed = d4j.completed_bug_keys_from_paths(args.skip_completed_from)
        print(f"[INFO] Found {len(completed)} completed bugs in prior results")
        selected = d4j.filter_completed_bug_groups(selected, completed)
    if args.max_bugs > 0:
        selected = selected[: args.max_bugs]
    return d4j.apply_bug_shard(selected, num_shards=args.num_shards, shard_index=args.shard_index)


P0_IMPORTS_BY_SYMBOL = {
    "File": "java.io.File",
    "Assert": "org.junit.Assert",
    "ImmutableList": "com.google.common.collect.ImmutableList",
    "StringEscapeUtils": "org.apache.commons.lang.StringEscapeUtils",
}


def _p0_safe_token(value: Any) -> str:
    token = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(value or "")).strip("_")
    return token or "item"


def _p0_compile_text(verification: dict[str, Any]) -> str:
    parts: list[str] = []
    for key in ("fixed_output", "fixed_failure_summary", "feedback", "repair_error"):
        val = verification.get(key)
        if isinstance(val, str) and val.strip():
            parts.append(val)
    diag = verification.get("fixed_diagnostic_file")
    generated_file = str(verification.get("generated_test_file") or "")
    if diag and generated_file:
        candidate = Path(generated_file).parents[0] / str(diag)
        for parent in Path(generated_file).parents:
            p = parent / str(diag)
            if p.exists():
                candidate = p
                break
        if candidate.exists():
            parts.append(candidate.read_text(encoding="utf-8", errors="replace")[:30000])
    return "\n".join(parts)


def _p0_missing_symbols(text: str) -> set[str]:
    return {
        m.group(1).strip().strip("(")
        for m in re.finditer(r"symbol:\s+(?:class|method|variable|constructor)\s+([^\s)]+)", text or "")
    }


def _p0_insert_imports(code: str, imports: list[str]) -> tuple[str, list[str]]:
    imports = [imp for imp in imports if imp]
    if not imports:
        return code, []
    lines = code.splitlines()
    existing = {
        m.group(1)
        for line in lines
        for m in [re.match(r"\s*import\s+(?:static\s+)?([^;]+);", line)]
        if m
    }
    to_add = [imp for imp in imports if imp not in existing]
    if not to_add:
        return code, []
    insert_at = 0
    for idx, line in enumerate(lines):
        if line.startswith("package "):
            insert_at = idx + 1
        elif line.startswith("import "):
            insert_at = idx + 1
    new_lines = lines[:insert_at] + [f"import {imp};" for imp in to_add] + lines[insert_at:]
    return "\n".join(new_lines) + ("\n" if code.endswith("\n") else ""), [f"add import {imp}" for imp in to_add]


def _p0_strip_natural_language_pollution(code: str) -> tuple[str, list[str]]:
    raw = code or ""
    suspicious = (
        "```" in raw
        or "Let me provide" in raw
        or "Here is" in raw
        or any(
            line.strip().startswith("import ")
            and not re.match(r"import\s+(?:static\s+)?[\w.*]+(?:\.[\w*]+)*;", line.strip())
            for line in raw.splitlines()
        )
        or any(
            re.match(r"\s*import\s+(?:static\s+)?[\w.*]+(?:\.[\w*]+)*;.+", line)
            for line in raw.splitlines()
        )
    )
    if not suspicious:
        return code, []
    extracted = _extract_java_file_from_response(code)
    lines: list[str] = []
    notes: list[str] = []
    for line in extracted.splitlines():
        stripped = line.strip()
        if stripped.startswith("import ") and not re.match(r"import\s+(?:static\s+)?[\w.*]+(?:\.[\w*]+)*;", stripped):
            notes.append(f"drop malformed import/prose line: {stripped[:80]}")
            continue
        m = re.match(r"(\s*import\s+(?:static\s+)?[\w.*]+(?:\.[\w*]+)*;).+", line)
        if m:
            lines.append(m.group(1))
            notes.append("trim prose after import semicolon")
            continue
        if stripped.startswith("```") or stripped in {"java", "Here is the fixed version:"}:
            notes.append(f"drop prose/fence line: {stripped[:80]}")
            continue
        lines.append(line)
    cleaned = "\n".join(lines).strip() + "\n"
    if cleaned.strip() != code.strip():
        notes.append("extract Java file body")
    return cleaned, notes


def _p0_fix_ambiguous_closure_compiler(code: str, text: str) -> tuple[str, list[str]]:
    if "reference to Compiler is ambiguous" not in text:
        return code, []
    new = re.sub(r"\bCompiler\b", "com.google.javascript.jscomp.Compiler", code)
    new = re.sub(
        r"^\s*import\s+com\.google\.javascript\.jscomp\.com\.google\.javascript\.jscomp\.Compiler;\s*\n",
        "",
        new,
        flags=re.MULTILINE,
    )
    new = re.sub(
        r"^\s*import\s+com\.google\.javascript\.jscomp\.Compiler;\s*\n",
        "",
        new,
        flags=re.MULTILINE,
    )
    if new != code:
        return new, ["fully qualify ambiguous Closure Compiler"]
    return code, []


def _p0_fix_captured_local_final(code: str, text: str) -> tuple[str, list[str]]:
    match = re.search(r"local variable\s+(\w+)\s+is accessed from within inner class; needs to be declared final", text)
    if not match:
        return code, []
    name = match.group(1)
    pattern = re.compile(rf"^(\s*)(?!final\b)([\w<>\[\].?,\s]+?\s+{re.escape(name)}\s*=)", re.MULTILINE)
    new, count = pattern.subn(r"\1final \2", code, count=1)
    if count:
        return new, [f"add final to captured local variable {name}"]
    return code, []


def apply_p0_postprocess(code: str, compile_output: str) -> tuple[str, list[str]]:
    notes: list[str] = []
    current, more = _p0_strip_natural_language_pollution(code)
    notes.extend(more)
    current, more = _p0_fix_ambiguous_closure_compiler(current, compile_output)
    notes.extend(more)
    imports = [P0_IMPORTS_BY_SYMBOL[sym] for sym in sorted(_p0_missing_symbols(compile_output)) if sym in P0_IMPORTS_BY_SYMBOL]
    current, more = _p0_insert_imports(current, imports)
    notes.extend(more)
    current, more = _p0_fix_captured_local_final(current, compile_output)
    notes.extend(more)
    current, prune_notes = _prune_generated_imports(current, compile_output)
    notes.extend(f"prune: {note}" for note in prune_notes)
    return current, notes


def main() -> None:
    parser = argparse.ArgumentParser(description="Defects4J multi-method generated-suite eval runner")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--workspace", default=str(DEFAULT_WORKSPACE))
    parser.add_argument("--dataset", default=str(d4j.D4J_DATASET))
    parser.add_argument("--bugs", nargs="*")
    parser.add_argument("--bug-list-file")
    parser.add_argument("--all-bugs", action="store_true")
    parser.add_argument("--skip-completed-from", nargs="*", default=[])
    parser.add_argument("--num-shards", type=int, default=1)
    parser.add_argument("--shard-index", type=int, default=0)
    parser.add_argument("--max-bugs", type=int, default=0)
    parser.add_argument("--max-focal-per-bug", type=int, default=0)
    parser.add_argument("--model", default=d4j.MODEL)
    parser.add_argument("--api-key", default="")
    parser.add_argument("--methods-per-class", type=int, default=DEFAULT_TEST_METHODS)
    parser.add_argument("--repair-rounds", type=int, default=DEFAULT_MAX_REPAIR_ROUNDS)
    parser.add_argument("--generation-repair-rounds", type=int, default=DEFAULT_GENERATION_REPAIR_ROUNDS)
    parser.add_argument("--max-attempts", type=int, default=DEFAULT_MAX_ATTEMPTS)
    parser.add_argument("--skill-start-attempt", type=int, default=DEFAULT_SKILL_START_ATTEMPT)
    parser.add_argument("--max-source-chars", type=int, default=DEFAULT_MAX_SOURCE_CHARS)
    parser.add_argument("--tool-steps", type=int, default=DEFAULT_TOOL_STEPS)
    parser.add_argument(
        "--vanilla-llm",
        action="store_true",
        help=(
            "Run pure Q&A LLM test generation: no tools, no skill bank, and no "
            "multi-attempt continuation. The prompt still includes the fixed-version "
            "focal method/source."
        ),
    )
    parser.add_argument(
        "--generation-max-tokens",
        type=int,
        default=4096,
        help="Max output tokens for initial test generation and generation-submission repair.",
    )
    parser.add_argument("--test-timeout", type=int, default=DEFAULT_TEST_TIMEOUT)
    parser.add_argument("--package-mode", choices=["gentest", "same"], default="gentest")
    parser.add_argument("--stop-on-detect", dest="stop_on_detect", action="store_true")
    parser.add_argument("--no-stop-on-detect", dest="stop_on_detect", action="store_false")
    parser.add_argument(
        "--skill-bank",
        default="",
        help="Path to skill bank directory. "
             "When set, skill tools (list_skills, read_skill) become available from "
             "--skill-start-attempt onward. For non-PASS_BOTH retries, the default "
             "tier gate exposes skills only if explicit tier metadata exists. "
             "Default: no skill bank.",
    )
    parser.add_argument(
        "--disable-skill-tier-gate",
        action="store_true",
        default=not SKILL_TIER_GATE_DEFAULT,
        help=(
            "Disable strict metadata gate for non-PASS_BOTH retries. "
            "By default, FAIL_ON_FIXED/COMPILE_FAIL/NO_TEST_GENERATED retries only "
            "receive skill tools when the bank contains explicit applicable_tiers or tier tags."
        ),
    )
    parser.set_defaults(stop_on_detect=True)
    args = parser.parse_args()

    if args.vanilla_llm:
        args.tool_steps = 0
        args.skill_bank = ""
        args.max_attempts = 1

    if args.api_key:
        os.environ["DEEPSEEK_API_KEY"] = args.api_key
    d4j.DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", d4j.DEEPSEEK_API_KEY)
    d4j.MODEL = args.model or d4j.MODEL
    if not d4j.DEEPSEEK_API_KEY:
        print("[ERROR] DEEPSEEK_API_KEY not set")
        sys.exit(1)

    output_dir = Path(args.output)
    workspace_base = Path(args.workspace)
    output_dir.mkdir(parents=True, exist_ok=True)
    workspace_base.mkdir(parents=True, exist_ok=True)

    # Load skill bank if path provided
    skill_bank: dict[str, Any] | None = None
    if args.skill_bank:
        skill_bank = _load_skill_bank(args.skill_bank)
        if skill_bank is None:
            print("[WARN] --skill-bank specified but failed to load; continuing without skills")
        elif args.max_attempts < args.skill_start_attempt:
            print("[INFO] --skill-bank loaded but max attempts end before --skill-start-attempt; skills will not be used")

    selected = _select_bug_groups(args, output_dir)
    print(f"[INFO] Final queue: {len(selected)} bug groups")
    start = time.strftime("%Y%m%d_%H%M%S")
    run_suffix = start
    if args.num_shards > 1:
        run_suffix = f"{start}_shard{args.shard_index}_pid{os.getpid()}"
    results: list[dict[str, Any]] = []
    for idx, bug_group in enumerate(selected, 1):
        first = d4j._normalize_d4j_record(bug_group[0])
        bug_key = f"{first.get('project')}-{first.get('bug_id')}"
        print(f"\n{'#'*60}\n# [{idx}/{len(selected)}] {bug_key}\n{'#'*60}")
        bug_result = run_single_bug(
            bug_group,
            output_dir=output_dir,
            workspace_base=workspace_base,
            stop_on_detect=args.stop_on_detect,
            max_focal_per_bug=args.max_focal_per_bug,
            methods_per_class=args.methods_per_class,
            package_mode=args.package_mode,
            max_source_chars=args.max_source_chars,
            tool_steps=args.tool_steps,
            generation_max_tokens=args.generation_max_tokens,
            generation_repair_rounds=args.generation_repair_rounds,
            repair_rounds=args.repair_rounds,
            max_attempts=args.max_attempts,
            skill_start_attempt=args.skill_start_attempt,
            test_timeout=args.test_timeout,
            skill_bank=skill_bank,
            skill_tier_gate=not args.disable_skill_tier_gate,
        )
        results.append(bug_result)
        inc_path = output_dir / f"results_{run_suffix}.json"
        inc_path.write_text(json.dumps(results, indent=2, default=str), encoding="utf-8")
        tiers: dict[str, int] = {}
        for item in results:
            tier = item.get("final_tier", "UNKNOWN")
            tiers[tier] = tiers.get(tier, 0) + 1
        print(f"[SUMMARY] {tiers}")

    tiers: dict[str, int] = {}
    for item in results:
        tier = item.get("final_tier", "UNKNOWN")
        tiers[tier] = tiers.get(tier, 0) + 1
    final_path = output_dir / f"final_results_{run_suffix}.json"
    final_path.write_text(
        json.dumps(
            {
                "config": {
                    "pipeline": (
                        "Fixed-view multi-method JUnit4 generated-suite evaluation"
                        + ("; SkillBank v2" if skill_bank else "; no SkillBank")
                    ),
                    "model": d4j.MODEL,
                    "dataset": str(args.dataset),
                    "methods_per_class": args.methods_per_class,
                    "tool_steps": args.tool_steps,
                    "vanilla_llm": bool(args.vanilla_llm),
                    "generation_repair_rounds": args.generation_repair_rounds,
                    "repair_rounds": args.repair_rounds,
                    "max_attempts": args.max_attempts,
                    "skill_start_attempt": args.skill_start_attempt,
                    "package_mode": args.package_mode,
                    "all_bugs": args.all_bugs,
                    "num_shards": args.num_shards,
                    "shard_index": args.shard_index,
                    "run_suffix": run_suffix,
                    "skip_completed_from": args.skip_completed_from,
                    "skill_bank": args.skill_bank if args.skill_bank else None,
                    "skill_tier_gate": not args.disable_skill_tier_gate,
                },
                "summary": {
                    "total": len(results),
                    "bug_detected": tiers.get("BUG_DETECTED", 0),
                    "tiers": tiers,
                },
                "results": results,
            },
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )
    total = len(results)
    detected = tiers.get("BUG_DETECTED", 0)
    print(f"\nFinal results saved to {final_path}")
    if total:
        print(f"BUG_DETECTED: {detected}/{total} ({detected / total * 100:.1f}%)")


if __name__ == "__main__":
    main()

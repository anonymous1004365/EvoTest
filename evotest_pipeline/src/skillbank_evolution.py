"""Utilities for evolving the SkillBank.

This module implements the non-destructive, operation-log based evolution path
described in ``docs/system_design_v16.md``.  It intentionally preserves the old
SkillBank layout and adds metadata in-place only in copied snapshots.
"""

from __future__ import annotations

import json
import re
import shutil
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import yaml
except Exception:  # pragma: no cover - scripts surface a clear runtime error
    yaml = None


SKILL_TOOLS = {
    "list_skills",
    "search_skills",
    "search_code_tags",
    "list_code_tags",
    "get_skills_by_code_tags",
    "read_skill",
}


TIER_TO_APPLICABLE = {
    "COMPILE_FAIL": "COMPILE_FAIL",
    "FAIL_ON_FIXED": "FAIL_ON_FIXED",
    "PASS_BOTH": "PASS_BOTH",
    "BUG_DETECTED": "PASS_BOTH",
    "NO_TEST_GENERATED": "NO_TEST_GENERATED",
}


def safe_name(value: str) -> str:
    return "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in str(value))


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8", errors="replace"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, default=str), encoding="utf-8")


def load_result_rows(paths: list[Path]) -> list[dict[str, Any]]:
    """Load result rows from files or experiment directories."""
    rows: list[dict[str, Any]] = []
    seen_files: set[Path] = set()
    files: list[Path] = []
    for path in paths:
        if path.is_dir():
            candidates = sorted(path.glob("final_results_*.json"))
            if candidates:
                files.append(candidates[-1])
            else:
                files.extend(sorted((path / "results").glob("*.json")))
                files.extend(sorted(path.glob("results_*.json")))
        else:
            files.append(path)
    for file in files:
        file = file.resolve()
        if file in seen_files or not file.exists():
            continue
        seen_files.add(file)
        payload = read_json(file)
        if isinstance(payload, dict) and isinstance(payload.get("results"), list):
            rows.extend(row for row in payload["results"] if isinstance(row, dict))
        elif isinstance(payload, list):
            rows.extend(row for row in payload if isinstance(row, dict))
        elif isinstance(payload, dict):
            rows.append(payload)
    return rows


def split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end >= 0 and yaml is not None:
            raw = text[3:end].strip()
            try:
                meta = yaml.safe_load(raw) or {}
                if isinstance(meta, dict):
                    return meta, text[end + 4 :].lstrip()
            except Exception:
                pass
    return {}, text


def dump_skill_text(meta: dict[str, Any], body: str) -> str:
    if yaml is None:
        raise RuntimeError("PyYAML is required to write SkillBank metadata")
    frontmatter = yaml.safe_dump(meta, allow_unicode=True, sort_keys=False).strip()
    return f"---\n{frontmatter}\n---\n\n{body.lstrip()}"


def load_skill_files(bank_dir: Path) -> dict[str, dict[str, Any]]:
    skills_dir = bank_dir / "skills"
    out: dict[str, dict[str, Any]] = {}
    for path in sorted(skills_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8", errors="replace")
        meta, body = split_frontmatter(text)
        name = str(meta.get("id") or meta.get("name") or path.stem)
        out[name] = {"name": name, "path": path, "meta": meta, "body": body, "raw": text}
    return out


def _json_from_observation(observation: str) -> dict[str, Any]:
    text = (observation or "").strip()
    if not text:
        return {}
    try:
        parsed = json.loads(text)
        return parsed if isinstance(parsed, dict) else {}
    except Exception:
        return {}


def _skill_names_from_rows(rows: Any) -> list[str]:
    names: list[str] = []
    if isinstance(rows, list):
        for item in rows:
            if isinstance(item, dict):
                name = item.get("name") or item.get("id") or item.get("title")
                if name:
                    names.append(str(name))
            elif item:
                names.append(str(item))
    return names


def _event_from_tool_call(step: dict[str, Any], call: dict[str, Any], phase: str) -> dict[str, Any] | None:
    name = str(call.get("name") or "")
    if name not in SKILL_TOOLS:
        return None
    args = call.get("arguments") or {}
    if not isinstance(args, dict):
        args = {}
    parsed = _json_from_observation(str(call.get("observation") or ""))
    returned_skills = _skill_names_from_rows(parsed.get("skills"))
    returned_code_tags = _skill_names_from_rows(parsed.get("code_tags"))
    event = {
        "phase": phase,
        "step": step.get("step"),
        "tool": name,
        "query": str(args.get("query") or ""),
        "selected_code_tags": [str(x) for x in (args.get("code_tags") or [])],
        "returned_skills": returned_skills,
        "returned_code_tags": returned_code_tags,
    }
    if name == "read_skill":
        event["read_skill"] = str(args.get("name") or "")
    return event


def extract_skill_events(tool_trajectory: list[dict[str, Any]], *, phase: str) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for step in tool_trajectory or []:
        if not isinstance(step, dict):
            continue
        for call in step.get("tool_calls") or []:
            if not isinstance(call, dict):
                continue
            event = _event_from_tool_call(step, call, phase)
            if event is not None:
                events.append(event)
    return events


def _append_unique(items: list[str], values: list[str]) -> None:
    seen = set(items)
    for value in values:
        value = str(value or "").strip()
        if value and value not in seen:
            items.append(value)
            seen.add(value)


def _collect_skill_usage(row: dict[str, Any]) -> dict[str, Any]:
    retrieval_events: list[dict[str, Any]] = []
    retrieved: list[str] = []
    read: list[str] = []

    generation = row.get("generation") or {}
    retrieval_events.extend(extract_skill_events(generation.get("tool_trajectory") or [], phase="generation"))
    _append_unique(retrieved, _skill_names_from_rows(generation.get("skill_initial_candidates") or []))
    _append_unique(read, [str(x) for x in (generation.get("skill_read_skills") or [])])

    verification = row.get("verification") or {}
    for attempt in verification.get("repair_attempts") or []:
        if not isinstance(attempt, dict):
            continue
        retrieval_events.extend(extract_skill_events(attempt.get("tool_trajectory") or [], phase="repair"))
        _append_unique(retrieved, _skill_names_from_rows(attempt.get("skill_initial_candidates") or []))
        _append_unique(read, [str(x) for x in (attempt.get("skill_read_skills") or [])])

    for attempt in row.get("retry_attempts") or []:
        if not isinstance(attempt, dict):
            continue
        retrieval_events.extend(extract_skill_events(attempt.get("tool_trajectory") or [], phase="pass_both_retry"))
        _append_unique(retrieved, _skill_names_from_rows(attempt.get("skill_initial_candidates") or []))
        _append_unique(read, [str(x) for x in (attempt.get("skill_read_skills") or [])])
        _append_unique(retrieved, _skill_names_from_rows(attempt.get("repair_skill_initial_candidates") or []))
        _append_unique(read, [str(x) for x in (attempt.get("repair_skill_read_skills") or [])])
        for repair in ((attempt.get("verification") or {}).get("repair_attempts") or []):
            if isinstance(repair, dict):
                retrieval_events.extend(extract_skill_events(repair.get("tool_trajectory") or [], phase="retry_repair"))

    for event in retrieval_events:
        _append_unique(retrieved, event.get("returned_skills") or [])
        if event.get("read_skill"):
            _append_unique(read, [str(event.get("read_skill"))])

    final_tier = str(row.get("final_tier_after_dependency_replay") or row.get("posthoc_final_tier") or row.get("final_tier") or "UNKNOWN")
    helpfulness = []
    for skill in read:
        if final_tier == "BUG_DETECTED":
            label = "helped"
        elif final_tier == "PASS_BOTH":
            label = "neutral"
        elif final_tier in {"COMPILE_FAIL", "FAIL_ON_FIXED"}:
            label = "too_generic"
        else:
            label = "neutral"
        helpfulness.append({"skill": skill, "label": label})

    followed = [{"skill": skill, "assessment": "unknown_from_logs"} for skill in read]
    return {
        "retrieval_events": retrieval_events,
        "retrieved": retrieved,
        "read_events": [
            {"skill": skill, "why_read": "read_skill tool call or skill_read_skills log"}
            for skill in read
        ],
        "read": read,
        "followed": followed,
        "helpfulness": helpfulness,
    }


def _attempts_from_row(row: dict[str, Any]) -> list[dict[str, Any]]:
    attempts: list[dict[str, Any]] = []
    generation = row.get("generation") or {}
    if generation:
        attempts.append({
            "attempt_id": 0,
            "stage": "generation",
            "tier": (row.get("verification") or {}).get("tier") or row.get("final_tier") or "UNKNOWN",
            "hypothesis": _compact_text(generation.get("raw_response") or generation.get("final_raw_response_full") or ""),
            "test_methods": _extract_method_names(generation),
            "failure_reason": _compact_text(row.get("feedback") or ""),
            "progress_signal": "",
        })
    verification = row.get("verification") or {}
    for idx, repair in enumerate(verification.get("repair_attempts") or [], start=1):
        if not isinstance(repair, dict):
            continue
        attempts.append({
            "attempt_id": idx,
            "stage": "repair",
            "tier": verification.get("tier") or row.get("final_tier") or "UNKNOWN",
            "hypothesis": _compact_text(repair.get("raw_response") or ""),
            "test_methods": [],
            "failure_reason": repair.get("error") or "",
            "progress_signal": "",
        })
    for idx, retry in enumerate(row.get("retry_attempts") or [], start=1):
        if not isinstance(retry, dict):
            continue
        verification_tier = ((retry.get("verification") or {}).get("tier") or retry.get("tier") or "")
        attempts.append({
            "attempt_id": idx,
            "stage": "pass_both_retry",
            "tier": verification_tier or row.get("final_tier") or "UNKNOWN",
            "hypothesis": _compact_text(retry.get("raw_response") or retry.get("forced_response") or ""),
            "test_methods": [],
            "failure_reason": retry.get("error") or "",
            "progress_signal": _transition_signal(row.get("final_tier"), verification_tier),
        })
    return attempts


def _extract_method_names(generation: dict[str, Any]) -> list[str]:
    raw = json.dumps(generation, ensure_ascii=False, default=str)
    names = re.findall(r'"test_method_name"\s*:\s*"([^"]+)"', raw)
    out: list[str] = []
    _append_unique(out, names)
    return out[:20]


def _compact_text(text: Any, limit: int = 800) -> str:
    value = re.sub(r"\s+", " ", str(text or "")).strip()
    return value[:limit]


def _transition_signal(before: Any, after: Any) -> str:
    if not before or not after or before == after:
        return ""
    return f"{before}_TO_{after}".upper()


def build_case_report(row: dict[str, Any]) -> dict[str, Any]:
    final_tier = str(row.get("final_tier_after_dependency_replay") or row.get("posthoc_final_tier") or row.get("final_tier") or "UNKNOWN")
    skill_usage = _collect_skill_usage(row)
    report = {
        "case_id": row.get("record_key") or row.get("bug_id") or row.get("idx"),
        "idx": row.get("idx"),
        "dataset": row.get("dataset") or "unknown",
        "project": row.get("project"),
        "bug_id": row.get("bug_id"),
        "source_id": row.get("source_id"),
        "focal_method": row.get("focal_method") or row.get("method_name"),
        "failing_test_class": row.get("failing_test_class"),
        "final_tier": final_tier,
        "attempts": _attempts_from_row(row),
        "oracle_analysis": {
            "triggering_behavior": "",
            "tg_gap": "",
            "must_not_memorize": "",
            "status": "not_performed_by_deterministic_extractor",
        },
        "skill_usage": skill_usage,
        "missed_skill_analysis": {"better_existing_skills": []},
        "proposed_operations": _propose_case_ops(row, skill_usage, final_tier),
    }
    return report


def _propose_case_ops(row: dict[str, Any], skill_usage: dict[str, Any], final_tier: str) -> list[dict[str, Any]]:
    ops: list[dict[str, Any]] = []
    applicable = TIER_TO_APPLICABLE.get(final_tier)
    for item in skill_usage.get("helpfulness") or []:
        skill = item.get("skill")
        if not skill:
            continue
        patch: dict[str, Any] = {
            "evidence_delta": {"read": 1, str(item.get("label") or "neutral"): 1},
        }
        if applicable:
            patch["add_applicable_tiers"] = [applicable]
        queries = _queries_for_skill(skill_usage, str(skill))
        if queries:
            patch["add_keywords"] = queries[:8]
        ops.append({
            "op": "MODIFY_META",
            "skill": skill,
            "reason": f"Skill was read in a case ending as {final_tier}",
            "patch": patch,
        })
    if final_tier in {"COMPILE_FAIL", "FAIL_ON_FIXED", "PASS_BOTH", "NO_TEST_GENERATED"}:
        ops.append(_tier_skill_add_op(final_tier, row))
    return ops


def _queries_for_skill(skill_usage: dict[str, Any], skill: str) -> list[str]:
    queries: list[str] = []
    for event in skill_usage.get("retrieval_events") or []:
        returned = set(event.get("returned_skills") or [])
        if skill in returned or event.get("read_skill") == skill:
            q = str(event.get("query") or "").strip()
            if q:
                queries.append(q[:120])
            for tag in event.get("selected_code_tags") or []:
                if tag:
                    queries.append(str(tag))
    out: list[str] = []
    _append_unique(out, queries)
    return out


def _tier_skill_add_op(final_tier: str, row: dict[str, Any]) -> dict[str, Any]:
    normalized = final_tier.lower()
    name = {
        "COMPILE_FAIL": "tier-compile-fail-repair-from-diagnostics",
        "FAIL_ON_FIXED": "tier-fail-on-fixed-calibrate-fixed-behavior",
        "PASS_BOTH": "tier-pass-both-discriminating-hypothesis",
        "NO_TEST_GENERATED": "tier-no-test-generated-submit-parseable-suite",
    }.get(final_tier, f"tier-{normalized}")
    guidance = {
        "COMPILE_FAIL": (
            "WHEN a generated suite fails to compile, treat compiler diagnostics as ground truth. "
            "Check imports, visibility, constructor signatures, abstract methods, JUnit version, "
            "and ambiguous static imports. Prefer deleting one invalid test over keeping a broad "
            "suite that cannot compile."
        ),
        "FAIL_ON_FIXED": (
            "WHEN a generated suite fails on the fixed version, the assertion is too strong or the "
            "setup violates the fixed API contract. Re-read fixed source and existing tests, reduce "
            "the assertion to fixed-valid behavior, and remove scenarios unsupported by the fixed code."
        ),
        "PASS_BOTH": (
            "WHEN tests pass on both fixed and buggy versions, keep fixed correctness but change the "
            "hypothesis. Target boundary values, malformed inputs, state transitions, nested structures, "
            "or branch conditions not covered by the current suite."
        ),
        "NO_TEST_GENERATED": (
            "WHEN the agent fails to submit parseable tests, stop exploring and convert the current "
            "understanding into a small valid JSON/test class. Preserve class name, package, and 2-4 "
            "self-contained tests."
        ),
    }.get(final_tier, "General tier-specific testing guidance.")
    return {
        "op": "ADD",
        "skill": name,
        "reason": f"Observed {final_tier} case that can teach tier-specific recovery.",
        "patch": {
            "name": name,
            "description": guidance[:180],
            "guidance": guidance,
            "code_tags": ["TIER_RECOVERY", final_tier],
            "test_pattern": "STATE_TEST",
            "retrieval": {
                "applicable_tiers": [final_tier],
                "transition_tags": [],
                "keywords": [final_tier.lower(), str(row.get("focal_method") or "")],
            },
        },
    }


def aggregate_case_reports(reports: list[dict[str, Any]], *, min_add_support: int = 2) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    skill_stats: dict[str, dict[str, Any]] = defaultdict(lambda: {
        "retrieved": 0,
        "read": 0,
        "helped": 0,
        "neutral": 0,
        "misleading": 0,
        "too_generic": 0,
        "keywords": Counter(),
        "applicable_tiers": Counter(),
    })
    add_candidates: dict[str, dict[str, Any]] = {}
    add_support: Counter[str] = Counter()
    for report in reports:
        usage = report.get("skill_usage") or {}
        for skill in usage.get("retrieved") or []:
            skill_stats[str(skill)]["retrieved"] += 1
        for skill in usage.get("read") or []:
            skill_stats[str(skill)]["read"] += 1
        for item in usage.get("helpfulness") or []:
            skill = str(item.get("skill") or "")
            label = str(item.get("label") or "neutral")
            if skill:
                skill_stats[skill][label] = int(skill_stats[skill].get(label) or 0) + 1
                tier = TIER_TO_APPLICABLE.get(str(report.get("final_tier") or ""))
                if tier:
                    skill_stats[skill]["applicable_tiers"][tier] += 1
                for q in _queries_for_skill(usage, skill):
                    skill_stats[skill]["keywords"][q] += 1
        for op in report.get("proposed_operations") or []:
            if op.get("op") == "ADD":
                name = str(op.get("skill") or (op.get("patch") or {}).get("name") or "")
                if name:
                    add_candidates.setdefault(name, op)
                    add_support[name] += 1

    ops: list[dict[str, Any]] = []
    for skill, stats in sorted(skill_stats.items()):
        patch: dict[str, Any] = {
            "evidence_delta": {
                "retrieved": stats["retrieved"],
                "read": stats["read"],
                "helped": stats["helped"],
                "neutral": stats["neutral"],
                "misleading": stats["misleading"],
                "too_generic": stats["too_generic"],
            }
        }
        keywords = [kw for kw, _count in stats["keywords"].most_common(12)]
        tiers = [tier for tier, _count in stats["applicable_tiers"].most_common()]
        if keywords:
            patch["add_keywords"] = keywords
        if tiers:
            patch["add_applicable_tiers"] = tiers
        if stats["helped"] > 0:
            patch["priority_delta"] = min(3, stats["helped"])
        if stats["too_generic"] > stats["helped"] + stats["neutral"]:
            patch["add_negative_triggers"] = ["review fixed-version diagnostics before applying this skill"]
        ops.append({
            "op": "MODIFY_META",
            "skill": skill,
            "reason": "Aggregated skill usage evidence across case reports.",
            "patch": patch,
        })

    for name, count in add_support.most_common():
        if count < min_add_support:
            continue
        op = dict(add_candidates[name])
        op["support"] = count
        op["reason"] = f"{op.get('reason', '')} Supported by {count} case reports."
        ops.append(op)

    summary = {
        "reports": len(reports),
        "skills_with_usage": len(skill_stats),
        "add_candidates": dict(add_support),
        "operation_counts": dict(Counter(op.get("op") for op in ops)),
    }
    return ops, summary


def apply_ops_to_skill_bank(bank_dir: Path, ops: list[dict[str, Any]], output_dir: Path) -> dict[str, Any]:
    """Copy a SkillBank and apply operation JSON objects."""
    target_bank = output_dir / "skill_bank"
    if target_bank.exists():
        shutil.rmtree(target_bank)
    shutil.copytree(bank_dir, target_bank)
    skills = load_skill_files(target_bank)
    applied: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    for op in ops:
        kind = str(op.get("op") or op.get("op_type") or "").upper().replace("-", "_")
        if kind == "MODIFY-META":
            kind = "MODIFY_META"
        skill_name = str(op.get("skill") or op.get("target") or "")
        patch = op.get("patch") or op.get("payload") or {}
        if kind == "ADD":
            result = _apply_add(target_bank, skills, patch, op)
        elif kind == "MODIFY_META":
            result = _apply_modify_meta(skills, skill_name, patch)
        elif kind == "MODIFY":
            result = _apply_modify(skills, skill_name, patch)
        elif kind == "DEPRECATE":
            result = _apply_deprecate(skills, skill_name, patch)
        else:
            skipped.append({"op": op, "reason": f"unsupported op {kind}"})
            continue
        if result.get("ok"):
            applied.append({"op": kind, "skill": result.get("skill"), "reason": op.get("reason", "")})
        else:
            skipped.append({"op": op, "reason": result.get("error", "unknown")})

    _rewrite_skill_files(skills)
    _update_index_model(target_bank, skills)
    summary = {
        "source_bank": str(bank_dir),
        "target_bank": str(target_bank),
        "ops_total": len(ops),
        "applied": len(applied),
        "skipped": len(skipped),
        "applied_ops": applied,
        "skipped_ops": skipped,
    }
    write_json(output_dir / "apply_summary.json", summary)
    return summary


def _ensure_evolution_meta(meta: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    evo = meta.setdefault("evolution", {})
    if not isinstance(evo, dict):
        evo = {}
        meta["evolution"] = evo
    evo.setdefault("active", True)
    evo.setdefault("priority", 0)
    evidence = evo.setdefault("evidence", {})
    if not isinstance(evidence, dict):
        evidence = {}
        evo["evidence"] = evidence
    retrieval = meta.setdefault("retrieval", {})
    if not isinstance(retrieval, dict):
        retrieval = {}
        meta["retrieval"] = retrieval
    retrieval.setdefault("keywords", [])
    retrieval.setdefault("boosted_tags", [])
    retrieval.setdefault("suppressed_tags", [])
    retrieval.setdefault("negative_triggers", [])
    retrieval.setdefault("applicable_tiers", [])
    retrieval.setdefault("transition_tags", [])
    return evo, retrieval


def _apply_modify_meta(skills: dict[str, dict[str, Any]], skill_name: str, patch: dict[str, Any]) -> dict[str, Any]:
    skill = _find_skill(skills, skill_name)
    if not skill:
        return {"ok": False, "error": f"skill not found: {skill_name}"}
    meta = skill["meta"]
    evo, retrieval = _ensure_evolution_meta(meta)
    evidence_delta = patch.get("evidence_delta") or {}
    evidence = evo.setdefault("evidence", {})
    for key, value in evidence_delta.items():
        try:
            evidence[key] = int(evidence.get(key) or 0) + int(value or 0)
        except Exception:
            continue
    if "priority_delta" in patch:
        evo["priority"] = int(evo.get("priority") or 0) + int(patch.get("priority_delta") or 0)
    for field, target in (
        ("add_keywords", "keywords"),
        ("add_boosted_tags", "boosted_tags"),
        ("add_suppressed_tags", "suppressed_tags"),
        ("add_negative_triggers", "negative_triggers"),
        ("add_applicable_tiers", "applicable_tiers"),
        ("add_transition_tags", "transition_tags"),
    ):
        _meta_add_list(retrieval, target, patch.get(field) or [])
    if patch.get("keywords"):
        _meta_add_list(retrieval, "keywords", patch.get("keywords") or [])
    if patch.get("code_tags"):
        _meta_add_list(meta, "code_tags", patch.get("code_tags") or [])
    if patch.get("add_code_tags"):
        _meta_add_list(meta, "code_tags", patch.get("add_code_tags") or [])
    if patch.get("test_pattern"):
        meta["test_pattern"] = patch["test_pattern"]
    if "description" in patch:
        meta["description"] = patch["description"]
    if patch.get("content"):
        marker = "\n\n## Evolution Notes\n\n"
        body = skill["body"]
        if "## Evolution Notes" not in body:
            body = body.rstrip() + marker
        skill["body"] = body.rstrip() + "\n" + str(patch["content"]).strip() + "\n"
    return {"ok": True, "skill": skill["name"]}


def _apply_modify(skills: dict[str, dict[str, Any]], skill_name: str, patch: dict[str, Any]) -> dict[str, Any]:
    skill = _find_skill(skills, skill_name)
    if not skill:
        return {"ok": False, "error": f"skill not found: {skill_name}"}
    append_text = str(patch.get("append_guidance") or patch.get("append_dont") or "")
    if append_text:
        marker = "\n\n## Evolution Notes\n\n"
        body = skill["body"]
        if "## Evolution Notes" not in body:
            body = body.rstrip() + marker
        body = body.rstrip() + f"\n- {append_text.strip()}\n"
        skill["body"] = body
    if "guidance" in patch:
        skill["body"] = str(patch["guidance"])
    return {"ok": True, "skill": skill["name"]}


def _apply_deprecate(skills: dict[str, dict[str, Any]], skill_name: str, patch: dict[str, Any]) -> dict[str, Any]:
    skill = _find_skill(skills, skill_name)
    if not skill:
        return {"ok": False, "error": f"skill not found: {skill_name}"}
    evo, retrieval = _ensure_evolution_meta(skill["meta"])
    evo["active"] = False
    if patch.get("reason"):
        _meta_add_list(retrieval, "negative_triggers", [str(patch["reason"])])
    return {"ok": True, "skill": skill["name"]}


def _apply_add(
    target_bank: Path,
    skills: dict[str, dict[str, Any]],
    patch: dict[str, Any],
    op: dict[str, Any],
) -> dict[str, Any]:
    skills_dir = target_bank / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    name = str(patch.get("name") or op.get("skill") or op.get("target") or "evolved-skill")
    filename = safe_name(name)
    path = skills_dir / f"{filename}.md"
    suffix = 1
    while path.exists():
        suffix += 1
        path = skills_dir / f"{filename}-{suffix}.md"
    meta = {
        "name": name,
        "description": patch.get("description") or "",
        "code_tags": patch.get("code_tags") or [],
        "test_pattern": patch.get("test_pattern") or "STATE_TEST",
        "evolution": {
            "active": True,
            "priority": int(patch.get("priority") or 0),
            "evidence": {"added": 1},
        },
        "retrieval": patch.get("retrieval") or {},
    }
    body = str(patch.get("guidance") or patch.get("content") or "")
    text = dump_skill_text(meta, body)
    path.write_text(text, encoding="utf-8")
    loaded_meta, loaded_body = split_frontmatter(text)
    skills[name] = {
        "name": name,
        "path": path,
        "meta": loaded_meta,
        "body": loaded_body,
        "raw": text,
    }
    return {"ok": True, "skill": name}


def _find_skill(skills: dict[str, dict[str, Any]], name: str) -> dict[str, Any] | None:
    if name in skills:
        return skills[name]
    lowered = str(name or "").lower()
    for skill in skills.values():
        meta = skill.get("meta") or {}
        if (
            str(skill.get("name") or "").lower() == lowered
            or str(meta.get("name") or "").lower() == lowered
            or str(meta.get("id") or "").lower() == lowered
            or Path(skill.get("path") or "").stem.lower() == lowered
        ):
            return skill
    return None


def _meta_add_list(container: dict[str, Any], field: str, values: list[Any]) -> None:
    current = container.setdefault(field, [])
    if not isinstance(current, list):
        current = []
        container[field] = current
    seen = {str(x) for x in current}
    for value in values:
        value = str(value or "").strip()
        if value and value not in seen:
            current.append(value)
            seen.add(value)


def _rewrite_skill_files(skills: dict[str, dict[str, Any]]) -> None:
    for skill in skills.values():
        path = Path(skill["path"])
        path.write_text(dump_skill_text(skill["meta"], skill["body"]), encoding="utf-8")


def _update_index_model(bank_dir: Path, skills: dict[str, dict[str, Any]]) -> None:
    if yaml is None:
        return
    entries = []
    for skill in sorted(skills.values(), key=lambda item: str(item.get("name") or "")):
        meta = skill.get("meta") or {}
        entries.append({
            "name": meta.get("name") or skill.get("name"),
            "description": meta.get("description") or "",
            "code_tags": meta.get("code_tags") or meta.get("tags") or [],
            "test_pattern": meta.get("test_pattern") or "",
            "evolution": meta.get("evolution") or {},
            "retrieval": meta.get("retrieval") or {},
        })
    index_path = bank_dir / "_index_model.yaml"
    index_path.write_text(yaml.safe_dump({"skills": entries}, allow_unicode=True, sort_keys=False), encoding="utf-8")

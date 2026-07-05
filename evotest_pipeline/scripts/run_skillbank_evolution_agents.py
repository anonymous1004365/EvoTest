#!/usr/bin/env python3
"""LLM agents for SkillBank evolution experiments.

This script is intentionally separate from the deterministic evolution pipeline.
It runs two small tool-using agents:

1. Case Analysis Agent: inspect one TG result/trajectory plus skills and
   write a structured per-case report.
2. Global Evolution Agent: inspect a small batch of case reports plus the
   current SkillBank and propose/apply operation-log evolution.

All outputs go to a new directory.  The source SkillBank is never modified.
"""

from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import fnmatch
import json
import os
from pathlib import Path
import re
import sys
import time
from typing import Any, Callable

SCRIPT_DIR = Path(__file__).resolve().parent
SRC_DIR = SCRIPT_DIR.parent / "src"
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(SRC_DIR))

import skillbank_tools  # noqa: E402
from skillbank_evolution import (  # noqa: E402
    apply_ops_to_skill_bank,
    build_case_report,
    load_result_rows,
    read_json,
    safe_name,
    write_json,
)


DEFAULT_MODEL = os.environ.get(
    "EVOLUTION_AGENT_MODEL",
    os.environ.get("SKILL_MODEL", os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-flash")),
)
DEFAULT_API_URL = os.environ.get("DEEPSEEK_API_URL", os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com"))
MAX_OBSERVATION_CHARS = int(os.environ.get("EVOLUTION_AGENT_MAX_OBSERVATION_CHARS", "18000"))


def _now_tag() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _json(data: Any, *, limit: int | None = None) -> str:
    text = json.dumps(data, ensure_ascii=False, indent=2, default=str)
    if limit is not None and len(text) > limit:
        return text[:limit] + f"\n...[truncated {len(text) - limit} chars]"
    return text


def _compact_text(text: Any, limit: int = 16000) -> str:
    value = str(text or "")
    if len(value) > limit:
        return value[:limit] + f"\n...[truncated {len(value) - limit} chars]"
    return value


def _extract_json_object(text: str) -> Any:
    text = (text or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text).strip()
    try:
        return json.loads(text)
    except Exception:
        pass
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        return json.loads(text[start : end + 1])
    raise ValueError("Could not parse JSON object from agent output")


def _client() -> Any:
    from openai import OpenAI

    api_key = os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing DEEPSEEK_API_KEY or OPENAI_API_KEY")
    return OpenAI(api_key=api_key, base_url=DEFAULT_API_URL, timeout=180)


def _create_chat_completion_with_retry(client: Any, kwargs: dict[str, Any], *, retries: int = 6) -> Any:
    delay = 5.0
    last_exc: Exception | None = None
    for attempt in range(retries + 1):
        try:
            return client.chat.completions.create(**kwargs)
        except Exception as exc:
            last_exc = exc
            message = str(exc).lower()
            retryable = any(token in message for token in ("429", "rate", "timeout", "temporar", "connection", "reset"))
            if attempt >= retries or not retryable:
                raise
            sleep_for = delay * (1.0 + 0.2 * min(attempt, 5))
            time.sleep(sleep_for)
            delay = min(delay * 1.8, 90.0)
    if last_exc is not None:
        raise last_exc
    raise RuntimeError("LLM retry loop exited unexpectedly")


def _append_trace(path: Path | None, event: dict[str, Any]) -> None:
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = dict(event)
    payload.setdefault("ts", time.time())
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False, default=str) + "\n")


def _compact_conversation(base: list[dict[str, Any]], trajectory: list[dict[str, Any]]) -> list[dict[str, Any]]:
    lines = ["Tool context was compacted. Keep using the same task instructions."]
    for step in trajectory[-60:]:
        if step.get("model_output"):
            lines.append(f"Step {step.get('step')} note: {str(step.get('model_output'))[:600]}")
        for call in (step.get("tool_calls") or [])[:8]:
            obs = re.sub(r"\s+", " ", str(call.get("observation") or ""))[:900]
            lines.append(f"Step {step.get('step')} {call.get('name')}({call.get('arguments')}): {obs}")
    return list(base) + [{"role": "user", "content": "\n".join(lines)[-24000:]}]


def _call_tool_agent(
    *,
    system: str,
    user: str,
    tools: list[dict[str, Any]],
    executor: Callable[[str, dict[str, Any]], str | None],
    model: str,
    max_tool_steps: int,
    max_tokens: int,
    final_instruction: str,
    trace_path: Path | None,
    context_compact_every: int = 100,
    required_tool_min_counts: dict[str, int] | None = None,
    required_tool_hint: str = "",
) -> tuple[str, list[dict[str, Any]]]:
    client = _client()
    base_messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
    conversation = list(base_messages)
    trajectory: list[dict[str, Any]] = []
    steps_since_compact = 0
    required_counts = {name: int(count) for name, count in (required_tool_min_counts or {}).items() if int(count) > 0}
    executed_counts: Counter[str] = Counter()

    def _missing_required_counts() -> dict[str, dict[str, int]]:
        return {
            name: {"current": executed_counts.get(name, 0), "required": required}
            for name, required in required_counts.items()
            if executed_counts.get(name, 0) < required
        }

    for step_idx in range(max_tool_steps + 1):
        allow_tools = step_idx < max_tool_steps
        if not allow_tools:
            conversation.append({"role": "user", "content": final_instruction})
        kwargs: dict[str, Any] = {
            "model": model,
            "messages": conversation,
            "temperature": 0.2,
            "max_tokens": max_tokens,
        }
        if allow_tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"
        if model in {"deepseek-v4-flash", "deepseek-v4-pro"}:
            kwargs["extra_body"] = {"thinking": {"type": "disabled"}}
        response = _create_chat_completion_with_retry(client, kwargs)
        message = response.choices[0].message
        content = message.content or ""
        calls = list(message.tool_calls or [])
        step_record = {"step": len(trajectory) + 1, "model_output": content, "tool_calls": []}
        _append_trace(trace_path, {
            "event": "llm_response",
            "step": step_record["step"],
            "tool_names": [call.function.name for call in calls],
            "content": content,
            "allow_tools": allow_tools,
        })

        if not calls or not allow_tools:
            missing = _missing_required_counts() if allow_tools else {}
            if missing:
                trajectory.append(step_record)
                conversation.append({"role": "assistant", "content": content})
                reminder = (
                    "Do not finalize yet. You have not inspected enough evidence for this run. "
                    f"Missing minimum tool counts: {json.dumps(missing, ensure_ascii=False)}. "
                    f"{required_tool_hint}".strip()
                )
                conversation.append({"role": "user", "content": reminder})
                _append_trace(trace_path, {
                    "event": "final_blocked_missing_required_tool_counts",
                    "step": step_record["step"],
                    "missing": missing,
                })
                continue
            trajectory.append(step_record)
            conversation.append({"role": "assistant", "content": content})
            return content, trajectory

        assistant_msg = {"role": "assistant", "content": content, "tool_calls": []}
        tool_messages = []
        for call in calls:
            name = call.function.name
            try:
                args = json.loads(call.function.arguments or "{}")
            except Exception:
                args = {}
            try:
                obs = executor(name, args)
                if obs is None:
                    obs = f"Error: unknown tool {name}"
            except Exception as exc:
                obs = f"Error while executing {name}: {exc}"
            obs = _compact_text(obs, MAX_OBSERVATION_CHARS)
            assistant_msg["tool_calls"].append({
                "id": call.id,
                "type": "function",
                "function": {"name": name, "arguments": json.dumps(args, ensure_ascii=False)},
            })
            tool_messages.append({"role": "tool", "tool_call_id": call.id, "name": name, "content": obs})
            step_record["tool_calls"].append({"id": call.id, "name": name, "arguments": args, "observation": obs})
            executed_counts[name] += 1
            _append_trace(trace_path, {
                "event": "tool_call",
                "step": step_record["step"],
                "name": name,
                "arguments": args,
                "observation": obs,
            })
        conversation.append(assistant_msg)
        conversation.extend(tool_messages)
        trajectory.append(step_record)
        steps_since_compact += 1
        if context_compact_every > 0 and steps_since_compact >= context_compact_every:
            conversation = _compact_conversation(base_messages, trajectory)
            step_record["context_compacted_after"] = True
            steps_since_compact = 0
            _append_trace(trace_path, {"event": "context_compacted", "step": step_record["step"]})
    return "", trajectory


def _trajectory_audit(trajectory: list[dict[str, Any]]) -> dict[str, Any]:
    tools: list[str] = []
    read_skills: list[str] = []
    max_step = 0
    for step in trajectory or []:
        try:
            max_step = max(max_step, int(step.get("step") or 0))
        except Exception:
            pass
        for call in step.get("tool_calls") or []:
            name = str(call.get("name") or "")
            if name:
                tools.append(name)
            if name == "read_skill":
                args = call.get("arguments") or {}
                read_skills.append(str(args.get("name") or ""))
    return {
        "llm_steps": max_step,
        "tool_calls": len(tools),
        "tool_counts": dict(Counter(tools)),
        "read_skill_calls": len(read_skills),
        "read_skills_unique": sorted({skill for skill in read_skills if skill}),
    }


def _safe_root(path: str | Path) -> Path:
    value = Path(path).expanduser()
    return value.resolve()


def _file_tools(allowed_roots: list[Path]) -> tuple[list[dict[str, Any]], Callable[[str, dict[str, Any]], str | None]]:
    roots = [_safe_root(root) for root in allowed_roots if str(root)]

    def _inside(path: Path) -> bool:
        try:
            resolved = path.resolve()
        except Exception:
            return False
        return any(resolved == root or root in resolved.parents for root in roots)

    def _resolve(path: str) -> Path:
        target = Path(path).expanduser()
        if not target.is_absolute() and roots:
            target = roots[0] / target
        resolved = target.resolve()
        if not _inside(resolved):
            raise ValueError(f"path outside allowed roots: {path}")
        return resolved

    tools = [
        {
            "type": "function",
            "function": {
                "name": "list_files",
                "description": "List files under an allowed root with glob filtering. Results are truncated.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "root": {"type": "string"},
                        "glob": {"type": "string", "default": "*"},
                        "max_results": {"type": "integer", "default": 80},
                    },
                    "required": ["root"],
                    "additionalProperties": False,
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "grep_text",
                "description": "Search text files under an allowed root. Use concise patterns.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "root": {"type": "string"},
                        "pattern": {"type": "string"},
                        "glob": {"type": "string", "default": "*.json"},
                        "max_results": {"type": "integer", "default": 60},
                    },
                    "required": ["root", "pattern"],
                    "additionalProperties": False,
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "read_text_file",
                "description": "Read a text file with line range and character truncation.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "start_line": {"type": "integer", "default": 1},
                        "num_lines": {"type": "integer", "default": 120},
                        "max_chars": {"type": "integer", "default": 16000},
                    },
                    "required": ["path"],
                    "additionalProperties": False,
                },
            },
        },
    ]

    def _exec(name: str, args: dict[str, Any]) -> str | None:
        if name == "list_files":
            root = _resolve(str(args.get("root") or ""))
            pattern = str(args.get("glob") or "*")
            max_results = max(1, min(300, int(args.get("max_results") or 80)))
            rows = []
            for path in root.rglob("*"):
                if len(rows) >= max_results:
                    break
                if path.is_file() and fnmatch.fnmatch(str(path.relative_to(root)), pattern):
                    rows.append(str(path))
            return _json({"root": str(root), "glob": pattern, "files": rows, "truncated": len(rows) >= max_results})
        if name == "grep_text":
            root = _resolve(str(args.get("root") or ""))
            pattern = str(args.get("pattern") or "")
            glob = str(args.get("glob") or "*.json")
            max_results = max(1, min(200, int(args.get("max_results") or 60)))
            regex = re.compile(pattern, re.IGNORECASE)
            hits = []
            for path in root.rglob("*"):
                if len(hits) >= max_results:
                    break
                if not path.is_file() or not fnmatch.fnmatch(str(path.relative_to(root)), glob):
                    continue
                try:
                    for line_no, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
                        if regex.search(line):
                            hits.append({"path": str(path), "line": line_no, "text": line[:500]})
                            if len(hits) >= max_results:
                                break
                except Exception:
                    continue
            return _json({"root": str(root), "pattern": pattern, "hits": hits, "truncated": len(hits) >= max_results})
        if name == "read_text_file":
            path = _resolve(str(args.get("path") or ""))
            start_line = max(1, int(args.get("start_line") or 1))
            num_lines = max(1, min(600, int(args.get("num_lines") or 120)))
            max_chars = max(1000, min(60000, int(args.get("max_chars") or 16000)))
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
            chunk = "\n".join(f"{idx}: {line}" for idx, line in enumerate(lines[start_line - 1 : start_line - 1 + num_lines], start=start_line))
            return _compact_text(chunk, max_chars)
        return None

    return tools, _exec


def _case_tools(
    *,
    row: dict[str, Any],
    seed_report: dict[str, Any],
    skill_bank: dict[str, Any],
    allowed_roots: list[Path],
    top_k: int,
) -> tuple[list[dict[str, Any]], Callable[[str, dict[str, Any]], str | None], list[str]]:
    read_log: list[str] = []
    initial = skillbank_tools._search_skills(
        skill_bank,
        _json({"row": row, "seed_report": seed_report}, limit=12000),
        top_k=top_k,
        exclude_bug_key=str(row.get("bug_id") or row.get("source_id") or ""),
    )
    skill_exec = skillbank_tools._make_skill_executor(
        skill_bank,
        initial,
        top_k=top_k,
        exclude_bug_key=str(row.get("bug_id") or row.get("source_id") or ""),
        read_log=read_log,
    )
    file_tool_specs, file_exec = _file_tools(allowed_roots)
    tools = [
        {
            "type": "function",
            "function": {
                "name": "read_case_seed_report",
                "description": "Read the deterministic seed report for this case.",
                "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "read_result_row",
                "description": "Read the raw result row for this case, including generation/verification fields.",
                "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "read_tool_trajectory",
                "description": "Read selected tool trajectory steps from generation, repair, or pass_both_retry.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "phase": {"type": "string", "enum": ["generation", "repair", "pass_both_retry", "all"], "default": "all"},
                        "start": {"type": "integer", "default": 1},
                        "limit": {"type": "integer", "default": 12},
                    },
                    "additionalProperties": False,
                },
            },
        },
    ] + skillbank_tools._skill_tool_specs() + file_tool_specs

    def _trajectory_steps(phase: str) -> list[dict[str, Any]]:
        steps: list[dict[str, Any]] = []
        if phase in {"generation", "all"}:
            steps.extend((row.get("generation") or {}).get("tool_trajectory") or [])
        if phase in {"repair", "all"}:
            for attempt in (row.get("verification") or {}).get("repair_attempts") or []:
                if isinstance(attempt, dict):
                    steps.extend(attempt.get("tool_trajectory") or [])
        if phase in {"pass_both_retry", "all"}:
            for attempt in row.get("retry_attempts") or []:
                if isinstance(attempt, dict):
                    steps.extend(attempt.get("tool_trajectory") or [])
        return steps

    def _exec(name: str, args: dict[str, Any]) -> str | None:
        if name == "read_case_seed_report":
            return _json(seed_report, limit=40000)
        if name == "read_result_row":
            return _json(row, limit=60000)
        if name == "read_tool_trajectory":
            phase = str(args.get("phase") or "all")
            start = max(1, int(args.get("start") or 1))
            limit = max(1, min(80, int(args.get("limit") or 12)))
            steps = _trajectory_steps(phase)
            selected = steps[start - 1 : start - 1 + limit]
            return _json({"phase": phase, "start": start, "limit": limit, "total_steps": len(steps), "steps": selected}, limit=60000)
        obs = skill_exec(name, args)
        if obs is not None:
            return obs
        return file_exec(name, args)

    return tools, _exec, read_log


def _case_system_prompt() -> str:
    return (
        "You are a Case Analysis Agent for SkillBank evolution. Analyze one Java test-generation "
        "trajectory. Use tools to inspect the result row, TG trajectory, and skills. "
        "Do not invent facts. If triggering-test or buggy-source evidence is unavailable, say so. "
        "Focus on why TG succeeded/failed, how skills were retrieved/read/used, whether better "
        "metadata could have helped, and what ADD/MODIFY/MODIFY_META/MERGE/SPLIT proposal is justified."
    )


def _case_user_prompt(seed_report: dict[str, Any], allowed_roots: list[Path]) -> str:
    return f"""
Analyze this case and output a JSON report.

Seed summary:
{_json(seed_report, limit=18000)}

Allowed file roots for tool inspection:
{_json([str(root) for root in allowed_roots])}

Required JSON schema:
{{
  "case_id": "...",
  "final_tier": "...",
  "diagnosis": {{
    "tg_success_or_failure_reason": "...",
    "bug_oracle_evidence_available": true,
    "triggering_behavior": "...",
    "tg_gap": "...",
    "confidence": "low|medium|high"
  }},
  "skill_usage": {{
    "retrieved": ["..."],
    "read": ["..."],
    "retrieval_events": [
      {{"tool": "search_skills|search_code_tags|list_code_tags|get_skills_by_code_tags|list_skills", "query": "...", "code_tags": ["..."], "returned_skills": ["..."], "assessment": "..."}}
    ],
    "followed": [{{"skill": "...", "assessment": "followed|partially_followed|ignored|unknown"}}],
    "helpfulness": [{{"skill": "...", "label": "helped|neutral|misleading|too_generic", "reason": "..."}}],
    "better_existing_skills": [{{"skill": "...", "why_better": "...", "metadata_fix": "..."}}]
  }},
  "proposed_operations": [
    {{"op": "ADD|MODIFY|MODIFY_META|MERGE|SPLIT|DEPRECATE", "skill": "...", "reason": "...", "patch": {{}}}}
  ],
  "tool_audit": {{
    "trajectory_steps_read": 0,
    "skills_read": 0,
    "analysis_agent_tools_used": ["..."],
    "tg_tools_observed_in_trajectory": ["..."],
    "missing_information": ["..."]
  }}
}}

Use read_case_seed_report/read_result_row/read_tool_trajectory first. Then inspect relevant skills.
In tool_audit, analysis_agent_tools_used must include only tools YOU called in this analysis run.
If you mention read_file/grep_code/write_test calls from TG's trajectory, put them under
tg_tools_observed_in_trajectory instead.
Return ONLY valid JSON.
"""


def _run_one_case_agent(
    idx_row: tuple[int, dict[str, Any]],
    *,
    skill_bank: dict[str, Any],
    output_dir: Path,
    model: str,
    max_tool_steps: int,
    top_k: int,
    allowed_roots: list[Path],
    context_compact_every: int,
) -> dict[str, Any]:
    idx, row = idx_row
    output_idx = int(row.get("idx") if row.get("idx") is not None else idx)
    seed_report = build_case_report(row)
    case_id = str(seed_report.get("case_id") or f"case-{idx}")
    case_name = safe_name(f"{output_idx:04d}_{case_id}")
    trace_path = output_dir / "traces" / f"{case_name}.jsonl"
    tools, executor, read_log = _case_tools(
        row=row,
        seed_report=seed_report,
        skill_bank=skill_bank,
        allowed_roots=allowed_roots,
        top_k=top_k,
    )
    content, agent_trajectory = _call_tool_agent(
        system=_case_system_prompt(),
        user=_case_user_prompt(seed_report, allowed_roots),
        tools=tools,
        executor=executor,
        model=model,
        max_tool_steps=max_tool_steps,
        max_tokens=4096,
        final_instruction="Return ONLY the final JSON case analysis report. No markdown, no prose.",
        trace_path=trace_path,
        context_compact_every=context_compact_every,
    )
    try:
        report = _extract_json_object(content)
        if not isinstance(report, dict):
            raise ValueError("case report is not an object")
    except Exception as exc:
        report = {
            "case_id": case_id,
            "final_tier": seed_report.get("final_tier"),
            "agent_parse_error": str(exc),
            "raw_output": content,
            "proposed_operations": [],
        }
    report.setdefault("case_id", case_id)
    report.setdefault("final_tier", seed_report.get("final_tier"))
    report["_deterministic_seed_report"] = seed_report
    report["_agent_trajectory"] = agent_trajectory
    report["_external_tool_audit"] = _trajectory_audit(agent_trajectory)
    report["_skill_read_log"] = read_log
    report["_trace_path"] = str(trace_path)
    write_json(output_dir / "case_reports" / f"{case_name}.json", report)
    return report


def _global_tools(
    *,
    reports: list[dict[str, Any]],
    skill_bank: dict[str, Any],
    allowed_roots: list[Path],
    top_k: int,
    max_skill_reads: int,
) -> tuple[list[dict[str, Any]], Callable[[str, dict[str, Any]], str | None], list[str]]:
    read_log: list[str] = []
    initial = skillbank_tools._search_skills(
        skill_bank,
        _json([{"case_id": r.get("case_id"), "tier": r.get("final_tier")} for r in reports], limit=12000),
        top_k=top_k,
        exclude_bug_key="",
    )
    skill_exec = skillbank_tools._make_skill_executor(
        skill_bank,
        initial,
        top_k=top_k,
        exclude_bug_key="",
        read_log=read_log,
    )
    file_tool_specs, file_exec = _file_tools(allowed_roots)
    tools = [
        {
            "type": "function",
            "function": {
                "name": "list_case_reports",
                "description": "List case report summaries and proposed operation counts.",
                "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "read_case_report",
                "description": "Read one full case report by case_id or index.",
                "parameters": {
                    "type": "object",
                    "properties": {"case_id": {"type": "string"}, "index": {"type": "integer"}},
                    "additionalProperties": False,
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "search_case_reports",
                "description": "Search case reports by keyword or final tier.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "default": ""},
                        "tier": {"type": "string", "default": ""},
                        "max_results": {"type": "integer", "default": 20},
                    },
                    "additionalProperties": False,
                },
            },
        },
    ] + skillbank_tools._skill_tool_specs() + file_tool_specs

    def _exec(name: str, args: dict[str, Any]) -> str | None:
        if name == "list_case_reports":
            rows = []
            for i, report in enumerate(reports):
                rows.append({
                    "index": i,
                    "case_id": report.get("case_id"),
                    "final_tier": report.get("final_tier"),
                    "ops": Counter(str(op.get("op") or "") for op in report.get("proposed_operations") or {}),
                    "skills_read": (report.get("skill_usage") or {}).get("read") or report.get("_skill_read_log") or [],
                })
            return _json({"reports": rows}, limit=40000)
        if name == "read_case_report":
            target = str(args.get("case_id") or "")
            index = args.get("index")
            report = None
            if target:
                for item in reports:
                    if str(item.get("case_id")) == target:
                        report = item
                        break
            if report is None and index is not None:
                i = int(index)
                if 0 <= i < len(reports):
                    report = reports[i]
            return _json(report or {"error": "case report not found"}, limit=60000)
        if name == "search_case_reports":
            query = str(args.get("query") or "").lower()
            tier = str(args.get("tier") or "")
            max_results = max(1, min(80, int(args.get("max_results") or 20)))
            rows = []
            for i, report in enumerate(reports):
                if tier and str(report.get("final_tier") or "") != tier:
                    continue
                haystack = json.dumps(report, ensure_ascii=False, default=str).lower()
                if query and query not in haystack:
                    continue
                rows.append({"index": i, "case_id": report.get("case_id"), "final_tier": report.get("final_tier"), "snippet": haystack[:1200]})
                if len(rows) >= max_results:
                    break
            return _json({"query": query, "tier": tier, "reports": rows}, limit=40000)
        if name == "read_skill" and max_skill_reads >= 0 and len(read_log) >= max_skill_reads:
            return (
                f"Skill read budget exhausted ({max_skill_reads}). Stop reading more skills and synthesize "
                "the global operation log from the case reports and already inspected skills."
            )
        obs = skill_exec(name, args)
        if obs is not None:
            return obs
        return file_exec(name, args)

    return tools, _exec, read_log


def _global_system_prompt() -> str:
    return (
        "You are the Global Evolution Agent for a Java testing SkillBank. "
        "Read multiple case reports and inspect the existing skills before proposing changes. "
        "Prefer ADD/MODIFY/MODIFY_META/MERGE/SPLIT. Avoid DEPRECATE unless strongly justified. "
        "Operations must be general training knowledge, not memorized eval bug facts."
    )


def _global_user_prompt(reports: list[dict[str, Any]], skill_bank_path: Path, *, max_skill_reads: int) -> str:
    summary = {
        "reports": len(reports),
        "tiers": dict(Counter(str(r.get("final_tier") or "UNKNOWN") for r in reports)),
        "case_ids": [r.get("case_id") for r in reports[:50]],
        "skill_bank": str(skill_bank_path),
    }
    return f"""
Build a small evolution operation log from this batch.

Batch summary:
{_json(summary)}

You have tools to list/read case reports and search/read the SkillBank.
Use the skill tools actively: inspect multiple candidate skills before proposing MODIFY/MODIFY_META/MERGE/SPLIT.
Use representative sampling rather than exhaustive browsing. Read at most {max_skill_reads} full skills.
Prefer reading:
- skills named in case report proposed operations;
- skills listed as better_existing_skills;
- skills repeatedly retrieved/read across cases;
- one or two candidates found by search_code_tags/search_skills for each shared failure pattern.
After reading enough representative skills, stop using tools and output operations.

Return ONLY valid JSON:
{{
  "global_diagnosis": "...",
  "skill_usage_findings": [
    {{"finding": "...", "supporting_cases": ["..."], "skills": ["..."]}}
  ],
  "operations": [
    {{"op": "ADD|MODIFY|MODIFY_META|MERGE|SPLIT|DEPRECATE", "skill": "...", "reason": "...", "patch": {{}}}}
  ],
  "tool_audit": {{
    "case_reports_read": 0,
    "skills_read": 0,
    "code_tag_tools_used": 0,
    "notes": ["..."]
  }}
}}

Keep the operation log compact:
- Return at most 8 operations for this debug run.
- Do not include markdown, fenced code blocks, or long Java examples inside patches.
- For ADD, use patch.name, patch.description, patch.guidance, patch.code_tags, patch.test_pattern, and patch.retrieval.
- Keep each patch.guidance under 900 characters.
- Prefer concise guidance over full skill documents; the apply step can create a first draft skill from it.
"""


def _load_case_reports(path: Path, max_reports: int = 0) -> list[dict[str, Any]]:
    files = sorted((path / "case_reports").glob("*.json")) if (path / "case_reports").is_dir() else sorted(path.glob("*.json"))
    reports = [read_json(file) for file in files if file.exists()]
    reports = [report for report in reports if isinstance(report, dict)]
    if max_reports > 0:
        reports = reports[:max_reports]
    return reports


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row, ensure_ascii=False, default=str) for row in rows) + ("\n" if rows else ""), encoding="utf-8")


def run_case_agents(args: argparse.Namespace) -> None:
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    skill_bank = skillbank_tools._load_skill_bank(args.skill_bank)
    rows = load_result_rows([Path(path) for path in args.results])
    if args.only_tier:
        wanted = set(args.only_tier)
        rows = [
            row for row in rows
            if str(row.get("final_tier_after_dependency_replay") or row.get("posthoc_final_tier") or row.get("final_tier") or "") in wanted
        ]
    if args.max_cases > 0:
        rows = rows[: args.max_cases]
    allowed_roots = [Path.cwd(), output_dir]
    allowed_roots.extend(Path(root) for root in args.allowed_root)
    for path in args.results:
        p = Path(path)
        allowed_roots.append(p if p.is_dir() else p.parent)
    write_json(output_dir / "case_agent_config.json", {
        "results": args.results,
        "skill_bank": args.skill_bank,
        "model": args.model,
        "max_cases": args.max_cases,
        "workers": args.workers,
        "only_tier": args.only_tier,
        "allowed_roots": [str(root) for root in allowed_roots],
    })
    reports: list[dict[str, Any]] = []
    indexed = list(enumerate(rows))
    if args.skip_existing:
        remaining: list[tuple[int, dict[str, Any]]] = []
        for idx, row in indexed:
            seed = build_case_report(row)
            output_idx = int(row.get("idx") if row.get("idx") is not None else idx)
            case_id = str(seed.get("case_id") or f"case-{idx}")
            case_name = safe_name(f"{output_idx:04d}_{case_id}")
            report_path = output_dir / "case_reports" / f"{case_name}.json"
            if report_path.exists():
                try:
                    reports.append(read_json(report_path))
                    continue
                except Exception:
                    pass
            remaining.append((idx, row))
        indexed = remaining
    if args.workers <= 1:
        for item in indexed:
            try:
                reports.append(_run_one_case_agent(
                    item,
                    skill_bank=skill_bank,
                    output_dir=output_dir,
                    model=args.model,
                    max_tool_steps=args.max_tool_steps,
                    top_k=args.top_k,
                    allowed_roots=allowed_roots,
                    context_compact_every=args.context_compact_every,
                ))
            except Exception as exc:
                reports.append(_write_case_error_report(item, output_dir, exc))
    else:
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            future_to_item = {
                pool.submit(
                    _run_one_case_agent,
                    item,
                    skill_bank=skill_bank,
                    output_dir=output_dir,
                    model=args.model,
                    max_tool_steps=args.max_tool_steps,
                    top_k=args.top_k,
                    allowed_roots=allowed_roots,
                    context_compact_every=args.context_compact_every,
                ): item
                for item in indexed
            }
            for future in as_completed(future_to_item):
                try:
                    reports.append(future.result())
                except Exception as exc:
                    reports.append(_write_case_error_report(future_to_item[future], output_dir, exc))
                print(f"[case-agent] completed {len(reports)}/{len(future_to_item)}")
    write_json(output_dir / "case_agent_summary.json", {
        "reports": len(reports),
        "tiers": dict(Counter(str(r.get("final_tier") or "UNKNOWN") for r in reports)),
        "parse_errors": sum(1 for r in reports if r.get("agent_parse_error")),
        "case_reports_dir": str(output_dir / "case_reports"),
    })
    print(f"[case-agent] wrote {len(reports)} reports to {output_dir / 'case_reports'}")


def _write_case_error_report(idx_row: tuple[int, dict[str, Any]], output_dir: Path, exc: Exception) -> dict[str, Any]:
    idx, row = idx_row
    output_idx = int(row.get("idx") if row.get("idx") is not None else idx)
    seed_report = build_case_report(row)
    case_id = str(seed_report.get("case_id") or f"case-{idx}")
    case_name = safe_name(f"{output_idx:04d}_{case_id}")
    report = {
        "case_id": case_id,
        "final_tier": seed_report.get("final_tier"),
        "agent_parse_error": f"case_agent_exception: {exc}",
        "proposed_operations": [],
        "_deterministic_seed_report": seed_report,
    }
    write_json(output_dir / "case_reports" / f"{case_name}.json", report)
    return report


def run_global_agent(args: argparse.Namespace) -> None:
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    skill_bank_path = Path(args.skill_bank)
    skill_bank = skillbank_tools._load_skill_bank(str(skill_bank_path))
    reports = _load_case_reports(Path(args.case_reports), max_reports=args.max_reports)
    allowed_roots = [Path.cwd(), output_dir, Path(args.case_reports)]
    allowed_roots.extend(Path(root) for root in args.allowed_root)
    tools, executor, read_log = _global_tools(
        reports=reports,
        skill_bank=skill_bank,
        allowed_roots=allowed_roots,
        top_k=args.top_k,
        max_skill_reads=args.max_skill_reads,
    )
    required_tool_min_counts: dict[str, int] = {}
    if args.min_case_reports_read > 0:
        required_tool_min_counts["read_case_report"] = args.min_case_reports_read
    if args.min_skill_reads > 0:
        required_tool_min_counts["read_skill"] = args.min_skill_reads
    trace_path = output_dir / "global_agent_trace.jsonl"
    content, trajectory = _call_tool_agent(
        system=_global_system_prompt(),
        user=_global_user_prompt(reports, skill_bank_path, max_skill_reads=args.max_skill_reads),
        tools=tools,
        executor=executor,
        model=args.model,
        max_tool_steps=args.max_tool_steps,
        max_tokens=args.max_tokens,
        final_instruction="Return ONLY the final JSON object with operations. No markdown, no prose.",
        trace_path=trace_path,
        context_compact_every=args.context_compact_every,
        required_tool_min_counts=required_tool_min_counts,
        required_tool_hint=(
            "Inspect a broad cross-tier sample before proposing global operations: BUG_DETECTED, PASS_BOTH, "
            "FAIL_ON_FIXED, COMPILE_FAIL, NO_TEST_GENERATED, and INFRA_RUNTIME_FAIL. Read skills named in "
            "proposed operations, skill_usage, and better_existing_skills before deciding ADD/MODIFY/"
            "MODIFY_META/MERGE/SPLIT."
        ),
    )
    try:
        payload = _extract_json_object(content)
        if not isinstance(payload, dict):
            raise ValueError("global output is not an object")
    except Exception as exc:
        payload = {"agent_parse_error": str(exc), "raw_output": content, "operations": []}
    payload["_agent_trajectory"] = trajectory
    payload["_external_tool_audit"] = _trajectory_audit(trajectory)
    payload["_skill_read_log"] = read_log
    payload["_trace_path"] = str(trace_path)
    write_json(output_dir / "global_evolution_agent_report.json", payload)
    ops = [op for op in (payload.get("operations") or []) if isinstance(op, dict)]
    _write_jsonl(output_dir / "evolution_ops.jsonl", ops)
    if args.apply:
        summary = apply_ops_to_skill_bank(skill_bank_path, ops, output_dir / "evolved_skillbank_snapshot")
        write_json(output_dir / "apply_summary.json", summary)
    print(f"[global-agent] reports={len(reports)} ops={len(ops)} output={output_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run SkillBank evolution LLM agents")
    sub = parser.add_subparsers(dest="cmd", required=True)

    case = sub.add_parser("case-agents")
    case.add_argument("--results", action="append", required=True)
    case.add_argument("--skill-bank", required=True)
    case.add_argument("--output", required=True)
    case.add_argument("--model", default=DEFAULT_MODEL)
    case.add_argument("--max-cases", type=int, default=3)
    case.add_argument("--only-tier", action="append", default=[])
    case.add_argument("--workers", type=int, default=1)
    case.add_argument("--max-tool-steps", type=int, default=12)
    case.add_argument("--top-k", type=int, default=10)
    case.add_argument("--context-compact-every", type=int, default=100)
    case.add_argument("--allowed-root", action="append", default=[])
    case.add_argument("--skip-existing", action="store_true")
    case.set_defaults(func=run_case_agents)

    glob = sub.add_parser("global-agent")
    glob.add_argument("--case-reports", required=True)
    glob.add_argument("--skill-bank", required=True)
    glob.add_argument("--output", required=True)
    glob.add_argument("--model", default=DEFAULT_MODEL)
    glob.add_argument("--max-reports", type=int, default=8)
    glob.add_argument("--max-tool-steps", type=int, default=18)
    glob.add_argument("--max-tokens", type=int, default=8192)
    glob.add_argument("--top-k", type=int, default=12)
    glob.add_argument("--max-skill-reads", type=int, default=20)
    glob.add_argument("--min-case-reports-read", type=int, default=0)
    glob.add_argument("--min-skill-reads", type=int, default=0)
    glob.add_argument("--context-compact-every", type=int, default=100)
    glob.add_argument("--allowed-root", action="append", default=[])
    glob.add_argument("--apply", action="store_true")
    glob.set_defaults(func=run_global_agent)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

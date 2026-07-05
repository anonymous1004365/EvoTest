#!/usr/bin/env python3
"""Internal finalization pass for the initial SkillBank builder.

This module is intentionally conservative:
- keep first-pass evidence immutable;
- normalize parseable Stage 2 outputs from failed first-pass trajectories;
- retry only unresolved cases, preserving the same extraction pipeline.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import threading
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PACKAGE_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from code_tag_registry import CodeTagRegistry
from skill_agent import (
    ExtractionInput,
    _validate_skill_data,
    parse_skill_markdown,
    run_skill_agent,
)
from skill_bank import write_skill_bank
from skill_model import Skill, TEST_PATTERNS


DATASET_EXCLUDE = {"gitbug-java"}
PATTERN_ALIASES = {
    "PARAMETERIZED_TEST": "PARAMETRIC_TEST",
    "PARAMETERIC_TEST": "PARAMETRIC_TEST",
    "PARAMETERISED_TEST": "PARAMETRIC_TEST",
}


def now() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S")


def safe_name(s: str) -> str:
    return "".join(c if c.isalnum() or c in "._-" else "_" for c in s)[:180]


def load_rows(input_path: Path) -> list[dict[str, Any]]:
    data = json.loads(input_path.read_text(encoding="utf-8"))
    rows = data.get("focal_methods") if isinstance(data, dict) else data
    return [r for r in rows if r.get("dataset") not in DATASET_EXCLUDE]


def key_for(fm: dict[str, Any], idx: int) -> str:
    return fm.get("focal_method_key") or f"{fm.get('dataset','unknown')}/{fm.get('bug_id','unknown')}/{idx}"


def make_input(fm: dict[str, Any]) -> ExtractionInput:
    return ExtractionInput(
        bug_id=fm.get("bug_id", ""),
        project=fm.get("project", ""),
        focal_class=fm.get("focal_class", ""),
        focal_method=fm.get("focal_method", ""),
        focal_method_sig=fm.get("focal_method_sig", ""),
        focal_file=fm.get("focal_file", ""),
        buggy_code=fm.get("buggy_code", ""),
        fixed_code=fm.get("fixed_code", ""),
        diff=fm.get("diff", ""),
        failing_test_class=fm.get("failing_test_class", ""),
        failing_test_method=fm.get("failing_test_method", ""),
        failure_message=fm.get("failure_message", ""),
        test_patch=fm.get("test_patch", ""),
        clone_url=fm.get("clone_url", ""),
        buggy_version=fm.get("buggy_version", ""),
        fixed_version=fm.get("fixed_version", ""),
        dataset=fm.get("dataset", ""),
        focal_method_idx=int(fm.get("focal_method_idx") or 0),
    )


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    if not path.exists():
        return rows
    with path.open(encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def normalize_pattern(pattern: str | None) -> str:
    value = (pattern or "PARAMETRIC_TEST").strip().strip('"').strip("'").upper()
    value = PATTERN_ALIASES.get(value, value)
    return value if value in TEST_PATTERNS else "PARAMETRIC_TEST"


def iter_tool_calls(obj: Any):
    if isinstance(obj, dict):
        if obj.get("type") == "function" and "function" in obj:
            yield obj
        for value in obj.values():
            yield from iter_tool_calls(value)
    elif isinstance(obj, list):
        for item in obj:
            yield from iter_tool_calls(item)


def collect_selected_tags(trajectory: list[dict[str, Any]]) -> dict[str, list[str]]:
    selected: dict[str, list[str]] = {}
    for call in iter_tool_calls(trajectory):
        fn = call.get("function") or {}
        if fn.get("name") != "select_code_tags":
            continue
        args = fn.get("arguments") or {}
        if isinstance(args, str):
            try:
                args = json.loads(args)
            except json.JSONDecodeError:
                continue
        if not isinstance(args, dict):
            continue
        phase = args.get("phase")
        tags = args.get("tags")
        if phase and isinstance(tags, list) and tags:
            selected[phase] = [str(t) for t in tags][:3]
    return selected


def stage2_output_candidates(trajectory: list[dict[str, Any]]) -> list[str]:
    candidates: list[str] = []

    def add(value: Any) -> None:
        if value is None:
            return
        if isinstance(value, (dict, list)):
            text = json.dumps(value, ensure_ascii=False)
        else:
            text = str(value)
        if text.strip():
            candidates.append(text)
            marker = "---\nname:"
            idx = text.find(marker)
            if idx > 0:
                candidates.append(text[idx:])
            fenced_marker = "```\n---\nname:"
            idx = text.find(fenced_marker)
            if idx > 0:
                candidates.append(text[idx + 4 :])

    for record in trajectory:
        if record.get("phase") != "stage2_oracle":
            continue
        for key in ("parsed", "model_output", "final_answer"):
            add(record.get(key))
        for step in record.get("steps") or []:
            if not isinstance(step, dict):
                continue
            for key in ("final_answer", "model_output_raw", "model_output"):
                add(step.get(key))

    # Longest outputs are usually full SKILL.md attempts. Keep order stable but
    # try richer candidates first.
    seen = set()
    unique = []
    for text in sorted(candidates, key=len, reverse=True):
        if text in seen:
            continue
        seen.add(text)
        unique.append(text)
    return unique


def parse_normalized_skill(
    *,
    row: dict[str, Any],
    fm: dict[str, Any],
    trajectory: list[dict[str, Any]],
) -> tuple[Skill | None, str]:
    selected = collect_selected_tags(trajectory)
    for candidate in stage2_output_candidates(trajectory):
        parsed, err = parse_skill_markdown(candidate)
        if not parsed:
            continue
        skill_data = dict(parsed)
        skill_data["id"] = row["skill_id"]
        skill_data.setdefault("source", {})
        skill_data["source"]["dataset"] = row.get("dataset", fm.get("dataset", ""))
        skill_data["source"]["bug_id"] = row.get("bug_id", fm.get("bug_id", ""))
        skill_data["source"]["focal_method_idx"] = int(fm.get("focal_method_idx") or 0)
        skill_data["focal_class"] = row.get("focal_class", fm.get("focal_class", ""))
        skill_data["focal_method"] = row.get("focal_method", fm.get("focal_method", ""))
        skill_data["focal_method_sig"] = fm.get("focal_method_sig", "")
        skill_data["confidence"] = float(skill_data.get("confidence", 0.8) or 0.8)
        skill_data["test_pattern"] = normalize_pattern(skill_data.get("test_pattern"))

        merged_tags = list(
            dict.fromkeys(
                selected.get("stage1_perceived", [])
                + selected.get("root_cause_tags", [])
                + list(skill_data.get("code_tags") or [])
            )
        )
        skill_data["code_tags"] = [str(t) for t in merged_tags[:3]]

        validation_error = _validate_skill_data(skill_data)
        if validation_error:
            continue
        try:
            return Skill.from_dict(skill_data), ""
        except Exception as exc:
            return None, f"{type(exc).__name__}: {exc}"
    return None, "not_parseable"


class InitialSkillBankFinalizationRun:
    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.run_dir = Path(args.run_dir)
        self.input_path = Path(args.input)
        self.out_dir = Path(args.out_dir)
        self.records_dir = self.out_dir / "records"
        self.traj_dir = self.out_dir / "trajectories"
        self.case_logs_dir = self.out_dir / "case_logs"
        self.summary_path = self.out_dir / "summary.jsonl"
        self.progress_path = self.out_dir / "progress.json"
        self.skills_latest_path = self.out_dir / "skills_latest.json"
        self.registry_path = self.out_dir / "code_tags_registry.json"
        self.lock = threading.RLock()
        self.rows = load_rows(self.input_path)
        limit = int(getattr(args, "limit", 0) or 0)
        if limit > 0:
            self.rows = self.rows[:limit]
        self.row_by_key = {key_for(fm, idx): (idx, fm) for idx, fm in enumerate(self.rows)}
        self.records_by_key: dict[str, dict[str, Any]] = {}
        self.skills_by_key: dict[str, Skill] = {}
        self.started_at = time.time()

    def setup(self) -> None:
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.records_dir.mkdir(exist_ok=True)
        self.traj_dir.mkdir(exist_ok=True)
        self.case_logs_dir.mkdir(exist_ok=True)
        source_registry = self.run_dir / "code_tags_registry.json"
        if self.registry_path.exists():
            CodeTagRegistry._instance = CodeTagRegistry.load(self.registry_path)
        elif source_registry.exists():
            CodeTagRegistry._instance = CodeTagRegistry.load(source_registry)

        for rec in load_jsonl(self.summary_path):
            self.records_by_key[rec["key"]] = rec
            if rec.get("skill"):
                try:
                    self.skills_by_key[rec["key"]] = Skill.from_dict(rec["skill"])
                except Exception:
                    pass

    def seed_first_pass_successes(self) -> None:
        for rec in load_jsonl(self.run_dir / "summary.jsonl"):
            key = rec.get("key")
            if not key or key in self.records_by_key:
                continue
            if rec.get("skill"):
                self.records_by_key[key] = {**rec, "build_status": "accepted_first_pass"}
                self.skills_by_key[key] = Skill.from_dict(rec["skill"])

    def normalize_parseable_first_pass_failures(self) -> tuple[int, int]:
        normalized = 0
        scanned = 0
        for rec in load_jsonl(self.run_dir / "summary.jsonl"):
            key = rec.get("key")
            if not key or key in self.skills_by_key or not rec.get("error"):
                continue
            scanned += 1
            idx_fm = self.row_by_key.get(key)
            if not idx_fm:
                continue
            _, fm = idx_fm
            trajectory = load_jsonl(Path(rec.get("trajectory_path", "")))
            skill, reason = parse_normalized_skill(row=rec, fm=fm, trajectory=trajectory)
            if not skill:
                self.records_by_key.setdefault(
                    key,
                    {**rec, "build_status": "unresolved_first_pass", "build_error": reason},
                )
                continue
            new_rec = {
                **rec,
                "error": None,
                "skill": skill.to_dict(),
                "build_status": "accepted_from_parse_normalization",
                "first_pass_error": rec.get("error"),
            }
            self.records_by_key[key] = new_rec
            self.skills_by_key[key] = skill
            normalized += 1
        return scanned, normalized

    def unresolved_keys(self) -> list[str]:
        keys = []
        for key in self.row_by_key:
            if key not in self.skills_by_key:
                keys.append(key)
        return keys

    def save(self) -> None:
        ordered_records = []
        for idx, fm in enumerate(self.rows):
            key = key_for(fm, idx)
            if key in self.records_by_key:
                ordered_records.append(self.records_by_key[key])
        tmp = self.summary_path.with_suffix(".jsonl.tmp")
        with tmp.open("w", encoding="utf-8") as f:
            for rec in ordered_records:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        tmp.replace(self.summary_path)

        ordered_skills = [
            self.skills_by_key[key_for(fm, idx)]
            for idx, fm in enumerate(self.rows)
            if key_for(fm, idx) in self.skills_by_key
        ]
        self.skills_latest_path.write_text(
            json.dumps([s.to_dict() for s in ordered_skills], indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        CodeTagRegistry.get_instance().save(self.registry_path)
        write_skill_bank(ordered_skills, self.out_dir)
        self.write_progress()

    def write_progress(self) -> None:
        total = len(self.rows)
        ok = len(self.skills_by_key)
        done = len(self.records_by_key)
        failed = total - ok
        payload = {
            "updated_at": now(),
            "pid": os.getpid(),
            "mode": "initial_skillbank_finalize",
            "workers": self.args.workers,
            "source_run_dir": str(self.run_dir),
            "input_path": str(self.input_path),
            "output_dir": str(self.out_dir),
            "total": total,
            "done": done,
            "ok": ok,
            "failed": failed,
            "pending": len(self.unresolved_keys()),
            "elapsed_seconds": round(time.time() - self.started_at, 2),
            "code_tag_count": len(CodeTagRegistry.get_instance().all_tags()),
        }
        self.progress_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    def retry_one(self, key: str, round_idx: int) -> tuple[str, dict[str, Any], Skill | None]:
        idx, fm = self.row_by_key[key]
        skill_id = f"initial_skill_{idx + 1:04d}"
        base = f"retry{round_idx}_{idx + 1:04d}_{safe_name(key)}"
        case_log_path = self.case_logs_dir / f"{base}.log"
        traj_path = self.traj_dir / f"{base}.jsonl"
        record_path = self.records_dir / f"{base}.json"
        t0 = time.time()
        record = {
            "index": idx,
            "skill_id": skill_id,
            "key": key,
            "dataset": fm.get("dataset", ""),
            "bug_id": fm.get("bug_id", ""),
            "focal_class": fm.get("focal_class", ""),
            "focal_method": fm.get("focal_method", ""),
            "started_at": now(),
            "elapsed_seconds": None,
            "error": None,
            "skill": None,
            "trajectory_path": str(traj_path),
            "case_log_path": str(case_log_path),
            "build_status": f"retry_round_{round_idx}_attempt",
        }

        def trajectory_callback(step_record: dict[str, Any]) -> None:
            with traj_path.open("a", encoding="utf-8") as tf:
                tf.write(json.dumps(step_record, ensure_ascii=False) + "\n")

        skill = None
        try:
            skill, trajectory, error = run_skill_agent(
                make_input(fm),
                skill_id=skill_id,
                max_steps=self.args.max_steps_s1,
                max_steps_s2=self.args.max_steps_s2,
                compress_every_s1=self.args.compress_every_s1,
                compress_every_s2=self.args.compress_every_s2,
                trajectory_callback=trajectory_callback,
                timeout=self.args.timeout,
                max_retries=self.args.max_retries,
                use_phase_a=getattr(self.args, "use_phase_a", True),
            )
            if not skill and trajectory:
                normalized_skill, reason = parse_normalized_skill(row=record, fm=fm, trajectory=trajectory)
                if normalized_skill:
                    skill = normalized_skill
                    error = None
                    record["build_status"] = f"accepted_after_retry_round_{round_idx}_parse_normalization"
                else:
                    record["build_error"] = reason
            record["elapsed_seconds"] = round(time.time() - t0, 2)
            if skill:
                record["skill"] = skill.to_dict()
                if record.get("build_status") == f"retry_round_{round_idx}_attempt":
                    record["build_status"] = f"accepted_after_retry_round_{round_idx}"
            else:
                record["error"] = error or "retry returned no skill"
                record["build_status"] = f"failed_after_retry_round_{round_idx}"
        except Exception as exc:
            record["elapsed_seconds"] = round(time.time() - t0, 2)
            record["error"] = f"{type(exc).__name__}: {exc}"
            case_log_path.write_text(traceback.format_exc(), encoding="utf-8")
        finally:
            record["finished_at"] = now()
            record["code_tag_count"] = len(CodeTagRegistry.get_instance().all_tags())
            record_path.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
        return key, record, skill

    def retry_unresolved(self) -> None:
        if self.args.rounds <= 0:
            return
        for round_idx in range(1, self.args.rounds + 1):
            keys = self.unresolved_keys()
            if not keys:
                break
            print(f"[{now()}] retry round {round_idx}: unresolved={len(keys)} workers={self.args.workers}", flush=True)
            with ThreadPoolExecutor(max_workers=self.args.workers) as executor:
                futures = [executor.submit(self.retry_one, key, round_idx) for key in keys]
                for fut in as_completed(futures):
                    key, record, skill = fut.result()
                    with self.lock:
                        if skill:
                            self.records_by_key[key] = record
                            self.skills_by_key[key] = skill
                            print(f"[{now()}] OK {key} {skill.name}", flush=True)
                        else:
                            self.records_by_key[key] = record
                            print(f"[{now()}] FAIL {key} {record.get('error')}", flush=True)
                        self.save()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--input", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--workers", type=int, default=int(os.environ.get("WORKERS", "8")))
    parser.add_argument("--rounds", type=int, default=1)
    parser.add_argument("--limit", type=int, default=0, help="Optional smoke-test case limit")
    parser.add_argument("--max-steps-s1", type=int, default=int(os.environ.get("MAX_STEPS_S1", "80")))
    parser.add_argument("--max-steps-s2", type=int, default=int(os.environ.get("MAX_STEPS_S2", "100")))
    parser.add_argument("--compress-every-s1", type=int, default=int(os.environ.get("COMPRESS_EVERY_S1", "10")))
    parser.add_argument("--compress-every-s2", type=int, default=int(os.environ.get("COMPRESS_EVERY_S2", "15")))
    parser.add_argument("--timeout", type=int, default=int(os.environ.get("CASE_TIMEOUT", "240")))
    parser.add_argument("--max-retries", type=int, default=int(os.environ.get("MAX_RETRIES", "1")))
    parser.add_argument(
        "--compat-stage1",
        dest="use_phase_a",
        action="store_false",
        help="Use the old Stage 1 prompt/tool set instead of fixed-only Phase A",
    )
    parser.set_defaults(use_phase_a=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.workers > 32:
        raise SystemExit("--workers must be <= 32")
    if args.rounds > 0 and not os.environ.get("LLM_API_KEY"):
        raise SystemExit("LLM_API_KEY is not set")

    run = InitialSkillBankFinalizationRun(args)
    run.setup()
    run.seed_first_pass_successes()
    scanned, normalized = run.normalize_parseable_first_pass_failures()
    run.save()
    print(
        f"[{now()}] seeded={len(run.skills_by_key)} scanned_failures={scanned} "
        f"normalized={normalized} unresolved={len(run.unresolved_keys())}",
        flush=True,
    )
    run.retry_unresolved()
    run.save()

    unresolved = len(run.unresolved_keys())
    if unresolved == 0:
        (run.out_dir / "DONE").write_text(now() + "\n", encoding="utf-8")
    print(
        f"[{now()}] COMPLETE ok={len(run.skills_by_key)} failed={unresolved} out={run.out_dir}",
        flush=True,
    )


if __name__ == "__main__":
    main()

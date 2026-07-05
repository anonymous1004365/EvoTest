#!/usr/bin/env python3
"""Internal first-pass extraction for the initial SkillBank builder.

This module creates the immutable first-pass evidence consumed by
``build_initial_skillbank.py``:

  output/
    summary.jsonl
    progress.json
    skills_latest.json
    code_tags_registry.json
    records/*.json
    trajectories/*.jsonl
    skill_bank/

The public builder may then normalize parseable failed trajectories and retry
only unresolved cases without overwriting the first-pass evidence.
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
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SRC_DIR))
sys.path.insert(0, str(SCRIPT_DIR))

from code_tag_registry import CodeTagRegistry  # noqa: E402
from _initial_skillbank_finalize import key_for, load_rows, make_input, safe_name  # noqa: E402
from skill_agent import run_skill_agent  # noqa: E402
from skill_bank import write_skill_bank  # noqa: E402
from skill_model import Skill  # noqa: E402


def now() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S")


class InitialExtractionRun:
    def __init__(self, args: argparse.Namespace):
        self.args = args
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
        if args.limit is not None:
            self.rows = self.rows[: args.limit]
        self.records_by_key: dict[str, dict[str, Any]] = {}
        self.skills_by_key: dict[str, Skill] = {}
        self.started_at = time.time()

    def setup(self) -> None:
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.records_dir.mkdir(exist_ok=True)
        self.traj_dir.mkdir(exist_ok=True)
        self.case_logs_dir.mkdir(exist_ok=True)
        if self.registry_path.exists():
            CodeTagRegistry._instance = CodeTagRegistry.load(self.registry_path)

        if self.args.resume and self.summary_path.exists():
            with self.summary_path.open(encoding="utf-8", errors="replace") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        rec = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    key = rec.get("key")
                    if not key:
                        continue
                    self.records_by_key[key] = rec
                    if rec.get("skill"):
                        try:
                            self.skills_by_key[key] = Skill.from_dict(rec["skill"])
                        except Exception:
                            pass

    def save(self) -> None:
        ordered_records = []
        for idx, fm in enumerate(self.rows):
            key = key_for(fm, idx)
            rec = self.records_by_key.get(key)
            if rec:
                ordered_records.append(rec)

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
        done = len(self.records_by_key)
        ok = len(self.skills_by_key)
        payload = {
            "updated_at": now(),
            "pid": os.getpid(),
            "mode": "initial_skillbank_raw_extraction",
            "input_path": str(self.input_path),
            "output_dir": str(self.out_dir),
            "workers": self.args.workers,
            "total": total,
            "done": done,
            "ok": ok,
            "failed": done - ok,
            "pending": total - done,
            "elapsed_seconds": round(time.time() - self.started_at, 2),
            "use_phase_a": self.args.use_phase_a,
            "code_tag_count": len(CodeTagRegistry.get_instance().all_tags()),
        }
        self.progress_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    def pending_items(self) -> list[tuple[int, dict[str, Any]]]:
        items = []
        for idx, fm in enumerate(self.rows):
            key = key_for(fm, idx)
            if self.args.resume and key in self.records_by_key:
                continue
            items.append((idx, fm))
        return items

    def run_one(self, idx: int, fm: dict[str, Any]) -> tuple[str, dict[str, Any], Skill | None]:
        key = key_for(fm, idx)
        skill_id = f"initial_skill_{idx + 1:04d}"
        base = f"{idx + 1:04d}_{safe_name(key)}"
        traj_path = self.traj_dir / f"{base}.jsonl"
        record_path = self.records_dir / f"{base}.json"
        case_log_path = self.case_logs_dir / f"{base}.log"
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
            "extraction_status": "raw_extraction",
        }

        if traj_path.exists() and not self.args.keep_existing_trajectories:
            traj_path.unlink()

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
                use_phase_a=self.args.use_phase_a,
            )
            if skill:
                record["skill"] = skill.to_dict()
            else:
                record["error"] = error or "run_skill_agent returned no skill"
                if trajectory and not traj_path.exists():
                    for step_record in trajectory:
                        trajectory_callback(step_record)
        except Exception as exc:
            record["error"] = f"{type(exc).__name__}: {exc}"
            case_log_path.write_text(traceback.format_exc(), encoding="utf-8")
        finally:
            record["elapsed_seconds"] = round(time.time() - t0, 2)
            record["finished_at"] = now()
            record["code_tag_count"] = len(CodeTagRegistry.get_instance().all_tags())
            record_path.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
        return key, record, skill

    def run(self) -> None:
        items = self.pending_items()
        print(f"[{now()}] raw extraction pending={len(items)} workers={self.args.workers}", flush=True)
        with ThreadPoolExecutor(max_workers=self.args.workers) as executor:
            futures = [executor.submit(self.run_one, idx, fm) for idx, fm in items]
            for future in as_completed(futures):
                key, record, skill = future.result()
                with self.lock:
                    self.records_by_key[key] = record
                    if skill:
                        self.skills_by_key[key] = skill
                        print(f"[{now()}] OK {key} {skill.name}", flush=True)
                    else:
                        print(f"[{now()}] FAIL {key} {record.get('error')}", flush=True)
                    self.save()
        self.save()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the raw initial SkillBank extraction pass")
    parser.add_argument("--input", required=True, help="Focal-method dataset JSON")
    parser.add_argument("--out-dir", required=True, help="Output directory for raw extraction evidence")
    parser.add_argument("--workers", type=int, default=int(os.environ.get("WORKERS", "8")))
    parser.add_argument("--limit", type=int, default=None, help="Optional smoke-test case limit")
    parser.add_argument("--max-steps-s1", type=int, default=int(os.environ.get("MAX_STEPS_S1", "80")))
    parser.add_argument("--max-steps-s2", type=int, default=int(os.environ.get("MAX_STEPS_S2", "100")))
    parser.add_argument("--compress-every-s1", type=int, default=int(os.environ.get("COMPRESS_EVERY_S1", "10")))
    parser.add_argument("--compress-every-s2", type=int, default=int(os.environ.get("COMPRESS_EVERY_S2", "15")))
    parser.add_argument("--timeout", type=int, default=int(os.environ.get("CASE_TIMEOUT", "240")))
    parser.add_argument("--max-retries", type=int, default=int(os.environ.get("MAX_RETRIES", "1")))
    parser.add_argument("--resume", action="store_true", help="Skip records already present in summary.jsonl")
    parser.add_argument(
        "--compat-stage1",
        dest="use_phase_a",
        action="store_false",
        help="Use the old Stage 1 prompt/tool set instead of fixed-only Phase A",
    )
    parser.add_argument(
        "--keep-existing-trajectories",
        action="store_true",
        help="Append to existing trajectory files instead of replacing them for rerun cases",
    )
    parser.set_defaults(use_phase_a=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.workers > 32:
        raise SystemExit("--workers must be <= 32")
    if not os.environ.get("LLM_API_KEY"):
        raise SystemExit("LLM_API_KEY is not set")

    run = InitialExtractionRun(args)
    run.setup()
    run.run()

    unresolved = len(run.rows) - len(run.skills_by_key)
    if unresolved == 0:
        (run.out_dir / "DONE").write_text(now() + "\n", encoding="utf-8")
    print(
        f"[{now()}] COMPLETE ok={len(run.skills_by_key)} failed={unresolved} out={run.out_dir}",
        flush=True,
    )


if __name__ == "__main__":
    main()

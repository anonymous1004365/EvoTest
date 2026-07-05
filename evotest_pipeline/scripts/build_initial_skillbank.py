#!/usr/bin/env python3
"""Build the initial SkillBank in one reproducible command.

The public final-pipeline entry point intentionally hides the first-pass/finalize
split behind one builder. It still preserves first-pass evidence under
``internal/first_pass`` for auditability, while the user-facing output directory
contains the finalized SkillBank and build report.
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
import os
import sys
import time
from pathlib import Path
from types import SimpleNamespace
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from _initial_skillbank_finalize import InitialSkillBankFinalizationRun, load_jsonl  # noqa: E402
from _initial_skillbank_raw_extraction import InitialExtractionRun  # noqa: E402


def now() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S")


def _status_counts(summary_path: Path) -> dict[str, int]:
    counts = Counter()
    for rec in load_jsonl(summary_path):
        status = rec.get("build_status") or rec.get("extraction_status") or "unknown"
        counts[str(status)] += 1
    return dict(sorted(counts.items()))


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the initial SkillBank")
    parser.add_argument("--input", required=True, help="Focal-method dataset JSON")
    parser.add_argument("--out-dir", required=True, help="Final output directory")
    parser.add_argument("--workers", type=int, default=int(os.environ.get("WORKERS", "8")))
    parser.add_argument("--limit", type=int, default=None, help="Optional smoke-test case limit")
    parser.add_argument("--finalize-rounds", type=int, default=1, help="Retry rounds for unresolved cases")
    parser.add_argument("--max-steps-s1", type=int, default=int(os.environ.get("MAX_STEPS_S1", "80")))
    parser.add_argument("--max-steps-s2", type=int, default=int(os.environ.get("MAX_STEPS_S2", "100")))
    parser.add_argument("--compress-every-s1", type=int, default=int(os.environ.get("COMPRESS_EVERY_S1", "10")))
    parser.add_argument("--compress-every-s2", type=int, default=int(os.environ.get("COMPRESS_EVERY_S2", "15")))
    parser.add_argument("--timeout", type=int, default=int(os.environ.get("CASE_TIMEOUT", "240")))
    parser.add_argument("--max-retries", type=int, default=int(os.environ.get("MAX_RETRIES", "1")))
    parser.add_argument("--resume", action="store_true", help="Reuse existing first-pass/final outputs")
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
    if not os.environ.get("LLM_API_KEY"):
        raise SystemExit("LLM_API_KEY is not set")

    out_dir = Path(args.out_dir)
    internal_dir = out_dir / "internal"
    first_pass_dir = internal_dir / "first_pass"
    out_dir.mkdir(parents=True, exist_ok=True)
    internal_dir.mkdir(exist_ok=True)

    started_at = now()
    started = time.time()
    first_pass_args = SimpleNamespace(
        input=args.input,
        out_dir=str(first_pass_dir),
        workers=args.workers,
        limit=args.limit,
        max_steps_s1=args.max_steps_s1,
        max_steps_s2=args.max_steps_s2,
        compress_every_s1=args.compress_every_s1,
        compress_every_s2=args.compress_every_s2,
        timeout=args.timeout,
        max_retries=args.max_retries,
        resume=args.resume,
        use_phase_a=args.use_phase_a,
        keep_existing_trajectories=False,
    )
    first_pass = InitialExtractionRun(first_pass_args)
    first_pass.setup()
    first_pass.run()

    finalize_args = SimpleNamespace(
        run_dir=str(first_pass_dir),
        input=args.input,
        out_dir=str(out_dir),
        workers=args.workers,
        rounds=args.finalize_rounds,
        limit=args.limit,
        max_steps_s1=args.max_steps_s1,
        max_steps_s2=args.max_steps_s2,
        compress_every_s1=args.compress_every_s1,
        compress_every_s2=args.compress_every_s2,
        timeout=args.timeout,
        max_retries=args.max_retries,
        use_phase_a=args.use_phase_a,
    )
    finalizer = InitialSkillBankFinalizationRun(finalize_args)
    finalizer.setup()
    finalizer.seed_first_pass_successes()
    scanned, normalized = finalizer.normalize_parseable_first_pass_failures()
    finalizer.save()
    print(
        f"[{now()}] first-pass failures scanned={scanned} "
        f"parse-normalized={normalized} unresolved={len(finalizer.unresolved_keys())}",
        flush=True,
    )
    finalizer.retry_unresolved()
    finalizer.save()

    unresolved = len(finalizer.unresolved_keys())
    if unresolved == 0:
        (out_dir / "DONE").write_text(now() + "\n", encoding="utf-8")

    first_progress = _read_json(first_pass_dir / "progress.json")
    final_progress = _read_json(out_dir / "progress.json")
    report = {
        "mode": "build_initial_skillbank",
        "started_at": started_at,
        "finished_at": now(),
        "elapsed_seconds": round(time.time() - started, 2),
        "input_path": str(Path(args.input)),
        "output_dir": str(out_dir),
        "skill_bank_dir": str(out_dir / "skill_bank"),
        "internal_first_pass_dir": str(first_pass_dir),
        "workers": args.workers,
        "limit": args.limit,
        "use_phase_a": args.use_phase_a,
        "finalize_rounds": args.finalize_rounds,
        "first_pass": first_progress,
        "final": final_progress,
        "final_status_counts": _status_counts(out_dir / "summary.jsonl"),
    }
    (out_dir / "build_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(
        f"[{now()}] COMPLETE ok={final_progress.get('ok')} "
        f"failed={final_progress.get('failed')} out={out_dir}",
        flush=True,
    )


if __name__ == "__main__":
    main()

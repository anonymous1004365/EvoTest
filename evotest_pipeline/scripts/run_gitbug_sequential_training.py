#!/usr/bin/env python3
"""Sequential GitBug-Java SkillBank training loop.

This orchestrator keeps the generated-suite TG and SkillBank evolution agents
unchanged, and adds the outer loop:

    working SkillBank -> GitBug batch 000 -> evolve -> overwrite working SkillBank
    working SkillBank -> GitBug batch 001 -> evolve -> overwrite working SkillBank
    ...

Each batch is archived independently, but the SkillBank itself is maintained as
one mutable working directory under ``output_root/skill_bank``.  Global
evolution output is applied by replacing that working directory in place; the
temporary evolved snapshot produced by the global agent is removed afterwards.
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent


def _now_tag() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8", errors="replace"))


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, default=str), encoding="utf-8")


def _load_dataset(path: Path) -> list[dict[str, Any]]:
    payload = _read_json(path)
    records = payload.get("focal_methods") if isinstance(payload, dict) else payload
    if not isinstance(records, list):
        raise ValueError("Dataset must be a list or an object with focal_methods")
    return [dict(item) for item in records if isinstance(item, dict)]


def _record_key(record: dict[str, Any], idx: int) -> str:
    bug_id = record.get("bug_id") or record.get("source_id") or record.get("bid") or f"record-{idx}"
    method = record.get("method_name") or record.get("focal_method") or record.get("focal_method_sig") or "focal"
    return f"{bug_id}::{str(method).split('(')[0].split('.')[-1]}"


def _build_schedule(
    records: list[dict[str, Any]],
    *,
    epochs: int,
    batch_size: int,
    max_records: int,
    max_batches: int,
) -> list[list[tuple[int, int, dict[str, Any]]]]:
    if max_records > 0:
        records = records[:max_records]
    stream: list[tuple[int, int, dict[str, Any]]] = []
    for epoch in range(epochs):
        for idx, record in enumerate(records):
            stream.append((epoch, idx, record))
    batches = [stream[i : i + batch_size] for i in range(0, len(stream), batch_size)]
    if max_batches > 0:
        batches = batches[:max_batches]
    return batches


def _copy_skillbank(src: Path, dst: Path, *, overwrite: bool = False) -> None:
    if dst.exists():
        if not overwrite:
            return
        shutil.rmtree(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dst)


def _replace_skillbank(src: Path, dst: Path) -> None:
    """Replace the working SkillBank with ``src`` without keeping a versioned copy."""
    if not src.exists():
        raise FileNotFoundError(f"SkillBank source not found: {src}")
    tmp = dst.with_name(f"{dst.name}.tmp_replace")
    if tmp.exists():
        shutil.rmtree(tmp)
    shutil.copytree(src, tmp)
    if dst.exists():
        shutil.rmtree(dst)
    tmp.rename(dst)


def _run_command(cmd: list[str], *, cwd: Path, log_path: Path, env: dict[str, str]) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8") as log:
        log.write("$ " + " ".join(cmd) + "\n\n")
        log.flush()
        proc = subprocess.run(
            cmd,
            cwd=str(cwd),
            env=env,
            stdout=log,
            stderr=subprocess.STDOUT,
            text=True,
        )
    if proc.returncode != 0:
        raise RuntimeError(f"Command failed with exit {proc.returncode}: {' '.join(cmd)}; see {log_path}")


def _latest_final_results(run_dir: Path) -> Path:
    candidates = sorted(run_dir.glob("final_results_*.json"))
    if not candidates:
        raise FileNotFoundError(f"No final_results_*.json under {run_dir}")
    return candidates[-1]


def _summarize_results(final_results: Path) -> dict[str, Any]:
    payload = _read_json(final_results)
    rows = payload.get("results", []) if isinstance(payload, dict) else payload
    if not isinstance(rows, list):
        rows = []
    tiers = Counter(str(row.get("final_tier") or "UNKNOWN") for row in rows if isinstance(row, dict))
    bug_best: dict[str, str] = {}
    tier_rank = {
        "BUG_DETECTED": 5,
        "PASS_BOTH": 4,
        "FAIL_ON_FIXED": 3,
        "COMPILE_FAIL": 2,
        "NO_TEST_GENERATED": 1,
    }
    for row in rows:
        if not isinstance(row, dict):
            continue
        bug_id = str(row.get("bug_id") or row.get("source_id") or row.get("bid") or row.get("record_key") or "")
        tier = str(row.get("final_tier") or "UNKNOWN")
        if not bug_id:
            continue
        if tier_rank.get(tier, 0) > tier_rank.get(bug_best.get(bug_id, "UNKNOWN"), 0):
            bug_best[bug_id] = tier
    return {
        "total_records": len(rows),
        "tiers": dict(tiers),
        "bug_level_total": len(bug_best),
        "bug_level_tiers": dict(Counter(bug_best.values())),
    }


def _write_batch_dataset(batch: list[tuple[int, int, dict[str, Any]]], path: Path) -> None:
    rows = []
    for global_idx, (epoch, source_idx, record) in enumerate(batch):
        item = dict(record)
        item["_training_epoch"] = epoch
        item["_source_dataset_index"] = source_idx
        item["_batch_local_index"] = global_idx
        rows.append(item)
    _write_json(path, {"focal_methods": rows})


def _command_base(args: argparse.Namespace) -> list[str]:
    return [args.python, "-u"]


def _run_training_batch(
    *,
    args: argparse.Namespace,
    batch_id: int,
    batch_dir: Path,
    batch_dataset: Path,
    current_bank: Path,
    env: dict[str, str],
) -> Path:
    output_dir = batch_dir / "inference"
    workspace = Path(args.workspace_root) / f"batch_{batch_id:03d}"
    cmd = _command_base(args) + [
        str(SCRIPT_DIR / "run_gitbug_generated_suite_training.py"),
        "--dataset-file",
        str(batch_dataset),
        "--output",
        str(output_dir),
        "--workspace",
        str(workspace),
        "--skill-bank",
        str(current_bank),
        "--skill-top-k",
        str(args.skill_top_k),
        "--skip-existing-results",
        "--gitbug-repo",
        args.gitbug_repo,
        "--git-cache",
        args.git_cache,
        "--checkout-backend",
        args.checkout_backend,
        "--workers",
        str(args.tg_workers),
        "--methods-per-class",
        str(args.methods_per_class),
        "--tool-steps",
        str(args.tool_steps),
        "--generation-max-tokens",
        str(args.generation_max_tokens),
        "--generation-repair-rounds",
        str(args.generation_repair_rounds),
        "--repair-rounds",
        str(args.repair_rounds),
        "--test-timeout",
        str(args.test_timeout),
        "--package-mode",
        args.package_mode,
        "--model",
        args.model,
    ]
    if args.gitbug_cli:
        cmd.extend(["--gitbug-cli", args.gitbug_cli])
    _run_command(cmd, cwd=Path(args.repo_root), log_path=batch_dir / "logs" / "01_inference.log", env=env)
    return _latest_final_results(output_dir)


def _run_case_agents(
    *,
    args: argparse.Namespace,
    batch_dir: Path,
    final_results: Path,
    current_bank: Path,
    env: dict[str, str],
) -> Path:
    output_dir = batch_dir / "case_agents"
    cmd = _command_base(args) + [
        str(SCRIPT_DIR / "run_skillbank_evolution_agents.py"),
        "case-agents",
        "--results",
        str(final_results),
        "--skill-bank",
        str(current_bank),
        "--output",
        str(output_dir),
        "--model",
        args.evolution_model,
        "--max-cases",
        "0",
        "--workers",
        str(args.case_workers),
        "--max-tool-steps",
        str(args.case_max_tool_steps),
        "--top-k",
        str(args.case_top_k),
        "--context-compact-every",
        str(args.context_compact_every),
        "--allowed-root",
        str(batch_dir),
        "--skip-existing",
    ]
    _run_command(cmd, cwd=Path(args.repo_root), log_path=batch_dir / "logs" / "02_case_agents.log", env=env)
    return output_dir / "case_reports"


def _run_global_agent(
    *,
    args: argparse.Namespace,
    batch_dir: Path,
    case_reports: Path,
    current_bank: Path,
    env: dict[str, str],
    batch_size: int,
) -> Path:
    output_dir = batch_dir / "global_agent"
    min_case_reports = args.min_case_reports_read
    if min_case_reports < 0:
        min_case_reports = min(batch_size, max(1, int(batch_size * 0.7)))
    cmd = _command_base(args) + [
        str(SCRIPT_DIR / "run_skillbank_evolution_agents.py"),
        "global-agent",
        "--case-reports",
        str(case_reports),
        "--skill-bank",
        str(current_bank),
        "--output",
        str(output_dir),
        "--model",
        args.evolution_model,
        "--max-reports",
        "0",
        "--max-tool-steps",
        str(args.global_max_tool_steps),
        "--max-tokens",
        str(args.global_max_tokens),
        "--top-k",
        str(args.global_top_k),
        "--max-skill-reads",
        str(args.max_skill_reads),
        "--min-case-reports-read",
        str(min_case_reports),
        "--min-skill-reads",
        str(args.min_skill_reads),
        "--context-compact-every",
        str(args.context_compact_every),
        "--allowed-root",
        str(batch_dir),
        "--apply",
    ]
    _run_command(cmd, cwd=Path(args.repo_root), log_path=batch_dir / "logs" / "03_global_agent.log", env=env)
    evolved = output_dir / "evolved_skillbank_snapshot" / "skill_bank"
    if not evolved.exists():
        raise FileNotFoundError(f"Global agent did not produce evolved skillbank: {evolved}")
    return evolved


def main() -> None:
    parser = argparse.ArgumentParser(description="Sequential GitBug-Java SkillBank training")
    parser.add_argument("--dataset-file", required=True)
    parser.add_argument("--initial-skill-bank", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--workspace-root", required=True)
    parser.add_argument("--repo-root", default=str(SCRIPT_DIR.parent.parent))
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument(
        "--data-root",
        default=os.environ.get("EVOTEST_DATA_DIR", os.environ.get("SKILL_MINING_DATA", "data")),
    )
    parser.add_argument("--epochs", type=int, default=2)
    parser.add_argument("--batch-size", type=int, default=50)
    parser.add_argument("--max-records", type=int, default=0)
    parser.add_argument("--max-batches", type=int, default=0, help="For smoke/debug; 0 means all scheduled batches")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--overwrite-skill-bank", action="store_true")

    parser.add_argument(
        "--gitbug-repo",
        default=os.environ.get("EVOTEST_GITBUG_REPO", os.environ.get("GITBUG_REPO", "")),
    )
    parser.add_argument("--gitbug-cli", default="")
    parser.add_argument(
        "--git-cache",
        default=os.environ.get("EVOTEST_GIT_CACHE", os.environ.get("GITBUG_CACHE", "")),
    )
    parser.add_argument("--checkout-backend", choices=["official", "cache"], default=os.environ.get("GITBUG_OFFICIAL_CHECKOUT_BACKEND", "official"))

    parser.add_argument("--model", default=os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-flash"))
    parser.add_argument("--evolution-model", default=os.environ.get("EVOLUTION_AGENT_MODEL", os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-flash")))
    parser.add_argument("--tg-workers", type=int, default=4)
    parser.add_argument("--case-workers", type=int, default=8)
    parser.add_argument("--skill-top-k", type=int, default=10)
    parser.add_argument("--methods-per-class", type=int, default=10)
    parser.add_argument("--tool-steps", type=int, default=50)
    parser.add_argument("--generation-max-tokens", type=int, default=8192)
    parser.add_argument("--generation-repair-rounds", type=int, default=2)
    parser.add_argument("--repair-rounds", type=int, default=2)
    parser.add_argument("--test-timeout", type=int, default=500)
    parser.add_argument("--package-mode", choices=["gentest", "same"], default="gentest")

    parser.add_argument("--case-max-tool-steps", type=int, default=50)
    parser.add_argument("--case-top-k", type=int, default=10)
    parser.add_argument("--global-max-tool-steps", type=int, default=220)
    parser.add_argument("--global-max-tokens", type=int, default=8192)
    parser.add_argument("--global-top-k", type=int, default=12)
    parser.add_argument("--max-skill-reads", type=int, default=50)
    parser.add_argument("--min-skill-reads", type=int, default=25)
    parser.add_argument("--min-case-reports-read", type=int, default=-1, help="-1 means roughly 70 percent of batch")
    parser.add_argument("--context-compact-every", type=int, default=100)
    args = parser.parse_args()
    if not args.gitbug_repo:
        args.gitbug_repo = str(Path(args.data_root) / "gitbug-java" / "gitbug-java")
    if not args.git_cache:
        args.git_cache = str(Path(args.data_root) / "cache" / "gitbug-repos")

    dataset_file = Path(args.dataset_file)
    output_root = Path(args.output_root)
    workspace_root = Path(args.workspace_root)
    initial_bank = Path(args.initial_skill_bank)
    if not initial_bank.exists():
        raise SystemExit(f"Initial SkillBank not found: {initial_bank}")
    records = _load_dataset(dataset_file)
    schedule = _build_schedule(
        records,
        epochs=args.epochs,
        batch_size=args.batch_size,
        max_records=args.max_records,
        max_batches=args.max_batches,
    )

    run_id = _now_tag()
    working_bank = output_root / "skill_bank"
    batch_root = output_root / "batches"
    output_root.mkdir(parents=True, exist_ok=True)
    workspace_root.mkdir(parents=True, exist_ok=True)

    launch = {
        "run_id": run_id,
        "dataset_file": str(dataset_file),
        "initial_skill_bank": str(initial_bank),
        "working_skill_bank": str(working_bank),
        "output_root": str(output_root),
        "workspace_root": str(workspace_root),
        "records": len(records),
        "epochs": args.epochs,
        "batch_size": args.batch_size,
        "scheduled_batches": len(schedule),
        "model": args.model,
        "evolution_model": args.evolution_model,
        "tg_workers": args.tg_workers,
        "case_workers": args.case_workers,
        "skill_top_k": args.skill_top_k,
        "generation_max_tokens": args.generation_max_tokens,
        "context_compact_every": args.context_compact_every,
    }
    _write_json(output_root / "RUN_CONFIG.json", launch)

    if args.dry_run:
        preview = []
        for batch_id, batch in enumerate(schedule):
            preview.append({
                "batch_id": batch_id,
                "size": len(batch),
                "first": _record_key(batch[0][2], batch[0][1]) if batch else "",
                "last": _record_key(batch[-1][2], batch[-1][1]) if batch else "",
                "epochs": sorted({epoch for epoch, _, _ in batch}),
            })
        _write_json(output_root / "DRY_RUN_SCHEDULE.json", {"config": launch, "batches": preview})
        print(json.dumps({"config": launch, "batches": preview}, indent=2, ensure_ascii=False))
        return

    completed_batch_manifests = sorted(batch_root.glob("batch_*/BATCH_MANIFEST.json"))
    if args.resume and completed_batch_manifests and not working_bank.exists():
        raise SystemExit(
            f"Cannot resume because completed batch manifests exist but the working SkillBank is missing: {working_bank}"
        )
    if working_bank.exists() and not args.resume and not args.overwrite_skill_bank:
        raise SystemExit(
            f"Working SkillBank already exists: {working_bank}. "
            "Use --resume to continue it or --overwrite-skill-bank to recreate it from --initial-skill-bank."
        )
    _copy_skillbank(initial_bank, working_bank, overwrite=args.overwrite_skill_bank)
    current_bank = working_bank
    manifest: list[dict[str, Any]] = []
    env = os.environ.copy()
    env.setdefault("TMPDIR", str(output_root / "tmp"))
    env.setdefault("EVOTEST_DATA_DIR", str(Path(args.data_root)))
    env.setdefault("EVOTEST_OUTPUT_DIR", str(output_root))
    env.setdefault("EVOTEST_TMP_DIR", str(output_root / "tmp"))
    env.setdefault("EVOTEST_WORKSPACE_ROOT", str(workspace_root))
    env.setdefault("SKILL_MINING_DATA", str(Path(args.data_root)))
    env.setdefault("SKILL_MINING_OUTPUT", str(output_root))
    env.setdefault("SKILL_WORKSPACE_BASE", str(workspace_root))
    env.setdefault("WORKSPACE_ROOT", str(workspace_root))
    env.setdefault("SKILL_USE_GITBUG_OFFICIAL", "1")
    env.setdefault("GITBUG_OFFICIAL_BACKEND", "docker_direct")
    env.setdefault("GITBUG_OFFICIAL_CHECKOUT_BACKEND", args.checkout_backend)
    env.setdefault("GITBUG_DOCKER_MAVEN_REPO", str(Path(args.data_root) / "cache" / "gitbug-m2"))
    env.setdefault("D4J_SUITE_CONTEXT_COMPACT_EVERY", str(args.context_compact_every))

    for batch_id, batch in enumerate(schedule):
        batch_dir = batch_root / f"batch_{batch_id:03d}"
        batch_manifest_path = batch_dir / "BATCH_MANIFEST.json"
        if args.resume and batch_manifest_path.exists():
            manifest.append(_read_json(batch_manifest_path))
            print(f"[resume] batch {batch_id:03d} already complete; working_bank={current_bank}")
            continue

        batch_dir.mkdir(parents=True, exist_ok=True)
        batch_dataset = batch_dir / "batch_dataset.json"
        _write_batch_dataset(batch, batch_dataset)
        batch_info = {
            "batch_id": batch_id,
            "size": len(batch),
            "skill_bank": str(current_bank),
            "dataset": str(batch_dataset),
            "records": [
                {"epoch": epoch, "source_index": idx, "key": _record_key(record, idx)}
                for epoch, idx, record in batch
            ],
        }
        _write_json(batch_dir / "BATCH_INPUT.json", batch_info)

        print(f"[batch {batch_id:03d}] inference with {len(batch)} records using {current_bank}", flush=True)
        final_results = _run_training_batch(
            args=args,
            batch_id=batch_id,
            batch_dir=batch_dir,
            batch_dataset=batch_dataset,
            current_bank=current_bank,
            env=env,
        )
        result_summary = _summarize_results(final_results)
        _write_json(batch_dir / "training_result_summary.json", result_summary)

        print(f"[batch {batch_id:03d}] case agents", flush=True)
        case_reports = _run_case_agents(
            args=args,
            batch_dir=batch_dir,
            final_results=final_results,
            current_bank=current_bank,
            env=env,
        )

        print(f"[batch {batch_id:03d}] global evolution", flush=True)
        evolved_bank = _run_global_agent(
            args=args,
            batch_dir=batch_dir,
            case_reports=case_reports,
            current_bank=current_bank,
            env=env,
            batch_size=len(batch),
        )
        _replace_skillbank(evolved_bank, current_bank)
        shutil.rmtree(evolved_bank.parent, ignore_errors=True)

        global_report = batch_dir / "global_agent" / "global_evolution_agent_report.json"
        ops_path = batch_dir / "global_agent" / "evolution_ops.jsonl"
        ops_count = 0
        if ops_path.exists():
            ops_count = sum(1 for line in ops_path.read_text(encoding="utf-8", errors="replace").splitlines() if line.strip())
        batch_manifest = {
            **batch_info,
            "final_results": str(final_results),
            "training_summary": result_summary,
            "case_reports": str(case_reports),
            "global_report": str(global_report),
            "evolution_ops": str(ops_path),
            "ops_count": ops_count,
            "completed_at": _now_tag(),
        }
        _write_json(batch_manifest_path, batch_manifest)
        manifest.append(batch_manifest)
        _write_json(output_root / "TRAINING_MANIFEST.json", {"config": launch, "batches": manifest})
        print(f"[batch {batch_id:03d}] done ops={ops_count} skill_bank={current_bank}", flush=True)

    _write_json(output_root / "TRAINING_MANIFEST.json", {"config": launch, "batches": manifest})
    print(f"Sequential training complete. Final SkillBank: {current_bank}")
    print(f"Manifest: {output_root / 'TRAINING_MANIFEST.json'}")


if __name__ == "__main__":
    main()

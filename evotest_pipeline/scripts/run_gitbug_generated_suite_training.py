#!/usr/bin/env python3
"""GitBug-Java generated-suite TG runner with SkillBank tools.

This is the GitBug-Java training analogue of the Defects4J v16 generated-suite
agent.  Each input focal method is still an independent training unit, but TG
now generates a multi-method JUnit4 suite, can inspect fixed-version files, can
search/read the SkillBank, and uses the same repair loop shape as
the Defects4J generated-suite evaluation.

The verifier uses GitBug-Java's official checkout plus the Docker-direct
backend.  Generated test methods are injected into the existing failing test
class and the Docker command is narrowed to those generated methods only.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime
import json
import os
from pathlib import Path
import shutil
import sys
import time
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
SRC_DIR = SCRIPT_DIR.parent / "src"
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(SRC_DIR))

import run_defects4j_eval as d4j  # noqa: E402
import run_defects4j_generated_suite_eval as suite  # noqa: E402
import skillbank_tools  # noqa: E402
from gitbug_official_runner import OfficialGitBugRunner, detect_existing_test_file, resolve_official_bid, _extract_void_test_methods  # noqa: E402
from paths import GITBUG_CACHE, GITBUG_REPO, OUTPUT_ROOT, WORKSPACE_ROOT  # noqa: E402


DEFAULT_OUTPUT = Path(os.environ.get("GITBUG_SUITE_OUTPUT", str(OUTPUT_ROOT / "gitbug_generated_suite_training")))
DEFAULT_WORKSPACE = Path(os.environ.get("GITBUG_SUITE_WORKSPACE", str(WORKSPACE_ROOT / "gitbug-generated-suite-training")))
DEFAULT_SKILL_BANK = os.environ.get(
    "GITBUG_SKILL_BANK",
    str(OUTPUT_ROOT / "initial_skillbank" / "skill_bank"),
)


def _safe_key(value: str) -> str:
    return "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in value)


def _method_name(value: str) -> str:
    return d4j._method_name_from_signature(str(value or ""))


def _focal_key(record: dict[str, Any], idx: int) -> str:
    bid = str(record.get("bug_id") or record.get("source_id") or record.get("bid") or f"case-{idx}")
    method = _method_name(str(record.get("method_name") or record.get("focal_method") or record.get("focal_method_sig") or ""))
    return f"{bid}::{method or 'focal'}"


def _normalize_record(record: dict[str, Any]) -> dict[str, Any]:
    out = dict(record)
    out.setdefault("dataset", "gitbug-java")
    if not out.get("bug_id") and out.get("source_id"):
        out["bug_id"] = out["source_id"]
    if not out.get("source_id") and out.get("bug_id"):
        out["source_id"] = out["bug_id"]
    if not out.get("class_name"):
        out["class_name"] = out.get("focal_class") or out.get("qualified_class_name") or ""
    if not out.get("method_name"):
        out["method_name"] = _method_name(
            str(out.get("focal_method") or out.get("focal_method_sig") or "")
        )
    if not out.get("focal_method") and out.get("focal_method_sig"):
        out["focal_method"] = out.get("focal_method_sig")
    return out


def _load_records(dataset_file: str, *, bug_ids: list[str], max_cases: int) -> list[dict[str, Any]]:
    data = json.loads(Path(dataset_file).read_text(encoding="utf-8"))
    records = data.get("focal_methods", data if isinstance(data, list) else [])
    if not isinstance(records, list):
        raise ValueError("Dataset must be a list or an object with focal_methods")
    normalized = [_normalize_record(r) for r in records if isinstance(r, dict)]
    normalized = [r for r in normalized if str(r.get("dataset") or "gitbug-java") == "gitbug-java"]
    if bug_ids:
        wanted = set(bug_ids)
        normalized = [
            r for r in normalized
            if (r.get("bug_id") in wanted or r.get("source_id") in wanted or r.get("bid") in wanted or r.get("gitbug_bid") in wanted)
        ]
    if max_cases > 0:
        normalized = normalized[:max_cases]
    return normalized


def _load_existing_results(results_dir: Path) -> dict[int, dict[str, Any]]:
    existing: dict[int, dict[str, Any]] = {}
    for path in sorted(results_dir.glob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            continue
        if not isinstance(payload, dict):
            continue
        idx = payload.get("idx")
        if not isinstance(idx, int):
            try:
                idx = int(path.name.split("_", 1)[0])
            except Exception:
                continue
        existing[idx] = payload
    return existing


def _skill_tools_for_record(
    record: dict[str, Any],
    skill_bank: dict[str, Any],
    *,
    fixed_dir: str,
    top_k: int,
    read_log: list[str],
) -> tuple[list[dict[str, Any]], Any, list[dict[str, Any]], str]:
    focal_file, focal_source = suite._focal_file_and_source(
        fixed_dir,
        record,
        suite.DEFAULT_MAX_SOURCE_CHARS,
    )
    method_name = _method_name(str(record.get("method_name") or record.get("focal_method") or ""))
    query = " ".join(
        part for part in [
            str(record.get("class_name") or record.get("focal_class") or ""),
            method_name,
            str(record.get("focal_method") or ""),
            focal_source[:2000],
        ] if part
    )
    initial = skillbank_tools._search_skills(
        skill_bank,
        query,
        top_k=top_k,
        exclude_bug_key=str(record.get("bug_id") or record.get("source_id") or ""),
    )
    executor = skillbank_tools._make_skill_executor(
        skill_bank,
        initial,
        top_k=top_k,
        exclude_bug_key=str(record.get("bug_id") or record.get("source_id") or ""),
        read_log=read_log,
    )
    hint = (
        "SkillBank tools are available: list_skills(), search_skills(query, code_tags), "
        "search_code_tags(query), list_code_tags(offset, limit, sort_by), "
        "get_skills_by_code_tags(code_tags), and read_skill(name). "
        "Skills are optional references. Read any skills that look relevant, possibly multiple, "
        "but ignore misleading skills and prioritize fixed-version source evidence."
    )
    return skillbank_tools._skill_tool_specs(), executor, initial, hint


def _host_test_framework(fixed_dir: str, failing_test_class: str) -> tuple[str, str]:
    test_file = detect_existing_test_file(Path(fixed_dir), failing_test_class)
    if test_file is None:
        return "junit4", ""
    try:
        source = test_file.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return "junit4", str(test_file)
    if "org.junit.jupiter" in source:
        return "junit5", str(test_file)
    if "org.testng" in source:
        return "testng", str(test_file)
    if "junit.framework" in source or "extends TestCase" in source:
        return "junit3", str(test_file)
    return "junit4", str(test_file)


def _framework_rule(framework: str) -> str:
    if framework == "junit5":
        return (
            "Use the same test framework as the host test class: JUnit 5/Jupiter. "
            "Import org.junit.jupiter.api.Test and static org.junit.jupiter.api.Assertions.*. "
            "Use assertThrows for exception assertions. Do not import org.junit.Test, org.junit.Rule, "
            "org.junit.rules.ExpectedException, or org.junit.Assert."
        )
    if framework == "testng":
        return (
            "Use the same test framework as the host test class: TestNG. "
            "Import org.testng.annotations.Test and static org.testng.Assert.*. "
            "Do not import JUnit APIs."
        )
    if framework == "junit3":
        return (
            "Use the same test framework style as the host test class: JUnit 3. "
            "Prefer public void testXxx() methods and avoid @Test annotations unless the host already uses them."
        )
    return (
        "Use the same test framework as the host test class: JUnit 4. "
        "Import org.junit.Test and static org.junit.Assert.*. "
        "Use ExpectedException only when needed."
    )


def _assemble_gitbug_test_class(
    *,
    test_class_name: str,
    test_package: str,
    focal_package: str,
    source_imports: list[str],
    test_methods: list[dict[str, str]],
    framework: str,
) -> str:
    if framework == "junit5":
        imports = [
            "org.junit.jupiter.api.Test",
            "static org.junit.jupiter.api.Assertions.*",
        ]
    elif framework == "testng":
        imports = [
            "org.testng.annotations.Test",
            "static org.testng.Assert.*",
        ]
    elif framework == "junit3":
        imports = []
    else:
        imports = [
            "org.junit.Test",
            "org.junit.Rule",
            "org.junit.rules.ExpectedException",
            "static org.junit.Assert.*",
        ]
    imports.extend([
        "java.lang.reflect.Method",
        "java.lang.reflect.Field",
        "java.lang.reflect.Constructor",
        "java.lang.reflect.*",
        "java.util.ArrayList",
        "java.util.List",
        "java.io.ByteArrayInputStream",
        "java.io.ByteArrayOutputStream",
    ])
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
        if framework == "junit5" and item.startswith("org.junit.") and "jupiter" not in item:
            continue
        if framework in {"junit4", "junit3"} and "org.junit.jupiter" in item:
            continue
        seen.add(item)
        lines.append(f"import {item};")
    lines.extend(["", f"public class {test_class_name} {{"])
    if framework == "junit4":
        lines.extend(["    @Rule", "    public ExpectedException thrown = ExpectedException.none();", ""])
    else:
        lines.append("")
    for method in suite._ensure_unique_test_method_names(test_methods):
        code = method["pure_test_method"].strip()
        if framework == "junit5":
            code = code.replace("org.junit.Test", "org.junit.jupiter.api.Test")
            code = code.replace("org.junit.Assert", "org.junit.jupiter.api.Assertions")
        elif framework == "testng":
            code = code.replace("org.junit.Test", "org.testng.annotations.Test")
            code = code.replace("org.junit.Assert", "org.testng.Assert")
        for line in code.splitlines():
            lines.append("    " + line if line.strip() else "")
        lines.append("")
    lines.append("}")
    lines.append("")
    return "\n".join(lines)


def _generate_initial_test_class(
    record: dict[str, Any],
    fixed_dir: str,
    *,
    focal_idx: int,
    methods_per_class: int,
    package_mode: str,
    max_source_chars: int,
    tool_steps: int,
    generation_max_tokens: int,
    generation_repair_rounds: int,
    skill_bank: dict[str, Any],
    skill_top_k: int,
    trace_path: str,
) -> dict[str, Any]:
    focal_file, source = suite._focal_file_and_source(fixed_dir, record, max_source_chars)
    if not source:
        return {"ok": False, "error": "Could not locate/read focal source file", "test_code": ""}

    focal_package = suite._extract_java_package(source)
    source_imports = suite._extract_java_imports(source)
    test_package = suite._test_package_for(focal_package, package_mode)
    test_class_name = suite._build_test_class_name(record, focal_idx)
    method_name = _method_name(str(record.get("method_name") or record.get("focal_method") or ""))
    focal_sig = str(record.get("focal_method") or record.get("focal_method_sig") or record.get("method_name") or "")
    framework, host_test_file = _host_test_framework(fixed_dir, str(record.get("failing_test_class") or ""))
    framework_rule = _framework_rule(framework)
    read_log: list[str] = []
    extra_tools, extra_executor, initial_candidates, skill_hint = _skill_tools_for_record(
        record,
        skill_bank,
        fixed_dir=fixed_dir,
        top_k=skill_top_k,
        read_log=read_log,
    )

    system = (
        "You are a Test Generator. "
        "Generate JUnit4 test methods that compile and pass on the fixed version, "
        "while trying to expose the bug on the buggy version. "
        "You may inspect only the fixed-version checkout with tools before generating tests. "
        "Return compact JSON when ready."
    )
    user = f"""
Generate a JUnit4 test class plan for this fixed-version source.

Focal class: {record.get('class_name') or record.get('focal_class') or ''}
Focal method: {method_name}
Focal signature: {focal_sig}
Generated test class name: {test_class_name}
Target test package: {test_package}
Host test class for final injection: {record.get('failing_test_class') or ''}
Host test file: {host_test_file or '(not found before generation)'}
Detected host test framework: {framework}

Rules:
- Produce up to {methods_per_class} distinct @Test methods when possible.
- {framework_rule}
- Mockito 3 and java.lang.reflect are allowed only when the project already supports them.
- Prefer a broad but fixed-valid suite: normal cases, boundary cases, null/error cases, state transitions, equality/hash/clone/serialization-style contracts when relevant.
- Fixed-version correctness is mandatory. Assertions must follow the fixed source or API contract.
- Each test method must be self-contained: declare local variables inside the method.
- Before writing tests, use tools when needed to verify exact constructors, method signatures, visibility, helper APIs, constants, and existing class behavior.
- Prefer reading production source and build files. Do not rely on memory for non-public constructors, abstract method signatures, protected/package-private members, or complex stubs.
- The generated class will be converted into methods and inserted into the existing host test class. Avoid class-level state unless each method initializes it locally.
- {skill_hint}
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
    content, tool_trajectory, session_state = suite._call_generation_agent(
        messages,
        work_dir=fixed_dir,
        max_tool_steps=tool_steps,
        max_tokens=generation_max_tokens,
        extra_tools=extra_tools,
        extra_tool_executor=extra_executor,
        trace_path=trace_path,
        require_extra_tool_read_skill=False,
        return_state=True,
    )
    methods = suite._extract_test_methods_from_response(content)
    generation_repair_attempts: list[dict[str, Any]] = []
    final_content = content
    for repair_round in range(1, generation_repair_rounds + 1):
        if methods:
            break
        repaired_generation = suite.repair_generation_submission(
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
            "skill_initial_candidates": initial_candidates,
            "skill_read_skills": read_log,
            "_session_state": session_state,
            "test_code": "",
        }
    test_code = _assemble_gitbug_test_class(
        test_class_name=test_class_name,
        test_package=test_package,
        focal_package=focal_package,
        source_imports=source_imports,
        test_methods=methods,
        framework=framework,
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
        "skill_initial_candidates": initial_candidates,
        "skill_read_skills": read_log,
        "_session_state": session_state,
        "test_code": test_code,
        "test_class_name": test_class_name,
        "test_package": test_package,
        "full_test_class": f"{test_package}.{test_class_name}" if test_package else test_class_name,
        "num_methods": len(methods),
        "focal_file": os.path.relpath(focal_file, fixed_dir),
        "test_framework": framework,
        "host_test_file": host_test_file,
    }


def _verify_with_repair(
    *,
    record: dict[str, Any],
    runner: OfficialGitBugRunner,
    bid: str,
    fixed_dir: str,
    initial_code: str,
    full_test_class: str,
    tool_steps: int,
    repair_rounds: int,
    repair_max_tokens: int,
    skill_bank: dict[str, Any],
    skill_top_k: int,
    session_state: dict[str, Any] | None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "tier": "UNKNOWN",
        "passed": False,
        "repair_rounds_used": 0,
        "repair_attempts": [],
        "deterministic_repair_attempts": [],
    }
    current_code = initial_code
    read_log: list[str] = []
    extra_tools, extra_executor, initial_candidates, repair_hint = _skill_tools_for_record(
        record,
        skill_bank,
        fixed_dir=fixed_dir,
        top_k=skill_top_k,
        read_log=read_log,
    )
    session_state = dict(session_state or {})
    test_package = full_test_class.rsplit(".", 1)[0] if "." in full_test_class else ""
    test_class_name = full_test_class.rsplit(".", 1)[-1]
    framework = str(record.get("_test_framework") or "junit4")
    latest_report: dict[str, Any] = {}

    for attempt in range(0, repair_rounds + 1):
        current_code, cleanup_notes = suite._prune_generated_imports(
            current_code,
            str((latest_report.get("coach_feedback") if latest_report else "") or ""),
        )
        if cleanup_notes:
            result["deterministic_repair_attempts"].append({
                "attempt": attempt,
                "notes": cleanup_notes,
            })
        report = runner.verify_generated_test_class_docker_direct(
            bid=bid,
            test_class_code=current_code,
            failing_test_class=str(record.get("failing_test_class") or ""),
        )
        latest_report = report
        result["latest_report"] = report
        result["tier"] = report.get("tier", "UNKNOWN")
        result["passed"] = bool(report.get("passed"))
        if report.get("tier") in {"BUG_DETECTED", "PASS_BOTH"}:
            result["fixed_passed"] = True
            result["buggy_passed"] = report.get("tier") == "PASS_BOTH"
            return result
        if attempt >= repair_rounds:
            return result

        fixed_output = str(report.get("coach_feedback") or "")
        repaired = suite.repair_test_class(
            record,
            current_code,
            fixed_output,
            fixed_dir=fixed_dir,
            test_class_name=test_class_name,
            test_package=test_package,
            repair_tool_steps=tool_steps,
            extra_tools=extra_tools,
            extra_tool_executor=extra_executor,
            extra_tool_hint=repair_hint,
            require_extra_tool_read_skill=False,
            framework_rule=_framework_rule(framework),
            session_messages=session_state.get("conversation"),
            session_base_messages=session_state.get("compaction_base_messages"),
            session_trajectory=[],
            session_steps_since_compaction=int(session_state.get("steps_since_compaction") or 0),
            repair_max_tokens=repair_max_tokens,
        )
        result["repair_rounds_used"] += 1
        result["repair_attempts"].append({
            "round": attempt + 1,
            "ok": bool(repaired.get("ok")),
            "error": repaired.get("error", ""),
            "raw_response": str(repaired.get("raw_response") or "")[:4000],
            "tool_trajectory": repaired.get("tool_trajectory", []),
            "skill_initial_candidates": initial_candidates,
            "skill_read_skills": list(read_log),
        })
        if isinstance(repaired.get("_session_state"), dict):
            session_state = repaired["_session_state"]
        if not repaired.get("ok"):
            return result
        repaired_code = str(repaired.get("test_code") or "")
        if repaired_code and _extract_void_test_methods(repaired_code, require_test_annotation=True):
            current_code = repaired_code
        else:
            result["deterministic_repair_attempts"].append({
                "attempt": attempt + 1,
                "notes": ["ignored repair output because no annotated test methods were extractable"],
            })
    return result


def run_one(payload: tuple[int, dict[str, Any], dict[str, Any], dict[str, Any]]) -> dict[str, Any]:
    idx, record, args_dict, skill_bank = payload
    args = argparse.Namespace(**args_dict)
    start = time.time()
    record = _normalize_record(record)
    key = _focal_key(record, idx)
    out_dir = Path(args.output)
    workspace_base = Path(args.workspace)
    case_dir = workspace_base / f"{idx:04d}_{_safe_key(key)}"
    fixed_gen_dir = case_dir / "generation_fixed"
    trace_path = out_dir / "traces" / f"{idx:04d}_{_safe_key(key)}.jsonl"
    session_path = out_dir / "sessions" / f"{idx:04d}_{_safe_key(key)}.json"
    result: dict[str, Any] = {
        "idx": idx,
        "record_key": key,
        "bug_id": record.get("bug_id"),
        "source_id": record.get("source_id"),
        "project": record.get("project"),
        "focal_method": record.get("focal_method"),
        "failing_test_class": record.get("failing_test_class"),
        "final_tier": "UNKNOWN",
    }
    try:
        if case_dir.exists():
            shutil.rmtree(case_dir, ignore_errors=True)
        case_dir.mkdir(parents=True, exist_ok=True)

        bid, bid_resolution = resolve_official_bid(record, Path(args.gitbug_repo))
        result["bid"] = bid
        result["bid_resolution"] = bid_resolution
        runner = OfficialGitBugRunner(
            gitbug_repo=Path(args.gitbug_repo),
            work_root=case_dir / "verify",
            cli=args.gitbug_cli or None,
            git_cache=Path(args.git_cache) if args.git_cache else None,
            checkout_backend=args.checkout_backend,
            timeout=args.test_timeout,
        )
        checkout = runner.checkout_version(bid, fixed_gen_dir, fixed=True)
        result["generation_checkout_fixed"] = checkout.as_dict()
        if not checkout.ok:
            result["final_tier"] = "CHECKOUT_FIXED_FAIL"
            result["feedback"] = checkout.stderr_tail or checkout.stdout_tail or checkout.error
            return result

        generated = _generate_initial_test_class(
            record,
            str(fixed_gen_dir),
            focal_idx=idx,
            methods_per_class=args.methods_per_class,
            package_mode=args.package_mode,
            max_source_chars=args.max_source_chars,
            tool_steps=args.tool_steps,
            generation_max_tokens=args.generation_max_tokens,
            generation_repair_rounds=args.generation_repair_rounds,
            skill_bank=skill_bank,
            skill_top_k=args.skill_top_k,
            trace_path=str(trace_path),
        )
        result["generation"] = {k: v for k, v in generated.items() if k != "test_code"}
        if not generated.get("ok"):
            result["final_tier"] = "NO_TEST_GENERATED"
            result["feedback"] = generated.get("error", "")
            return result

        verification = _verify_with_repair(
            record={**record, "_test_framework": str(generated.get("test_framework") or "junit4")},
            runner=runner,
            bid=bid,
            fixed_dir=str(fixed_gen_dir),
            initial_code=str(generated.get("test_code") or ""),
            full_test_class=str(generated.get("full_test_class") or generated.get("test_class_name") or "GeneratedTest"),
            tool_steps=args.tool_steps,
            repair_rounds=args.repair_rounds,
            repair_max_tokens=args.generation_max_tokens,
            skill_bank=skill_bank,
            skill_top_k=args.skill_top_k,
            session_state=generated.get("_session_state") if isinstance(generated.get("_session_state"), dict) else None,
        )
        result["verification"] = verification
        result["final_tier"] = verification.get("tier", "UNKNOWN")
        result["feedback"] = ((verification.get("latest_report") or {}).get("coach_feedback") or "")[:4000]

        session_payload = {
            "record": record,
            "generation_session": generated.get("_session_state"),
            "result_tier": result["final_tier"],
            "elapsed_seconds": round(time.time() - start, 1),
        }
        session_path.parent.mkdir(parents=True, exist_ok=True)
        session_path.write_text(json.dumps(session_payload, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
        return result
    except Exception as exc:
        result["final_tier"] = "PIPELINE_ERROR"
        result["error"] = str(exc)
        return result
    finally:
        result["elapsed_seconds"] = round(time.time() - start, 1)


def main() -> None:
    parser = argparse.ArgumentParser(description="GitBug-Java generated-suite training runner with SkillBank skills")
    parser.add_argument("--dataset-file", required=True)
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--workspace", default=str(DEFAULT_WORKSPACE))
    parser.add_argument("--skill-bank", default=DEFAULT_SKILL_BANK)
    parser.add_argument("--skill-top-k", type=int, default=10)
    parser.add_argument("--gitbug-repo", default=str(GITBUG_REPO))
    parser.add_argument("--gitbug-cli", default="")
    parser.add_argument("--git-cache", default=str(GITBUG_CACHE))
    parser.add_argument("--checkout-backend", choices=["official", "cache"], default=os.environ.get("GITBUG_OFFICIAL_CHECKOUT_BACKEND", "official"))
    parser.add_argument("--model", default=d4j.MODEL)
    parser.add_argument("--api-key", default="")
    parser.add_argument("--bug-ids", default="", help="Comma-separated bug/source/BID ids to run")
    parser.add_argument("--max-cases", type=int, default=0)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--methods-per-class", type=int, default=suite.DEFAULT_TEST_METHODS)
    parser.add_argument("--tool-steps", type=int, default=50)
    parser.add_argument("--generation-max-tokens", type=int, default=8192)
    parser.add_argument("--generation-repair-rounds", type=int, default=suite.DEFAULT_GENERATION_REPAIR_ROUNDS)
    parser.add_argument("--repair-rounds", type=int, default=suite.DEFAULT_MAX_REPAIR_ROUNDS)
    parser.add_argument("--max-source-chars", type=int, default=suite.DEFAULT_MAX_SOURCE_CHARS)
    parser.add_argument("--test-timeout", type=int, default=500)
    parser.add_argument("--package-mode", choices=["gentest", "same"], default="gentest")
    parser.add_argument("--skip-existing-results", action="store_true")
    args = parser.parse_args()

    if args.api_key:
        os.environ["DEEPSEEK_API_KEY"] = args.api_key
    d4j.DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", d4j.DEEPSEEK_API_KEY)
    d4j.MODEL = args.model or d4j.MODEL
    if not d4j.DEEPSEEK_API_KEY:
        raise SystemExit("[ERROR] DEEPSEEK_API_KEY not set")

    output = Path(args.output)
    workspace = Path(args.workspace)
    output.mkdir(parents=True, exist_ok=True)
    workspace.mkdir(parents=True, exist_ok=True)
    (output / "traces").mkdir(parents=True, exist_ok=True)
    (output / "sessions").mkdir(parents=True, exist_ok=True)
    (output / "results").mkdir(parents=True, exist_ok=True)

    records = _load_records(
        args.dataset_file,
        bug_ids=[x.strip() for x in args.bug_ids.split(",") if x.strip()],
        max_cases=args.max_cases,
    )
    skill_bank = skillbank_tools._load_skill_bank(args.skill_bank)
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    launch = {
        "start": run_id,
        "script": "final_submission/evotest_pipeline/scripts/run_gitbug_generated_suite_training.py",
        "mode": "gitbug_generated_suite_training_inference",
        "stage": "tg_inference_only_no_ea",
        "requires_gitbug_official_docker": True,
        "dataset_file": args.dataset_file,
        "output": str(output),
        "workspace": str(workspace),
        "skill_bank": args.skill_bank,
        "records": len(records),
        "workers": args.workers,
        "model": d4j.MODEL,
        "methods_per_class": args.methods_per_class,
        "tool_steps": args.tool_steps,
        "generation_max_tokens": args.generation_max_tokens,
        "generation_repair_rounds": args.generation_repair_rounds,
        "repair_rounds": args.repair_rounds,
        "test_timeout": args.test_timeout,
        "gitbug_repo": args.gitbug_repo,
        "checkout_backend": args.checkout_backend,
        "skip_existing_results": args.skip_existing_results,
        "gitbug_docker_image": os.environ.get("GITBUG_DOCKER_IMAGE", ""),
        "context_compact_every": os.environ.get("D4J_SUITE_CONTEXT_COMPACT_EVERY", ""),
        "tool_observation_max_chars": os.environ.get("D4J_SUITE_TOOL_OBSERVATION_MAX_CHARS", ""),
    }
    (output / "LAUNCH_INFO.json").write_text(json.dumps(launch, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(launch, indent=2, ensure_ascii=False))

    args_dict = vars(args)
    existing_results = _load_existing_results(output / "results") if args.skip_existing_results else {}
    existing_results = {idx: row for idx, row in existing_results.items() if 0 <= idx < len(records)}
    payloads = [
        (idx, record, args_dict, skill_bank)
        for idx, record in enumerate(records)
        if idx not in existing_results
    ]
    results: list[dict[str, Any]] = [existing_results[idx] for idx in sorted(existing_results)]
    if existing_results:
        tiers: dict[str, int] = {}
        for row in results:
            tier = row.get("final_tier", "UNKNOWN")
            tiers[tier] = tiers.get(tier, 0) + 1
        print(
            f"[skip-existing] loaded {len(existing_results)} existing results; "
            f"remaining={len(payloads)} tiers={tiers}",
            flush=True,
        )
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(run_one, payload): payload[0] for payload in payloads}
        for future in as_completed(futures):
            idx = futures[future]
            try:
                result = future.result()
            except Exception as exc:
                result = {"idx": idx, "final_tier": "PIPELINE_ERROR", "error": str(exc)}
            results.append(result)
            key = _safe_key(str(result.get("record_key") or idx))
            (output / "results" / f"{idx:04d}_{key}.json").write_text(
                json.dumps(result, indent=2, ensure_ascii=False, default=str),
                encoding="utf-8",
            )
            inc_path = output / f"results_{run_id}_pid{os.getpid()}.json"
            inc_path.write_text(json.dumps(sorted(results, key=lambda r: r.get("idx", 0)), indent=2, ensure_ascii=False, default=str), encoding="utf-8")
            tiers: dict[str, int] = {}
            for row in results:
                tiers[row.get("final_tier", "UNKNOWN")] = tiers.get(row.get("final_tier", "UNKNOWN"), 0) + 1
            print(f"[{len(results)}/{len(records)}] idx={idx} tier={result.get('final_tier')} tiers={tiers}", flush=True)

    results.sort(key=lambda r: r.get("idx", 0))
    tiers: dict[str, int] = {}
    for row in results:
        tiers[row.get("final_tier", "UNKNOWN")] = tiers.get(row.get("final_tier", "UNKNOWN"), 0) + 1
    final_path = output / f"final_results_{run_id}_pid{os.getpid()}.json"
    final_path.write_text(
        json.dumps(
            {
                "config": launch,
                "summary": {
                    "total": len(results),
                    "tiers": tiers,
                    "bug_detected": tiers.get("BUG_DETECTED", 0),
                },
                "results": results,
            },
            indent=2,
            ensure_ascii=False,
            default=str,
        ),
        encoding="utf-8",
    )
    print(f"Final results saved to {final_path}")
    print(json.dumps({"total": len(results), "tiers": tiers}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

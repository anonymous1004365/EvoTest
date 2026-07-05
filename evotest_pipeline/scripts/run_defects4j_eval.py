#!/usr/bin/env python3
"""Defects4J runtime helpers for EvoTest generated-suite evaluation.

This module is imported by ``run_defects4j_generated_suite_eval.py``.  It
contains only deterministic Defects4J utilities: checkout/export wrappers,
fixed-view source browsing helpers, generated-suite packaging, dataset
selection, sharding, and result aggregation.  It is not a standalone evaluation
entry point.
"""

from __future__ import annotations

import ast
import fnmatch
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path
from typing import Any

import openai

# Keep local src imports available when scripts are run directly.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_API_URL = os.environ.get("DEEPSEEK_API_URL", "https://api.deepseek.com")
MODEL = os.environ.get("SKILL_MODEL", os.environ.get("DEEPSEEK_MODEL", "deepseek-chat"))
DATA_DIR = Path(os.environ.get("EVOTEST_DATA_DIR", "data"))
TMP_DIR = Path(os.environ.get("EVOTEST_TMP_DIR", "tmp"))
D4J_HOME = Path(os.environ.get("D4J_HOME", str(DATA_DIR / "defects4j")))
D4J_BIN = Path(os.environ.get("D4J_BIN", str(D4J_HOME / "framework" / "bin" / "defects4j")))
D4J_DATASET = Path(os.environ.get("D4J_DATASET", str(DATA_DIR / "defects4j_dataset.json")))

COMPILE_TIMEOUT = int(os.environ.get("D4J_COMPILE_TIMEOUT", "180"))
TEST_TIMEOUT = int(os.environ.get("D4J_TEST_TIMEOUT", "90"))
READ_FILE_MAX_CHARS = int(os.environ.get("SKILL_READ_FILE_MAX_CHARS", "8000"))
TOOL_OUTPUT_MAX_CHARS = int(os.environ.get("D4J_TOOL_OUTPUT_MAX_CHARS", "5000"))
LIST_FILES_MAX_RESULTS = int(os.environ.get("D4J_LIST_FILES_MAX_RESULTS", "50"))
GREP_MAX_RESULTS = int(os.environ.get("D4J_GREP_MAX_RESULTS", "100"))
_BLOCKED_FILE = ".blocked_trigger_tests"

# The generated-suite runner sets these while evaluating a generated host file.
_injected_test_file: str | None = None
_generated_test_methods: list[str] = []


def _parse_triggering_tests(raw) -> list[str]:
    """Parse triggering_tests field which may be a Python-style string list or JSON."""
    if isinstance(raw, list):
        return raw
    if not isinstance(raw, str) or not raw.strip():
        return []
    # Try JSON first
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            return parsed
    except (json.JSONDecodeError, TypeError):
        pass
    # Try Python literal (e.g., "['a::b', 'c::d']")
    try:
        parsed = ast.literal_eval(raw)
        if isinstance(parsed, list):
            return parsed
    except (ValueError, SyntaxError):
        pass
    # Last resort: split by comma
    return [t.strip().strip("'\"") for t in raw.strip("[]").split(",") if t.strip()]


def _parse_triggering_test_code(raw) -> dict[str, str]:
    """Parse triggering_test_code field which may be a Python-style dict string or JSON dict."""
    if isinstance(raw, dict):
        return raw
    if not isinstance(raw, str) or not raw.strip():
        return {}
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            return parsed
    except (json.JSONDecodeError, TypeError):
        pass
    try:
        parsed = ast.literal_eval(raw)
        if isinstance(parsed, dict):
            return parsed
    except (ValueError, SyntaxError):
        pass
    return {}


def _run_cmd(cmd, cwd=None, timeout=60, check=False):
    """Run a command and return (returncode, stdout, stderr)."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", f"TIMEOUT after {timeout}s"
    except Exception as e:
        return -1, "", str(e)


def _d4j(*args, cwd=None, timeout=120):
    """Run a defects4j command."""
    return _run_cmd([str(D4J_BIN)] + list(args), cwd=cwd, timeout=timeout)


def checkout_buggy(project, bug_id, work_dir):
    """Checkout buggy version and export triggering tests for blocking."""
    if os.path.exists(work_dir):
        shutil.rmtree(work_dir, ignore_errors=True)
    os.makedirs(work_dir, exist_ok=True)

    rc, stdout, stderr = _d4j("checkout", "-p", project, "-v", f"{bug_id}b", "-w", work_dir)
    if rc != 0:
        return False, f"Checkout failed: {stderr or stdout}"

    # Export triggering tests and save blocked file list
    _save_blocked_trigger_tests(work_dir)
    return True, work_dir


def checkout_fixed(project, bug_id, work_dir):
    """Checkout fixed version and export triggering tests for blocking."""
    if os.path.exists(work_dir):
        shutil.rmtree(work_dir, ignore_errors=True)
    os.makedirs(work_dir, exist_ok=True)

    rc, stdout, stderr = _d4j("checkout", "-p", project, "-v", f"{bug_id}f", "-w", work_dir)
    if rc != 0:
        return False, f"Checkout failed: {stderr or stdout}"

    # Evaluation TG is fixed-view, but triggering tests remain off-limits.
    _save_blocked_trigger_tests(work_dir)
    return True, work_dir


def d4j_export(work_dir: str, prop: str) -> str:
    """Export a Defects4J property, returning an empty string on failure."""
    rc, stdout, stderr = _d4j("export", "-p", prop, cwd=work_dir)
    if rc != 0:
        return ""
    return stdout.strip().splitlines()[0].strip() if stdout.strip() else ""


def _read_text_limited(path: str | os.PathLike[str], limit: int = 12000) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read(limit)
    except Exception:
        return ""


def _find_focal_file_in_checkout(work_dir: str, bug_data: dict[str, Any]) -> str:
    """Find the focal source file in a Defects4J checkout."""
    hint = _focal_source_hint(bug_data)
    candidates: list[str] = []
    if hint and not hint.startswith("("):
        candidates.append(os.path.join(work_dir, hint))
        if hint.startswith("src/main/java/"):
            candidates.append(os.path.join(work_dir, hint[len("src/main/java/"):]))

    class_name = str(bug_data.get("class_name") or bug_data.get("focal_class") or "").replace("$", ".")
    simple = class_name.rsplit(".", 1)[-1] if class_name else ""
    if simple:
        for root, _dirs, files in os.walk(work_dir):
            if ".git" in root.split(os.sep):
                continue
            if f"{simple}.java" in files:
                candidates.append(os.path.join(root, f"{simple}.java"))
                break

    for path in candidates:
        if path and os.path.isfile(path):
            return path
    return ""


def _sanitize_java_identifier(value: str, default: str = "Generated") -> str:
    """Return a Java-identifier-safe Camel-ish token."""
    parts = re.findall(r"[A-Za-z0-9]+", value or "")
    token = "".join(part[:1].upper() + part[1:] for part in parts if part)
    if not token:
        token = default
    if token[0].isdigit():
        token = f"_{token}"
    return token


def _method_name_from_signature(value: str) -> str:
    """Best-effort method name extraction from a method name/signature field."""
    text = (value or "").strip()
    if not text:
        return ""
    before_paren = text.split("(", 1)[0].strip()
    return before_paren.split()[-1].strip() if before_paren else text


def _focal_package_and_simple_class(bug_data: dict[str, Any]) -> tuple[str, str]:
    """Return the package and simple class for the focal class record."""
    class_name = (
        bug_data.get("class_name")
        or bug_data.get("focal_class")
        or bug_data.get("qualified_class_name")
        or ""
    )
    class_name = str(class_name).strip().replace("$", ".")
    if "." in class_name:
        package, simple = class_name.rsplit(".", 1)
        return package, simple
    return "", class_name or "Generated"


def _focal_source_hint(bug_data: dict[str, Any]) -> str:
    """Best-effort source path hint for the focal class."""
    file_path = str(bug_data.get("file_path") or bug_data.get("focal_file") or "").strip()
    if not file_path:
        package, simple_class = _focal_package_and_simple_class(bug_data)
        if package and simple_class:
            file_path = f"{package.replace('.', '/')}/{simple_class}.java"
    if not file_path:
        return "(unknown; use find_class_file on the focal class)"
    file_path = file_path.replace("\\", "/").lstrip("./")
    if file_path.startswith(("src/", "test/", "org/", "com/", "net/")):
        if not file_path.startswith("src/") and file_path.endswith(".java"):
            return f"src/main/java/{file_path}"
        return file_path
    return file_path


def _find_test_source_root(work_dir: str) -> str:
    """Find the checkout's test source root for generated evaluation tests."""
    exported = d4j_export(work_dir, "dir.src.tests")
    if exported:
        root = os.path.join(work_dir, exported)
        os.makedirs(root, exist_ok=True)
        return root

    for rel in ("src/test/java", "test", "tests"):
        root = os.path.join(work_dir, rel)
        if os.path.isdir(root):
            return root

    root = os.path.join(work_dir, "src", "test", "java")
    os.makedirs(root, exist_ok=True)
    return root


def _strip_code_fences(code: str) -> str:
    normalized = (code or "").strip()
    normalized = re.sub(r"^```(?:java)?\s*\n?", "", normalized)
    normalized = re.sub(r"\n?```\s*$", "", normalized).strip()
    return normalized


def _find_java_void_method_blocks(code: str) -> list[tuple[str, int, int]]:
    """Return ``(method_name, start, end)`` for top-level-looking void methods.

    The TG may submit several @Test methods in one write_test call.  We keep the
    parser intentionally small and conservative: find Java void method
    declarations and balance braces from each declaration.
    """
    text = _strip_code_fences(code)
    allowed_depth = 1 if re.search(r"\bclass\s+\w+", text) else 0
    method_header = re.compile(
        r"(?:@\w+(?:\([^)]*\))?\s*)*"
        r"(?:public|protected|private)?\s*"
        r"void\s+(\w+)\s*\([^)]*\)\s*(?:throws\s+[\w.,\s]+)?\s*\{",
        re.DOTALL,
    )
    blocks: list[tuple[str, int, int]] = []
    for match in method_header.finditer(text):
        if text[:match.start()].count("{") - text[:match.start()].count("}") != allowed_depth:
            continue
        brace_start = text.find("{", match.end() - 1)
        if brace_start < 0:
            continue
        depth = 0
        end = -1
        for pos in range(brace_start, len(text)):
            ch = text[pos]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    end = pos + 1
                    break
        if end > match.start():
            blocks.append((match.group(1), match.start(), end))
    return blocks


def pack_generated_suite(work_dir: str, generated_files: list[str], archive_path: str) -> str:
    """Pack fixed-pass generated test files as a Defects4J-compatible suite archive."""
    os.makedirs(os.path.dirname(archive_path), exist_ok=True)
    test_root = _find_test_source_root(work_dir)
    with tarfile.open(archive_path, "w:bz2") as tar:
        for file_path in generated_files:
            if os.path.exists(file_path):
                tar.add(file_path, arcname=os.path.relpath(file_path, test_root))
    return archive_path


def _save_blocked_trigger_tests(work_dir):
    """Export triggering test class names and save source paths for blocking."""
    rc, stdout, stderr = _d4j("export", "-p", "tests.trigger", cwd=work_dir)
    if rc != 0 or not stdout.strip():
        return

    blocked_paths = set()
    for line in stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        # Format: "fully.qualified.ClassName::methodName"
        class_part = line.split("::")[0]
        rel = class_part.replace(".", "/") + ".java"
        blocked_paths.add(rel)

    if blocked_paths:
        with open(os.path.join(work_dir, _BLOCKED_FILE), "w") as f:
            f.write("\n".join(sorted(blocked_paths)))


def _get_blocked_test_files(work_dir):
    """Return set of relative source-file paths that are blocked."""
    bfile = os.path.join(work_dir, _BLOCKED_FILE)
    if not os.path.exists(bfile):
        return set()
    with open(bfile) as f:
        return {line.strip() for line in f if line.strip()}


def _is_blocked_path(work_dir, relative_path):
    """Check if a path resolves to a blocked triggering test file.

    Once TG has written a generated test via write_test, that generated file is unblocked
    so TG can read and edit it to fix compilation errors.
    """
    global _injected_test_file
    blocked = _get_blocked_test_files(work_dir)
    if not blocked:
        return False
    rel = relative_path.replace("\\", "/").lstrip("./")
    for bp in blocked:
        if rel.endswith(bp) or bp.endswith(rel):
            # Allow access to the generated test file (TG needs to read/edit it).
            # Resolve the user-supplied path to an absolute path and compare with
            # _injected_test_file. Using the blocked-path bp for comparison is
            # unreliable because bp (from d4j export) lacks the source-root prefix
            # (e.g. "tests/", "src/test/") that the real filesystem path includes.
            if _injected_test_file:
                if os.path.isabs(relative_path):
                    resolved = os.path.abspath(relative_path)
                else:
                    resolved = os.path.abspath(os.path.join(work_dir, relative_path))
                if resolved == os.path.abspath(_injected_test_file):
                    return False  # unblock the generated test file
            return True
    return False


def tg_read_file(work_dir, relative_path, start_line=None, end_line=None):
    """Read file with triggering test blocking and auto-truncation."""
    if _is_blocked_path(work_dir, relative_path):
        return "Error: Access denied. This file is a triggering test for the bug."

    full_path = os.path.join(work_dir, relative_path)
    if not os.path.exists(full_path):
        # Try finding recursively
        found = None
        for root, dirs, files in os.walk(work_dir):
            if relative_path in files:
                found = os.path.join(root, relative_path)
                break
            # Handle partial paths like org/package/Class.java
            candidate = os.path.join(root, relative_path)
            if os.path.exists(candidate):
                found = candidate
                break
        if found:
            full_path = found
        else:
            return f"Error: File {relative_path} not found in checkout."

    try:
        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        if _injected_test_file and os.path.abspath(full_path) == os.path.abspath(_injected_test_file):
            generated_names = set(_generated_test_methods or [])
            excerpts = []
            for name, start, end in _find_java_void_method_blocks(content):
                if not generated_names or name in generated_names:
                    excerpts.append(content[start:end].strip())
            if excerpts:
                rendered = (
                    "[Generated test file excerpt only — existing host tests are hidden]\n"
                    + "\n\n".join(excerpts)
                )
                return _truncate_code(rendered, READ_FILE_MAX_CHARS)
            return "[Generated test file excerpt only — no generated methods found]"

        if start_line is not None or end_line is not None:
            lines = content.splitlines(keepends=True)
            total = len(lines)
            s = max(0, int(start_line) - 1) if start_line else 0
            e = min(total, int(end_line)) if end_line else total
            selected = "".join(lines[s:e])
            header = f"[Lines {s+1}-{min(e, total)} of {total}]\n"
            if len(selected) <= READ_FILE_MAX_CHARS:
                return header + selected
            return (
                header
                + selected[:READ_FILE_MAX_CHARS]
                + f"\n... [truncated selected range, total {len(selected)} chars]"
            )

        # Match training TG's read_file budget unless SKILL_READ_FILE_MAX_CHARS overrides it.
        if len(content) <= READ_FILE_MAX_CHARS:
            return content
        return content[:READ_FILE_MAX_CHARS] + f"\n... [truncated, total {len(content)} chars]"
    except Exception as e:
        return f"Error reading file: {e}"


def _matches_file_pattern(rel_path: str, file_pattern: str) -> bool:
    pattern = (file_pattern or "*.java").replace("\\", "/").lstrip("./")
    rel = rel_path.replace("\\", "/").lstrip("./")
    name = os.path.basename(rel)
    if pattern in {"", "*"}:
        return True
    if fnmatch.fnmatch(rel, pattern) or fnmatch.fnmatch(name, pattern):
        return True
    if pattern.startswith("**/"):
        tail = pattern[3:]
        return fnmatch.fnmatch(rel, tail) or fnmatch.fnmatch(name, tail)
    return "/" in pattern and rel == pattern


def tg_grep_code(work_dir, query, file_pattern="*.java"):
    """Search code with path-aware glob matching, filtering blocked files."""
    blocked = _get_blocked_test_files(work_dir)
    try:
        pattern = re.compile(query)
    except re.error:
        pattern = re.compile(re.escape(query))

    raw_lines = []
    try:
        for root, dirs, files in os.walk(work_dir):
            dirs[:] = [d for d in dirs if d != ".git"]
            for filename in files:
                full_path = os.path.join(root, filename)
                rel_path = os.path.relpath(full_path, work_dir)
                rel_norm = rel_path.replace(os.sep, "/")
                if blocked and any(rel_norm.endswith(bp) or bp.endswith(rel_norm) for bp in blocked):
                    continue
                if not _matches_file_pattern(rel_norm, file_pattern):
                    continue
                try:
                    if os.path.getsize(full_path) > 1024 * 1024:
                        continue
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                        for line_no, line in enumerate(f, 1):
                            if pattern.search(line):
                                raw_lines.append(f"./{rel_norm}:{line_no}:{line.rstrip()}")
                                if len(raw_lines) >= GREP_MAX_RESULTS:
                                    raise StopIteration
                except StopIteration:
                    raise
                except Exception:
                    continue
    except StopIteration:
        pass
    except Exception as e:
        return f"Error: {e}"

    if not raw_lines:
        return f"No matches found for '{query}' in {file_pattern} files."

    text = "\n".join(raw_lines)
    if len(text) > TOOL_OUTPUT_MAX_CHARS:
        text = text[:TOOL_OUTPUT_MAX_CHARS] + "\n... (output truncated)"
    return text


def tg_list_files(work_dir, subpath="."):
    """List files, hiding blocked triggering test files.

    NOTE: subpath is always treated as relative to work_dir. An absolute path
    like '/' or '/src' is stripped to '.' or 'src' to prevent filesystem traversal.
    """
    subpath = (subpath or ".").lstrip("/") or "."
    target_dir = os.path.join(work_dir, subpath)
    if not os.path.exists(target_dir):
        return f"Error: Directory {subpath} does not exist"

    blocked = _get_blocked_test_files(work_dir)
    files = []
    total_seen = 0
    for root, dirs, filenames in os.walk(target_dir):
        dirs[:] = [d for d in dirs if d != ".git"]
        for f in filenames:
            rel = os.path.relpath(os.path.join(root, f), work_dir)
            if not any(rel.endswith(bp) or bp.endswith(rel) for bp in blocked):
                total_seen += 1
                files.append(rel)
                if len(files) >= LIST_FILES_MAX_RESULTS:
                    break
        if len(files) >= LIST_FILES_MAX_RESULTS:
            break
    if total_seen >= LIST_FILES_MAX_RESULTS:
        files.append(f"... truncated to first {LIST_FILES_MAX_RESULTS} files")
    return json.dumps(files)


def _build_client():
    return openai.OpenAI(
        api_key=DEEPSEEK_API_KEY,
        base_url=DEEPSEEK_API_URL,
    )


def _truncate_code(code: str, max_chars: int = 8000) -> str:
    if not code:
        return ""
    if len(code) <= max_chars:
        return code
    half = max_chars // 2
    return code[:half] + f"\n... [truncated, total {len(code)} chars] ...\n" + code[-half:]


def _normalize_d4j_record(raw: dict[str, Any]) -> dict[str, Any]:
    """Normalize one Defects4J focal record from the dataset."""
    record = dict(raw)
    record["triggering_tests"] = _parse_triggering_tests(record.get("triggering_tests", []))
    record["triggering_test_code"] = _parse_triggering_test_code(record.get("triggering_test_code", {}))
    if "class_name" not in record and record.get("focal_class"):
        record["class_name"] = record.get("focal_class", "")
    if "method_name" not in record and record.get("focal_method"):
        record["method_name"] = _method_name_from_signature(str(record.get("focal_method", "")))
    return record


def _record_display_key(record: dict[str, Any], focal_idx: int) -> str:
    return (
        f"{record.get('project')}-{record.get('bug_id')}#focal{focal_idx}:"
        f"{record.get('class_name', '')}.{record.get('method_name', '')}"
    )


def _aggregate_bug_tier(focal_results: list[dict[str, Any]]) -> str:
    """Aggregate focal-record outcomes to the paper's bug-level OR semantics."""
    tiers = [r.get("final_tier", "UNKNOWN") for r in focal_results]
    if "BUG_DETECTED" in tiers:
        return "BUG_DETECTED"
    for tier in ("PASS_BOTH", "FAIL_ON_FIXED", "COMPILE_FAIL", "NO_TEST_GENERATED", "PHASE_A_FAIL", "PIPELINE_ERROR"):
        if tier in tiers:
            return tier
    return tiers[0] if tiers else "NO_FOCAL_RECORDS"


def _group_records_by_bug(records: list[dict[str, Any]]) -> dict[tuple[str, str], list[dict[str, Any]]]:
    from collections import defaultdict

    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for raw in records:
        rec = _normalize_d4j_record(raw)
        grouped[(str(rec["project"]), str(rec["bug_id"]))].append(rec)
    return dict(grouped)


def _bug_id_sort_value(bug_id: Any):
    bug_id_str = str(bug_id)
    return (0, int(bug_id_str)) if bug_id_str.isdigit() else (1, bug_id_str)


def _bug_group_sort_key(group: list[dict[str, Any]]):
    first = group[0]
    return (str(first.get("project", "")), _bug_id_sort_value(first.get("bug_id", "")))


def _bug_key_for_group(group: list[dict[str, Any]]) -> str:
    first = group[0]
    return f"{first.get('project')}-{first.get('bug_id')}"


def select_all_bug_groups(dataset_path, output_dir=None):
    """Select every Defects4J bug group, keeping all focal records per bug."""
    with open(dataset_path) as f:
        data = json.load(f)

    selected = sorted(_group_records_by_bug(data).values(), key=_bug_group_sort_key)
    total_focal = sum(len(group) for group in selected)
    print(f"[INFO] Selected all {len(selected)} bug groups ({total_focal} focal records)")

    if output_dir is not None:
        selection_path = Path(output_dir) / "all_bug_selection.json"
        selection_log = [
            {
                "bug_key": _bug_key_for_group(group),
                "num_focal_records": len(group),
                "first_class_name": group[0].get("class_name", ""),
                "first_method_name": group[0].get("method_name", ""),
            }
            for group in selected
        ]
        with open(selection_path, "w") as f:
            json.dump(selection_log, f, indent=2)
        print(f"[INFO] Full bug list saved to {selection_path}")

    return selected


def read_bug_list_file(path: str | os.PathLike[str]) -> list[str]:
    """Read Project-BugId entries from a newline-delimited list."""
    specs = []
    with open(path) as f:
        for line in f:
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                specs.append(stripped)
    return specs


def select_bug_groups_by_specs(dataset_path, bug_specs: list[str]) -> list[list[dict[str, Any]]]:
    """Select explicit Project-BugId bug groups from the dataset."""
    with open(dataset_path) as f:
        data = json.load(f)

    by_bug = _group_records_by_bug(data)
    selected = []
    missing = []
    seen = set()
    for bug_spec in bug_specs:
        parts = bug_spec.split("-", 1)
        if len(parts) != 2:
            missing.append(bug_spec)
            continue
        project, bug_id = parts
        key = (project, bug_id)
        if key in seen:
            continue
        seen.add(key)
        group = by_bug.get(key)
        if group:
            selected.append(group)
        else:
            missing.append(bug_spec)

    if missing:
        print(f"[WARN] Skipped {len(missing)} unknown bug specs: {', '.join(missing[:10])}")
        if len(missing) > 10:
            print(f"[WARN] ... and {len(missing) - 10} more")
    print(f"[INFO] Running {len(selected)} specified bugs")
    return selected


def _result_bug_key(result: dict[str, Any]) -> str:
    bug_key = result.get("bug_key")
    if bug_key:
        return str(bug_key)
    project = result.get("project")
    bug_id = result.get("bug_id")
    if project is None or bug_id is None:
        return ""
    return f"{project}-{bug_id}"


def _iter_result_records(payload: Any):
    if isinstance(payload, list):
        for item in payload:
            if isinstance(item, dict):
                yield item
    elif isinstance(payload, dict):
        results = payload.get("results")
        if isinstance(results, list):
            for item in results:
                if isinstance(item, dict):
                    yield item
        elif payload.get("final_tier") and _result_bug_key(payload):
            yield payload


def completed_bug_keys_from_paths(paths: list[str | os.PathLike[str]]) -> set[str]:
    """Collect bug keys already present in prior eval result files."""
    completed: set[str] = set()
    result_files: list[Path] = []

    for raw_path in paths:
        path = Path(raw_path)
        if not path.exists():
            continue
        if path.is_file():
            result_files.append(path)
            continue
        result_files.extend(path.rglob("final_results_*.json"))
        result_files.extend(path.rglob("results_*.json"))
        result_files.extend(path.rglob("*.jsonl"))

    for result_file in sorted(set(result_files)):
        try:
            if result_file.suffix == ".jsonl":
                with open(result_file) as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        for result in _iter_result_records(json.loads(line)):
                            bug_key = _result_bug_key(result)
                            if bug_key and result.get("final_tier"):
                                completed.add(bug_key)
            else:
                with open(result_file) as f:
                    payload = json.load(f)
                for result in _iter_result_records(payload):
                    bug_key = _result_bug_key(result)
                    if bug_key and result.get("final_tier"):
                        completed.add(bug_key)
        except Exception as exc:
            print(f"[WARN] Failed to read prior result file {result_file}: {exc}")

    return completed


def filter_completed_bug_groups(
    selected: list[list[dict[str, Any]]],
    completed_bug_keys: set[str],
) -> list[list[dict[str, Any]]]:
    if not completed_bug_keys:
        return selected
    filtered = [group for group in selected if _bug_key_for_group(group) not in completed_bug_keys]
    print(f"[INFO] Skipped {len(selected) - len(filtered)} completed bugs from prior results")
    return filtered


def apply_bug_shard(
    selected: list[list[dict[str, Any]]],
    *,
    num_shards: int,
    shard_index: int,
) -> list[list[dict[str, Any]]]:
    if num_shards <= 1:
        return selected
    if shard_index < 0 or shard_index >= num_shards:
        raise ValueError(f"shard_index must be in [0, {num_shards}), got {shard_index}")
    sharded = [group for idx, group in enumerate(selected) if idx % num_shards == shard_index]
    print(f"[INFO] Shard {shard_index}/{num_shards}: {len(sharded)} bug groups")
    return sharded


def select_17_bug_groups(dataset_path, output_dir):
    """Select one bug per project and include all focal records for that bug."""
    with open(dataset_path) as f:
        data = json.load(f)

    from collections import defaultdict
    by_bug = _group_records_by_bug(data)
    bug_keys_by_project = defaultdict(list)
    for (project, bug_id), records in by_bug.items():
        bug_keys_by_project[project].append((bug_id, records))

    selected = []
    selection_log = {}
    for project in sorted(bug_keys_by_project.keys()):
        bug_groups = sorted(bug_keys_by_project[project], key=lambda x: int(x[0]) if str(x[0]).isdigit() else str(x[0]))
        chosen_bug_id = None
        chosen_records = None
        for bug_id, records in bug_groups:
            if any(r.get("triggering_tests") for r in records) and any(r.get("fixed_code") or r.get("code") for r in records):
                chosen_bug_id = bug_id
                chosen_records = records
                break
        if chosen_records is None:
            chosen_bug_id, chosen_records = bug_groups[0]
        selected.append(chosen_records)
        first = chosen_records[0]
        selection_log[project] = {
            "bug_id": chosen_bug_id,
            "num_focal_records": len(chosen_records),
            "first_class_name": first.get("class_name", ""),
            "first_method_name": first.get("method_name", ""),
            "triggering_tests": first.get("triggering_tests", [])[:3],
        }

    # Save selection log
    selection_path = os.path.join(str(output_dir), "bug_selection.json")
    with open(selection_path, "w") as f:
        json.dump(selection_log, f, indent=2)
    print(f"[INFO] Selected {len(selected)} bugs, list saved to {selection_path}")

    for proj, info in selection_log.items():
        print(
            f"  {proj}-{info['bug_id']}: {info['num_focal_records']} focal records "
            f"(first {info['first_class_name']}.{info['first_method_name']})"
        )

    return selected



if __name__ == "__main__":
    raise SystemExit(
        "run_defects4j_eval.py is a helper module. "
        "Use run_defects4j_generated_suite_eval.py for EvoTest evaluation."
    )

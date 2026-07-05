"""Adapter helpers for probing GitBug-Java's official checkout/run path.

This module intentionally stays outside verification_coach.py.  It is a
small prototype layer for resolving our focal-method records to official
GitBug-Java BIDs and invoking the upstream CLI.
"""

from __future__ import annotations

import json
import os
import re
import shlex
import shutil
import subprocess
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


def _safe_name(value: str) -> str:
    return "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in value)


def _tail(text: str, limit: int = 4000) -> str:
    if len(text) <= limit:
        return text
    return text[-limit:]


def _data_cache_dir(name: str, fallback_root: Path) -> Path:
    data_root = (
        os.environ.get("EVOTEST_DATA_DIR")
        or os.environ.get("EVOTEST_OUTPUT_DIR")
        or os.environ.get("SKILL_MINING_DATA")
        or os.environ.get("SKILL_MINING_OUTPUT")
    )
    if data_root:
        return Path(data_root) / "cache" / name
    return fallback_root / name


def _write_dependency_cache_config(maven_repo: Path, gradle_home: Path) -> None:
    """Install conservative Maven/Gradle mirror config into shared caches.

    The GitBug-Java official Docker runner executes many independent projects.
    Without a shared cache and mirror, concurrent Gradle/Maven resolution often
    trips Maven Central / Gradle Plugin Portal 429 limits.  These files live in
    the mounted cache directories, so they are outside project workspaces and
    do not alter the checked-out GitBug projects.
    """
    maven_repo.mkdir(parents=True, exist_ok=True)
    gradle_home.mkdir(parents=True, exist_ok=True)

    settings = maven_repo / "settings.xml"
    if not settings.exists():
        settings.write_text(
            """<settings xmlns="http://maven.apache.org/SETTINGS/1.0.0"
          xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xsi:schemaLocation="http://maven.apache.org/SETTINGS/1.0.0 https://maven.apache.org/xsd/settings-1.0.0.xsd">
  <mirrors>
    <mirror>
      <id>aliyun-public</id>
      <mirrorOf>central</mirrorOf>
      <name>Aliyun Maven public mirror</name>
      <url>https://maven.aliyun.com/repository/public</url>
    </mirror>
  </mirrors>
</settings>
""",
            encoding="utf-8",
        )

    init_dir = gradle_home / "init.d"
    init_dir.mkdir(parents=True, exist_ok=True)
    init_script = init_dir / "gitbug-mirrors.gradle"
    if not init_script.exists():
        init_script.write_text(
            """settingsEvaluated { settings ->
    settings.pluginManagement {
        repositories {
            maven { url 'https://maven.aliyun.com/repository/gradle-plugin' }
            maven { url 'https://maven.aliyun.com/repository/public' }
            gradlePluginPortal()
            mavenCentral()
        }
    }
}

allprojects {
    buildscript {
        repositories {
            maven { url 'https://maven.aliyun.com/repository/gradle-plugin' }
            maven { url 'https://maven.aliyun.com/repository/public' }
            google()
            mavenCentral()
            gradlePluginPortal()
        }
    }
    repositories {
        maven { url 'https://maven.aliyun.com/repository/public' }
        google()
        mavenCentral()
    }
}
""",
            encoding="utf-8",
        )


def _contains_test_report(project_path: Path) -> bool:
    for pattern in (
        "target/surefire-reports/TEST-*.xml",
        "target/failsafe-reports/TEST-*.xml",
        "build/test-results/**/TEST-*.xml",
    ):
        if any(project_path.rglob(pattern)):
            return True
    return False


def _wait_for_test_reports(project_path: Path, timeout_seconds: float = 3.0) -> None:
    deadline = time.time() + max(0.0, timeout_seconds)
    while time.time() < deadline:
        if _contains_test_report(project_path):
            return
        time.sleep(0.2)


@dataclass
class CommandResult:
    cmd: list[str]
    cwd: str | None
    returncode: int | None = None
    duration_ms: int = 0
    stdout_tail: str = ""
    stderr_tail: str = ""
    error: str = ""

    @property
    def ok(self) -> bool:
        return self.returncode == 0 and not self.error

    def as_dict(self) -> dict[str, Any]:
        return {
            "cmd": self.cmd,
            "cwd": self.cwd,
            "returncode": self.returncode,
            "duration_ms": self.duration_ms,
            "stdout_tail": self.stdout_tail,
            "stderr_tail": self.stderr_tail,
            "error": self.error,
        }


@dataclass
class OfficialGitBugResult:
    bid: str
    work_root: Path
    dry_run: bool
    commands: dict[str, CommandResult] = field(default_factory=dict)
    test_results: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        fixed = self.test_results.get("fixed") or {}
        buggy = self.test_results.get("buggy") or {}
        fixed_passed = self.commands.get("run_fixed", CommandResult([], None)).ok
        buggy_failed = (
            "run_buggy" in self.commands
            and self.commands["run_buggy"].returncode not in (None, 0)
            and not self.commands["run_buggy"].error
        )
        return {
            "bid": self.bid,
            "work_root": str(self.work_root),
            "dry_run": self.dry_run,
            "fixed_passed": fixed_passed,
            "buggy_failed": buggy_failed,
            "official_shape_ok": fixed_passed and buggy_failed,
            "fixed_summary": summarize_test_results(fixed),
            "buggy_summary": summarize_test_results(buggy),
            "metadata": self.metadata,
            "commands": {name: result.as_dict() for name, result in self.commands.items()},
            "test_results": self.test_results,
        }


def summarize_test_results(results: dict[str, Any]) -> dict[str, Any]:
    if not results:
        return {}
    return {
        "expected_tests": results.get("expected_tests"),
        "executed_tests": results.get("executed_tests"),
        "passing_tests": results.get("passing_tests"),
        "failing_tests": results.get("failing_tests"),
        "missing_tests": len(results.get("missing_tests") or []),
        "unexpected_tests": len(results.get("unexpected_tests") or []),
        "failed_tests": results.get("failed_tests") or [],
    }


def official_gitbug_enabled(dataset: str | None = None) -> bool:
    """Return whether the official GitBug-Java runner should be used."""
    enabled = os.environ.get("SKILL_USE_GITBUG_OFFICIAL", "").strip().lower()
    if enabled not in {"1", "true", "yes", "on"}:
        return False
    return dataset in {None, "", "gitbug-java"}


def _official_backend() -> str:
    return os.environ.get("GITBUG_OFFICIAL_BACKEND", "official").strip().lower()


def resolve_official_bid(record: dict[str, Any], gitbug_repo: Path | None = None) -> tuple[str, dict[str, Any]]:
    """Resolve a skill-mining focal record to the upstream GitBug-Java BID.

    Current focal records usually carry `bug_id` as `<project-file-stem>-<line>`,
    not the official BID.  If the GitBug-Java repo is available, resolve that
    source id against `data/bugs/*.json`.  Otherwise fall back to the stable BID
    formula used by upstream: `<repository with / replaced by ->-<fixed sha[:12]>`.
    """
    explicit = record.get("gitbug_bid") or record.get("bid")
    if explicit:
        return str(explicit), {"resolution": "explicit"}

    source_id = str(record.get("source_id") or record.get("bug_id") or "")
    if gitbug_repo is not None and source_id:
        resolved = _resolve_from_gitbug_data(source_id, gitbug_repo)
        if resolved is not None:
            return resolved

    project = str(record.get("project") or "")
    fixed_sha = str(record.get("fixed_version") or record.get("commit_hash") or "")
    if project and fixed_sha:
        return f"{project.replace('/', '-')}-{fixed_sha[:12]}", {
            "resolution": "project_and_fixed_sha",
            "warning": "Resolved without checking GitBug-Java data/bugs metadata.",
        }

    raise ValueError(
        "Cannot resolve official GitBug-Java BID. Provide `bid`/`gitbug_bid`, "
        "or a focal record with project+fixed_version, or set --gitbug-repo so "
        "`bug_id` can be resolved through data/bugs/*.json."
    )


def _resolve_from_gitbug_data(source_id: str, gitbug_repo: Path) -> tuple[str, dict[str, Any]] | None:
    if not source_id:
        return None

    bugs_dir = gitbug_repo / "data" / "bugs"
    if not bugs_dir.exists():
        return None

    try:
        repo_stem, line_number_text = source_id.rsplit("-", 1)
        line_number = int(line_number_text)
    except ValueError:
        return None

    bug_file = bugs_dir / f"{repo_stem}.json"
    if not bug_file.exists():
        return None

    with bug_file.open(encoding="utf-8") as f:
        for idx, line in enumerate(f):
            if idx != line_number:
                continue
            bug = json.loads(line)
            repository = str(bug["repository"])
            fixed_sha = str(bug["commit_hash"])
            bid = f"{repository.replace('/', '-')}-{fixed_sha[:12]}"
            return bid, {
                "resolution": "source_id_data_bugs",
                "source_id": source_id,
                "repository": repository,
                "commit_hash": fixed_sha,
                "previous_commit_hash": bug.get("previous_commit_hash", ""),
                "strategy": bug.get("strategy", ""),
            }
    return None


def find_bug_metadata_by_bid(bid: str, gitbug_repo: Path) -> dict[str, Any] | None:
    """Find the upstream GitBug-Java metadata record for an official BID."""
    bugs_dir = gitbug_repo / "data" / "bugs"
    if not bugs_dir.exists():
        return None

    for bug_file in sorted(bugs_dir.glob("*.json")):
        with bug_file.open(encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                bug = json.loads(line)
                repository = str(bug.get("repository") or "")
                fixed_sha = str(bug.get("commit_hash") or "")
                candidate = f"{repository.replace('/', '-')}-{fixed_sha[:12]}"
                if candidate == bid:
                    return bug
    return None


class OfficialGitBugRunner:
    """Thin wrapper over `gitbug-java checkout` and `gitbug-java run`."""

    def __init__(
        self,
        gitbug_repo: Path,
        work_root: Path,
        cli: str | None = None,
        act_cache_dir: Path | None = None,
        git_cache: Path | None = None,
        checkout_backend: str = "official",
        timeout: int = 0,
        dry_run: bool = False,
    ) -> None:
        self.gitbug_repo = gitbug_repo
        self.work_root = work_root
        self.cli = cli or self._default_cli()
        self.act_cache_dir = act_cache_dir
        self.git_cache = git_cache
        self.checkout_backend = checkout_backend
        self.timeout = timeout
        self.dry_run = dry_run

    def check_prerequisites(self, require_docker: bool = False) -> list[str]:
        issues: list[str] = []
        if not self.gitbug_repo.exists():
            issues.append(f"GitBug-Java repo not found: {self.gitbug_repo}")
        if not (self.gitbug_repo / "data" / "bugs").exists():
            issues.append(f"Missing GitBug-Java data/bugs under: {self.gitbug_repo}")
        if not self._cli_path_exists():
            issues.append(f"gitbug-java CLI not found or not executable: {self.cli}")
        if not (self.gitbug_repo / "bin" / "act").exists():
            issues.append(f"modified act not found: {self.gitbug_repo / 'bin' / 'act'}")
        if require_docker and shutil.which("docker") is None:
            issues.append("docker CLI not found on PATH")
        return issues

    def probe_bid(
        self,
        bid: str,
        run_buggy: bool = True,
        run_fixed: bool = True,
        checkout_only: bool = False,
        keep_workdir: bool = False,
    ) -> OfficialGitBugResult:
        case_root = self.work_root / _safe_name(bid)
        if not self.dry_run:
            if case_root.exists() and not keep_workdir:
                shutil.rmtree(case_root)
            case_root.mkdir(parents=True, exist_ok=True)

        result = OfficialGitBugResult(
            bid=bid,
            work_root=case_root,
            dry_run=self.dry_run,
            metadata={
                "gitbug_repo": str(self.gitbug_repo),
                "cli": self.cli,
                "act_cache_dir": str(self.act_cache_dir) if self.act_cache_dir else "",
                "git_cache": str(self.git_cache) if self.git_cache else "",
                "checkout_backend": self.checkout_backend,
                "timeout": self.timeout,
            },
        )

        if run_buggy:
            buggy_dir = case_root / "buggy"
            result.commands["checkout_buggy"] = self._checkout(bid, buggy_dir, fixed=False)
            if result.commands["checkout_buggy"].ok and not checkout_only:
                result.commands["run_buggy"] = self._run(self._run_cmd(buggy_dir))
                result.test_results["buggy"] = self._load_test_results(buggy_dir)

        if run_fixed:
            fixed_dir = case_root / "fixed"
            result.commands["checkout_fixed"] = self._checkout(bid, fixed_dir, fixed=True)
            if result.commands["checkout_fixed"].ok and not checkout_only:
                result.commands["run_fixed"] = self._run(self._run_cmd(fixed_dir))
                result.test_results["fixed"] = self._load_test_results(fixed_dir)

        return result

    def checkout_version(self, bid: str, dest: Path, *, fixed: bool, strip_test_dirs: bool = False) -> CommandResult:
        """Checkout one version through the upstream GitBug-Java CLI."""
        if not self.dry_run:
            if dest.exists():
                shutil.rmtree(dest)
            dest.parent.mkdir(parents=True, exist_ok=True)
        result = self._checkout(bid, dest, fixed=fixed)
        if result.ok and strip_test_dirs and not self.dry_run:
            _strip_test_dirs(dest)
        return result

    def verify_injected_test_method(
        self,
        *,
        bid: str,
        test_method_code: str,
        test_method_name: str,
        failing_test_class: str,
        keep_workdir: bool = False,
    ) -> dict[str, Any]:
        """Inject one TG-generated test method and classify fixed/buggy behavior.

        This keeps GitBug-Java's official checkout/run path, but evaluates the
        generated method semantics instead of requiring the whole original
        benchmark test set to match exactly.
        """
        if _official_backend() == "docker_direct":
            return self.verify_injected_test_method_docker_direct(
                bid=bid,
                test_method_code=test_method_code,
                test_method_name=test_method_name,
                failing_test_class=failing_test_class,
                keep_workdir=keep_workdir,
            )

        case_root = self.work_root / _safe_name(f"{bid}-{int(time.time() * 1000)}")
        if not self.dry_run:
            if case_root.exists() and not keep_workdir:
                shutil.rmtree(case_root)
            case_root.mkdir(parents=True, exist_ok=True)

        report: dict[str, Any] = {
            "bid": bid,
            "work_root": str(case_root),
            "commands": {},
            "fixed": {},
            "buggy": {},
            "tier": "",
            "passed": False,
            "coach_feedback": "",
        }

        fixed_dir = case_root / "fixed"
        buggy_dir = case_root / "buggy"
        report["commands"]["checkout_fixed"] = self.checkout_version(bid, fixed_dir, fixed=True).as_dict()
        report["commands"]["checkout_buggy"] = self.checkout_version(bid, buggy_dir, fixed=False).as_dict()
        if report["commands"]["checkout_fixed"].get("returncode") != 0:
            report["tier"] = "INFRA_CHECKOUT_FAIL"
            report["coach_feedback"] = "Failed to checkout fixed version via official GitBug-Java."
            return report
        if report["commands"]["checkout_buggy"].get("returncode") != 0:
            report["tier"] = "INFRA_CHECKOUT_FAIL"
            report["coach_feedback"] = "Failed to checkout buggy version via official GitBug-Java."
            return report

        fixed_inject = inject_test_method_into_existing_class(
            fixed_dir, test_method_code, test_method_name, failing_test_class
        )
        buggy_inject = inject_test_method_into_existing_class(
            buggy_dir, test_method_code, test_method_name, failing_test_class
        )
        report["fixed"]["inject"] = fixed_inject
        report["buggy"]["inject"] = buggy_inject
        if fixed_inject.get("status") != "success":
            report["tier"] = "COMPILE_FAIL"
            report["coach_feedback"] = f"Failed to inject test into fixed version: {fixed_inject.get('message', '')}"
            return report
        if buggy_inject.get("status") != "success":
            report["tier"] = "COMPILE_FAIL"
            report["coach_feedback"] = f"Failed to inject test into buggy version: {buggy_inject.get('message', '')}"
            return report

        fixed_run = self._run(self._run_cmd(fixed_dir))
        report["commands"]["run_fixed"] = fixed_run.as_dict()
        report["fixed"]["test_results"] = self._load_test_results(fixed_dir)
        fixed_eval = evaluate_generated_method_run(
            report["fixed"]["test_results"], fixed_run, test_method_name
        )
        report["fixed"]["generated_method_eval"] = fixed_eval

        if fixed_eval["status"] == "infra_error":
            report["tier"] = "INFRA_RUNTIME_FAIL"
            report["coach_feedback"] = fixed_eval["message"]
            return report
        if not fixed_eval["compile_ok"]:
            report["tier"] = "COMPILE_FAIL"
            report["coach_feedback"] = fixed_eval["message"]
            return report
        if not fixed_eval["passed"]:
            buggy_message = "skipped to avoid spending an extra official GitBug-Java run"
            if os.environ.get("GITBUG_RUN_BUGGY_DIAGNOSTIC_ON_FIXED_FAIL", "").strip().lower() in {
                "1", "true", "yes", "on",
            }:
                buggy_diag = self._run(self._run_cmd(buggy_dir))
                report["commands"]["run_buggy_diagnostic"] = buggy_diag.as_dict()
                report["buggy"]["test_results"] = self._load_test_results(buggy_dir)
                report["buggy"]["generated_method_eval"] = evaluate_generated_method_run(
                    report["buggy"]["test_results"], buggy_diag, test_method_name
                )
                buggy_message = report["buggy"]["generated_method_eval"]["message"]
            report["tier"] = "FAIL_ON_FIXED"
            report["coach_feedback"] = (
                "Observed verification behavior:\n"
                "- Expected shape: fixed=PASS, buggy=FAIL.\n"
                f"- Fixed version: FAIL. {fixed_eval['message']}\n"
                f"- Buggy version diagnostic: {buggy_message}.\n\n"
                "Tier: FAIL_ON_FIXED. The test currently rejects the correct fixed behavior."
            )
            return report

        buggy_run = self._run(self._run_cmd(buggy_dir))
        report["commands"]["run_buggy"] = buggy_run.as_dict()
        report["buggy"]["test_results"] = self._load_test_results(buggy_dir)
        buggy_eval = evaluate_generated_method_run(
            report["buggy"]["test_results"], buggy_run, test_method_name
        )
        report["buggy"]["generated_method_eval"] = buggy_eval
        if buggy_eval["status"] == "infra_error":
            report["tier"] = "INFRA_RUNTIME_FAIL"
            report["coach_feedback"] = buggy_eval["message"]
            return report
        if not buggy_eval["compile_ok"]:
            report["tier"] = "COMPILE_FAIL"
            report["coach_feedback"] = buggy_eval["message"]
            return report
        if not buggy_eval["passed"]:
            report["tier"] = "BUG_DETECTED"
            report["passed"] = True
            report["coach_feedback"] = (
                "Observed verification behavior:\n"
                "- Expected shape: fixed=PASS, buggy=FAIL.\n"
                f"- Fixed version: PASS. {fixed_eval['message']}\n"
                f"- Buggy version: FAIL. {buggy_eval['message']}\n\n"
                "Tier: BUG_DETECTED. The test accepts the fixed behavior and rejects the buggy behavior."
            )
            return report

        report["tier"] = "PASS_BOTH"
        report["coach_feedback"] = (
            "Observed verification behavior:\n"
            "- Expected shape: fixed=PASS, buggy=FAIL.\n"
            f"- Fixed version: PASS. {fixed_eval['message']}\n"
            f"- Buggy version: PASS. {buggy_eval['message']}\n\n"
            "Tier: PASS_BOTH. The test is compatible with the fixed behavior, but the buggy version also passes."
            )
        return report

    def verify_generated_test_class_docker_direct(
        self,
        *,
        bid: str,
        test_class_code: str,
        failing_test_class: str,
        keep_workdir: bool = False,
    ) -> dict[str, Any]:
        """Inject a generated JUnit test class as methods into the host class.

        This is the GitBug-Java analogue of the Defects4J generated-suite
        verifier.  We keep the official GitBug-Java checkout and Docker-direct
        execution path, but the generated class is adapted to GitBug-Java's
        existing test class by inserting all generated ``@Test`` methods into
        ``failing_test_class``.  The Docker command is then narrowed to only the
        generated methods, so original triggering tests cannot accidentally
        count as bug detection.
        """
        case_root = self.work_root / _safe_name(f"{bid}-suite-{int(time.time() * 1000)}")
        if not self.dry_run:
            if case_root.exists() and not keep_workdir:
                shutil.rmtree(case_root)
            case_root.mkdir(parents=True, exist_ok=True)

        report: dict[str, Any] = {
            "bid": bid,
            "work_root": str(case_root),
            "backend": "gitbug-official-docker-direct-generated-suite",
            "commands": {},
            "fixed": {},
            "buggy": {},
            "tier": "",
            "passed": False,
            "coach_feedback": "",
            "generated_test_methods": [],
        }

        fixed_dir = case_root / "fixed"
        buggy_dir = case_root / "buggy"
        report["commands"]["checkout_fixed"] = self.checkout_version(bid, fixed_dir, fixed=True).as_dict()
        report["commands"]["checkout_buggy"] = self.checkout_version(bid, buggy_dir, fixed=False).as_dict()
        if report["commands"]["checkout_fixed"].get("returncode") != 0:
            report["tier"] = "INFRA_CHECKOUT_FAIL"
            report["coach_feedback"] = "Failed to checkout fixed version via official GitBug-Java."
            return report
        if report["commands"]["checkout_buggy"].get("returncode") != 0:
            report["tier"] = "INFRA_CHECKOUT_FAIL"
            report["coach_feedback"] = "Failed to checkout buggy version via official GitBug-Java."
            return report

        fixed_inject = inject_generated_test_class_into_existing_class(
            fixed_dir,
            test_class_code,
            failing_test_class,
        )
        method_names = list(fixed_inject.get("test_method_names") or [])
        buggy_inject = inject_generated_test_class_into_existing_class(
            buggy_dir,
            test_class_code,
            failing_test_class,
            preferred_names=method_names,
        )
        report["fixed"]["inject"] = fixed_inject
        report["buggy"]["inject"] = buggy_inject
        report["generated_test_methods"] = method_names
        if fixed_inject.get("status") != "success":
            report["tier"] = "COMPILE_FAIL"
            report["coach_feedback"] = f"Failed to inject generated suite into fixed version: {fixed_inject.get('message', '')}"
            return report
        if buggy_inject.get("status") != "success":
            report["tier"] = "COMPILE_FAIL"
            report["coach_feedback"] = f"Failed to inject generated suite into buggy version: {buggy_inject.get('message', '')}"
            return report
        if not method_names:
            report["tier"] = "NO_TEST_GENERATED"
            report["coach_feedback"] = "Generated class did not contain any injectable test methods."
            return report

        fixed_run = self._run_docker_direct(
            fixed_dir,
            "fixed",
            failing_test_class=failing_test_class,
            test_method_name=method_names,
        )
        report["commands"]["run_fixed"] = fixed_run.as_dict()
        _wait_for_test_reports(fixed_dir)
        fixed_results = parse_surefire_results(fixed_dir)
        report["fixed"]["test_results"] = fixed_results
        fixed_eval = evaluate_generated_suite_run(fixed_results, fixed_run, method_names)
        report["fixed"]["generated_suite_eval"] = fixed_eval
        if fixed_eval["status"] == "infra_error":
            report["tier"] = "INFRA_RUNTIME_FAIL"
            report["coach_feedback"] = fixed_eval["message"]
            return report
        if not fixed_eval["compile_ok"]:
            report["tier"] = "COMPILE_FAIL"
            report["coach_feedback"] = fixed_eval["message"]
            return report
        if not fixed_eval["passed"]:
            report["tier"] = "FAIL_ON_FIXED"
            report["coach_feedback"] = (
                "Observed verification behavior:\n"
                "- Expected shape: fixed=PASS, buggy=FAIL.\n"
                f"- Fixed version: FAIL. {fixed_eval['message']}\n"
                "- Buggy version diagnostic: skipped because fixed failed.\n\n"
                "Tier: FAIL_ON_FIXED. The generated suite currently rejects the correct fixed behavior."
            )
            return report

        buggy_run = self._run_docker_direct(
            buggy_dir,
            "buggy",
            failing_test_class=failing_test_class,
            test_method_name=method_names,
        )
        report["commands"]["run_buggy"] = buggy_run.as_dict()
        _wait_for_test_reports(buggy_dir)
        buggy_results = parse_surefire_results(buggy_dir)
        report["buggy"]["test_results"] = buggy_results
        buggy_eval = evaluate_generated_suite_run(buggy_results, buggy_run, method_names)
        report["buggy"]["generated_suite_eval"] = buggy_eval
        if buggy_eval["status"] == "infra_error":
            report["tier"] = "INFRA_RUNTIME_FAIL"
            report["coach_feedback"] = buggy_eval["message"]
            return report
        if not buggy_eval["compile_ok"]:
            report["tier"] = "COMPILE_FAIL"
            report["coach_feedback"] = buggy_eval["message"]
            return report
        if not buggy_eval["passed"]:
            report["tier"] = "BUG_DETECTED"
            report["passed"] = True
            report["coach_feedback"] = (
                "Observed verification behavior:\n"
                "- Expected shape: fixed=PASS, buggy=FAIL.\n"
                f"- Fixed version: PASS. {fixed_eval['message']}\n"
                f"- Buggy version: FAIL. {buggy_eval['message']}\n\n"
                "Tier: BUG_DETECTED. The generated suite accepts the fixed behavior and rejects the buggy behavior."
            )
            return report

        report["tier"] = "PASS_BOTH"
        report["coach_feedback"] = (
            "Observed verification behavior:\n"
            "- Expected shape: fixed=PASS, buggy=FAIL.\n"
            f"- Fixed version: PASS. {fixed_eval['message']}\n"
            f"- Buggy version: PASS. {buggy_eval['message']}\n\n"
            "Tier: PASS_BOTH. The generated suite is compatible with the fixed behavior, but the buggy version also passes."
        )
        return report

    def verify_injected_test_method_docker_direct(
        self,
        *,
        bid: str,
        test_method_code: str,
        test_method_name: str,
        failing_test_class: str,
        keep_workdir: bool = False,
    ) -> dict[str, Any]:
        """Verify a TG method inside the official GitBug-Java base Docker image.

        The upstream `gitbug-java run` path can hang in the Python/act wrapper on
        small hosts. This backend still uses GitBug-Java's official checkout data,
        workflow command, and DockerHub base image, but executes the project
        command directly in `gitbug-java:base` and classifies only the generated
        method from Surefire XML/log output.
        """
        case_root = self.work_root / _safe_name(f"{bid}-{int(time.time() * 1000)}")
        if not self.dry_run:
            if case_root.exists() and not keep_workdir:
                shutil.rmtree(case_root)
            case_root.mkdir(parents=True, exist_ok=True)

        report: dict[str, Any] = {
            "bid": bid,
            "work_root": str(case_root),
            "backend": "gitbug-official-docker-direct",
            "commands": {},
            "fixed": {},
            "buggy": {},
            "tier": "",
            "passed": False,
            "coach_feedback": "",
        }

        fixed_dir = case_root / "fixed"
        buggy_dir = case_root / "buggy"
        report["commands"]["checkout_fixed"] = self.checkout_version(bid, fixed_dir, fixed=True).as_dict()
        report["commands"]["checkout_buggy"] = self.checkout_version(bid, buggy_dir, fixed=False).as_dict()
        if report["commands"]["checkout_fixed"].get("returncode") != 0:
            report["tier"] = "INFRA_CHECKOUT_FAIL"
            report["coach_feedback"] = "Failed to checkout fixed version via official GitBug-Java."
            return report
        if report["commands"]["checkout_buggy"].get("returncode") != 0:
            report["tier"] = "INFRA_CHECKOUT_FAIL"
            report["coach_feedback"] = "Failed to checkout buggy version via official GitBug-Java."
            return report

        fixed_inject = inject_test_method_into_existing_class(
            fixed_dir, test_method_code, test_method_name, failing_test_class
        )
        buggy_inject = inject_test_method_into_existing_class(
            buggy_dir, test_method_code, test_method_name, failing_test_class
        )
        report["fixed"]["inject"] = fixed_inject
        report["buggy"]["inject"] = buggy_inject
        if fixed_inject.get("status") != "success":
            report["tier"] = "COMPILE_FAIL"
            report["coach_feedback"] = f"Failed to inject test into fixed version: {fixed_inject.get('message', '')}"
            return report
        if buggy_inject.get("status") != "success":
            report["tier"] = "COMPILE_FAIL"
            report["coach_feedback"] = f"Failed to inject test into buggy version: {buggy_inject.get('message', '')}"
            return report

        fixed_run = self._run_docker_direct(
            fixed_dir,
            "fixed",
            failing_test_class=failing_test_class,
            test_method_name=test_method_name,
        )
        report["commands"]["run_fixed"] = fixed_run.as_dict()
        _wait_for_test_reports(fixed_dir)
        fixed_results = parse_surefire_results(fixed_dir)
        report["fixed"]["test_results"] = fixed_results
        fixed_eval = evaluate_generated_method_run(fixed_results, fixed_run, test_method_name)
        report["fixed"]["generated_method_eval"] = fixed_eval
        if fixed_eval["status"] == "infra_error":
            report["tier"] = "INFRA_RUNTIME_FAIL"
            report["coach_feedback"] = fixed_eval["message"]
            return report
        if not fixed_eval["compile_ok"]:
            report["tier"] = "COMPILE_FAIL"
            report["coach_feedback"] = fixed_eval["message"]
            return report
        if not fixed_eval["passed"]:
            report["tier"] = "FAIL_ON_FIXED"
            report["coach_feedback"] = (
                "Observed verification behavior:\n"
                "- Expected shape: fixed=PASS, buggy=FAIL.\n"
                f"- Fixed version: FAIL. {fixed_eval['message']}\n"
                "- Buggy version diagnostic: skipped because fixed failed.\n\n"
                "Tier: FAIL_ON_FIXED. The test currently rejects the correct fixed behavior."
            )
            return report

        buggy_run = self._run_docker_direct(
            buggy_dir,
            "buggy",
            failing_test_class=failing_test_class,
            test_method_name=test_method_name,
        )
        report["commands"]["run_buggy"] = buggy_run.as_dict()
        _wait_for_test_reports(buggy_dir)
        buggy_results = parse_surefire_results(buggy_dir)
        report["buggy"]["test_results"] = buggy_results
        buggy_eval = evaluate_generated_method_run(buggy_results, buggy_run, test_method_name)
        report["buggy"]["generated_method_eval"] = buggy_eval
        if buggy_eval["status"] == "infra_error":
            report["tier"] = "INFRA_RUNTIME_FAIL"
            report["coach_feedback"] = buggy_eval["message"]
            return report
        if not buggy_eval["compile_ok"]:
            report["tier"] = "COMPILE_FAIL"
            report["coach_feedback"] = buggy_eval["message"]
            return report
        if not buggy_eval["passed"]:
            report["tier"] = "BUG_DETECTED"
            report["passed"] = True
            report["coach_feedback"] = (
                "Observed verification behavior:\n"
                "- Expected shape: fixed=PASS, buggy=FAIL.\n"
                f"- Fixed version: PASS. {fixed_eval['message']}\n"
                f"- Buggy version: FAIL. {buggy_eval['message']}\n\n"
                "Tier: BUG_DETECTED. The test accepts the fixed behavior and rejects the buggy behavior."
            )
            return report

        report["tier"] = "PASS_BOTH"
        report["coach_feedback"] = (
            "Observed verification behavior:\n"
            "- Expected shape: fixed=PASS, buggy=FAIL.\n"
            f"- Fixed version: PASS. {fixed_eval['message']}\n"
            f"- Buggy version: PASS. {buggy_eval['message']}\n\n"
            "Tier: PASS_BOTH. The test is compatible with the fixed behavior, but the buggy version also passes."
        )
        return report

    def _checkout(self, bid: str, dest: Path, fixed: bool) -> CommandResult:
        if self.checkout_backend == "cache":
            return self._checkout_from_cache(bid, dest, fixed=fixed)

        cmd = [self.cli, "checkout", bid, str(dest)]
        if fixed:
            cmd.append("--fixed")
        return self._run(cmd)

    def _checkout_from_cache(self, bid: str, dest: Path, fixed: bool) -> CommandResult:
        label = "--fixed" if fixed else "--buggy"
        command = CommandResult(
            cmd=["cache-checkout", bid, str(dest), label],
            cwd=str(self.gitbug_repo),
        )
        if self.dry_run:
            return command

        started = time.time()
        try:
            if self.git_cache is None:
                raise RuntimeError("cache checkout requires --git-cache")
            bug = find_bug_metadata_by_bid(bid, self.gitbug_repo)
            if bug is None:
                raise RuntimeError(f"Cannot find GitBug-Java metadata for BID: {bid}")
            source = self._cached_repo_path(bug)
            if source is None:
                raise RuntimeError(
                    f"Cached repo not found for {bug.get('repository')} under {self.git_cache}"
                )
            if dest.exists():
                shutil.rmtree(dest)
            dest.parent.mkdir(parents=True, exist_ok=True)

            steps: list[str] = []
            for cmd, stdin_text in [
                (["git", "clone", "--no-hardlinks", str(source), str(dest)], None),
                (["git", "config", "gc.auto", "0"], None),
                (["git", "checkout", "--force", bug["commit_hash" if fixed else "previous_commit_hash"]], None),
            ]:
                proc = self._run_subprocess(cmd, cwd=dest if cmd[1] != "clone" else self.gitbug_repo, stdin_text=stdin_text)
                steps.append(self._format_step(cmd, proc))
                if proc.returncode != 0:
                    command.returncode = proc.returncode
                    command.stderr_tail = "\n".join(steps)
                    return command

            if not fixed:
                if bug.get("non_code_patch") and bug.get("bug_patch"):
                    proc = self._run_subprocess(["git", "apply"], cwd=dest, stdin_text=bug["non_code_patch"])
                    steps.append(self._format_step(["git", "apply", "<non_code_patch>"], proc))
                    if proc.returncode != 0:
                        command.returncode = proc.returncode
                        command.stderr_tail = "\n".join(steps)
                        return command
                if bug.get("test_patch"):
                    proc = self._run_subprocess(["git", "apply"], cwd=dest, stdin_text=bug["test_patch"])
                    steps.append(self._format_step(["git", "apply", "<test_patch>"], proc))
                    if proc.returncode != 0:
                        command.returncode = proc.returncode
                        command.stderr_tail = "\n".join(steps)
                        return command

            subprocess.run(
                ["git", "remote", "set-url", "origin", f"https://github.com/{bug['repository']}"],
                cwd=dest,
                capture_output=True,
                text=True,
            )
            self._remove_workflows(dest)
            workflow_note = self._copy_gitbug_workflow(dest, bug)
            self._write_gitbug_json(dest, bug, fixed=fixed)

            command.returncode = 0
            command.stdout_tail = "\n".join(steps + [workflow_note])
        except Exception as exc:
            command.error = str(exc)
        finally:
            command.duration_ms = int((time.time() - started) * 1000)
        return command

    def _cached_repo_path(self, bug: dict[str, Any]) -> Path | None:
        assert self.git_cache is not None
        clone_url = str(bug.get("clone_url") or "")
        repo_name = clone_url.rstrip("/").split("/")[-1].replace(".git", "")
        candidates = [
            self.git_cache / repo_name,
            self.git_cache / str(bug.get("repository", "")).replace("/", "-"),
        ]
        for candidate in candidates:
            if (candidate / ".git").exists():
                return candidate
        return None

    def _remove_workflows(self, workdir: Path) -> None:
        workflows_dir = workdir / ".github" / "workflows"
        if not workflows_dir.exists():
            return
        for workflow in list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml")):
            workflow.unlink()

    def _copy_gitbug_workflow(self, workdir: Path, bug: dict[str, Any]) -> str:
        pid = str(bug["repository"]).replace("/", "-")
        diff_folder = self.gitbug_repo / "data" / pid / str(bug["commit_hash"])
        workflow_dir = diff_folder / "workflow"
        if not workflow_dir.exists():
            return f"workflow_missing={workflow_dir}"
        workflows = list(workflow_dir.glob("*.yml")) + list(workflow_dir.glob("*.yaml"))
        if not workflows:
            return f"workflow_empty={workflow_dir}"
        dest_dir = workdir / ".github" / "workflows"
        dest_dir.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(workflows[0], dest_dir / workflows[0].name)
        return f"workflow_copied={workflows[0]}"

    def _write_gitbug_json(self, workdir: Path, bug: dict[str, Any], fixed: bool) -> None:
        bug_info = dict(bug)
        bug_info["fixed"] = fixed
        with (workdir / "gitbug.json").open("w", encoding="utf-8") as f:
            json.dump(bug_info, f)

    def _run_subprocess(
        self,
        cmd: list[str],
        cwd: Path,
        stdin_text: str | None = None,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            cmd,
            cwd=cwd,
            input=stdin_text,
            capture_output=True,
            text=True,
            timeout=max(self.timeout + 60, 300) if self.timeout else None,
        )

    def _format_step(self, cmd: list[str], proc: subprocess.CompletedProcess[str]) -> str:
        tail = _tail((proc.stderr or proc.stdout or "").strip(), 1000)
        return f"{' '.join(cmd)} -> {proc.returncode}" + (f"\n{tail}" if tail else "")

    def _run_docker_direct(
        self,
        workdir: Path,
        version: str,
        *,
        failing_test_class: str | None = None,
        test_method_name: str | list[str] | None = None,
    ) -> CommandResult:
        command_text = _workflow_command(workdir)
        command_text = _target_generated_test_command(
            command_text,
            failing_test_class=failing_test_class,
            test_method_name=test_method_name,
        )
        java_version = _required_java_version(workdir)
        java_home = _docker_java_home(java_version)
        java_mount_args = _docker_java_mount_args(java_version)
        if java_home:
            command_text = (
                f'export JAVA_HOME="{java_home}"\n'
                'export PATH="$JAVA_HOME/bin:$PATH"\n'
                "java -version\n"
                f"{command_text}"
            )
        command_text = (
            "export LANG=C.UTF-8\n"
            "export LC_ALL=C.UTF-8\n"
            'export JAVA_TOOL_OPTIONS="${JAVA_TOOL_OPTIONS:-} -Dfile.encoding=UTF-8"\n'
            'export MAVEN_OPTS="${MAVEN_OPTS:-} -Dfile.encoding=UTF-8"\n'
            'export GRADLE_OPTS="${GRADLE_OPTS:-} -Dfile.encoding=UTF-8"\n'
            "mkdir -p /tmp/.m2\n"
            "cp /tmp/m2/settings.xml /tmp/.m2/settings.xml 2>/dev/null || true\n"
            f"{command_text}"
        )
        maven_repo = Path(os.environ.get(
            "GITBUG_DOCKER_MAVEN_REPO",
            str(_data_cache_dir("gitbug-m2", self.work_root)),
        ))
        maven_repo.mkdir(parents=True, exist_ok=True)
        gradle_home = Path(os.environ.get(
            "GITBUG_DOCKER_GRADLE_USER_HOME",
            str(_data_cache_dir("gitbug-gradle", self.work_root)),
        ))
        gradle_home.mkdir(parents=True, exist_ok=True)
        _write_dependency_cache_config(maven_repo, gradle_home)
        docker_image = os.environ.get("GITBUG_DOCKER_IMAGE", "gitbug-java:base")
        user_spec = f"{os.getuid()}:{os.getgid()}"
        docker_cmd = [
            "docker",
            "run",
            "--rm",
            "--network",
            "host",
            "--user",
            user_spec,
            "-e",
            "HOME=/tmp",
            "-e",
            "LANG=C.UTF-8",
            "-e",
            "LC_ALL=C.UTF-8",
            "-e",
            "JAVA_TOOL_OPTIONS=-Dfile.encoding=UTF-8",
            "-e",
            "MAVEN_OPTS=-Dfile.encoding=UTF-8",
            "-e",
            "GRADLE_OPTS=-Dfile.encoding=UTF-8",
            "-e",
            "GRADLE_USER_HOME=/tmp/gradle",
            *(
                ["-e", f"JAVA_HOME={java_home}"]
                if java_home
                else []
            ),
            *java_mount_args,
            "-v",
            f"{maven_repo}:/tmp/m2",
            "-v",
            f"{gradle_home}:/tmp/gradle",
            "-v",
            f"{workdir}:/workspace",
            "-w",
            "/workspace",
            docker_image,
            "bash",
            "-lc",
            _with_maven_repo(command_text),
        ]
        command = CommandResult(cmd=docker_cmd, cwd=str(workdir))
        if self.dry_run:
            return command

        shutil.rmtree(workdir / "target", ignore_errors=True)
        started = time.time()
        timeout = int(os.environ.get(
            "GITBUG_DOCKER_DIRECT_TIMEOUT",
            str(max(self.timeout, 900) if self.timeout else 900),
        ))
        retry_notes: list[str] = []
        dependency_retries = max(1, int(os.environ.get("GITBUG_DOCKER_DEP_RETRIES", "3")))
        format_applied = False
        try:
            for attempt in range(dependency_retries):
                proc = subprocess.run(
                    docker_cmd,
                    cwd=workdir,
                    env=self._env(),
                    capture_output=True,
                    text=True,
                    timeout=timeout if timeout > 0 else None,
                )
                output = f"{proc.stdout or ''}\n{proc.stderr or ''}"
                command.returncode = proc.returncode
                command.stdout_tail = _tail(proc.stdout or "", 8000)
                command.stderr_tail = _tail(proc.stderr or "", 4000)
                if (
                    proc.returncode != 0
                    and not format_applied
                    and _looks_like_spring_javaformat_failure(output.lower())
                    and (workdir / "pom.xml").exists()
                ):
                    format_applied = True
                    format_cmd_text = "mvn -B --file pom.xml spring-javaformat:apply -DskipTests"
                    if java_home:
                        format_cmd_text = (
                            f'export JAVA_HOME="{java_home}"\n'
                            'export PATH="$JAVA_HOME/bin:$PATH"\n'
                            "java -version\n"
                            f"{format_cmd_text}"
                        )
                    format_cmd_text = (
                        "export LANG=C.UTF-8\n"
                        "export LC_ALL=C.UTF-8\n"
                        'export JAVA_TOOL_OPTIONS="${JAVA_TOOL_OPTIONS:-} -Dfile.encoding=UTF-8"\n'
                        'export MAVEN_OPTS="${MAVEN_OPTS:-} -Dfile.encoding=UTF-8"\n'
                        'export GRADLE_OPTS="${GRADLE_OPTS:-} -Dfile.encoding=UTF-8"\n'
                        "mkdir -p /tmp/.m2\n"
                        "cp /tmp/m2/settings.xml /tmp/.m2/settings.xml 2>/dev/null || true\n"
                        f"{format_cmd_text}"
                    )
                    format_docker_cmd = [
                        "docker",
                        "run",
                        "--rm",
                        "--network",
                        "host",
                        "--user",
                        user_spec,
                        "-e",
                        "HOME=/tmp",
                        "-e",
                        "LANG=C.UTF-8",
                        "-e",
                        "LC_ALL=C.UTF-8",
                        "-e",
                        "JAVA_TOOL_OPTIONS=-Dfile.encoding=UTF-8",
                        "-e",
                        "MAVEN_OPTS=-Dfile.encoding=UTF-8",
                        "-e",
                        "GRADLE_OPTS=-Dfile.encoding=UTF-8",
                        "-e",
                        "GRADLE_USER_HOME=/tmp/gradle",
                        *(
                            ["-e", f"JAVA_HOME={java_home}"]
                            if java_home
                            else []
                        ),
                        *java_mount_args,
                        "-v",
                        f"{maven_repo}:/tmp/m2",
                        "-v",
                        f"{gradle_home}:/tmp/gradle",
                        "-v",
                        f"{workdir}:/workspace",
                        "-w",
                        "/workspace",
                        docker_image,
                        "bash",
                        "-lc",
                        _with_maven_repo(format_cmd_text),
                    ]
                    format_proc = subprocess.run(
                        format_docker_cmd,
                        cwd=workdir,
                        env=self._env(),
                        capture_output=True,
                        text=True,
                        timeout=timeout if timeout > 0 else None,
                    )
                    retry_notes.append(
                        "spring-javaformat validation failed; "
                        f"spring-javaformat:apply returned {format_proc.returncode}"
                    )
                    if format_proc.returncode == 0:
                        proc = subprocess.run(
                            docker_cmd,
                            cwd=workdir,
                            env=self._env(),
                            capture_output=True,
                            text=True,
                            timeout=timeout if timeout > 0 else None,
                        )
                        output = f"{proc.stdout or ''}\n{proc.stderr or ''}"
                        command.returncode = proc.returncode
                        command.stdout_tail = _tail(proc.stdout or "", 8000)
                        command.stderr_tail = _tail(proc.stderr or "", 4000)
                if (
                    proc.returncode == 0
                    or attempt >= dependency_retries - 1
                    or not _looks_like_dependency_resolution_failure(output.lower())
                ):
                    break
                delay = min(60, 5 * (2 ** attempt))
                retry_notes.append(
                    f"dependency resolution failure on attempt {attempt + 1}/{dependency_retries}; "
                    f"retrying after {delay}s"
                )
                time.sleep(delay)
            if retry_notes:
                command.stderr_tail = _tail("\n".join(retry_notes) + "\n" + command.stderr_tail, 4000)
        except subprocess.TimeoutExpired as exc:
            command.error = f"timeout after {exc.timeout}s"
            command.stdout_tail = _tail((exc.stdout or "") if isinstance(exc.stdout, str) else "", 8000)
            command.stderr_tail = _tail((exc.stderr or "") if isinstance(exc.stderr, str) else "", 4000)
        except Exception as exc:
            command.error = str(exc)
        finally:
            command.duration_ms = int((time.time() - started) * 1000)
        return command

    def _default_cli(self) -> str:
        local = self.gitbug_repo / "gitbug-java"
        if local.exists():
            return str(local)
        return "gitbug-java"

    def _cli_path_exists(self) -> bool:
        cli_path = Path(self.cli)
        if cli_path.is_absolute() or os.sep in self.cli:
            return cli_path.exists()
        return shutil.which(self.cli) is not None

    def _run_cmd(self, workdir: Path) -> list[str]:
        cmd = [self.cli, "run", str(workdir)]
        if self.act_cache_dir is not None:
            cmd.append(f"--act_cache_dir={self.act_cache_dir}")
        if self.timeout:
            cmd.append(f"--timeout={self.timeout}")
        return cmd

    def _run(self, cmd: list[str]) -> CommandResult:
        command = CommandResult(cmd=cmd, cwd=str(self.gitbug_repo))
        if self.dry_run:
            return command

        started = time.time()
        process_timeout = int(os.environ.get(
            "GITBUG_OFFICIAL_PROCESS_TIMEOUT",
            str(min(max(self.timeout + 60, 300), 300)) if self.timeout else "300",
        ))
        try:
            proc = subprocess.run(
                cmd,
                cwd=self.gitbug_repo,
                env=self._env(),
                capture_output=True,
                text=True,
                timeout=process_timeout if process_timeout > 0 else None,
            )
            command.returncode = proc.returncode
            command.stdout_tail = _tail(proc.stdout or "")
            command.stderr_tail = _tail(proc.stderr or "")
        except subprocess.TimeoutExpired as exc:
            command.error = f"timeout after {exc.timeout}s"
            command.stdout_tail = _tail((exc.stdout or "") if isinstance(exc.stdout, str) else "")
            command.stderr_tail = _tail((exc.stderr or "") if isinstance(exc.stderr, str) else "")
        except Exception as exc:
            command.error = str(exc)
        finally:
            command.duration_ms = int((time.time() - started) * 1000)
        return command

    def _load_test_results(self, workdir: Path) -> dict[str, Any]:
        results = workdir / ".gitbug-java" / "test-results.json"
        if not results.exists():
            return {}
        with results.open(encoding="utf-8") as f:
            return json.load(f)

    def _env(self) -> dict[str, str]:
        env = os.environ.copy()
        venv_candidates = [
            env.get("GITBUG_JAVA_VENV", ""),
            str(self.gitbug_repo / ".venv" / "bin"),
            str(self.gitbug_repo.parent / "venv" / "bin"),
        ]
        path_parts = [
            *[path for path in venv_candidates if path],
            str(self.gitbug_repo),
            str(self.gitbug_repo / "bin"),
            env.get("PATH", ""),
        ]
        env["PATH"] = os.pathsep.join(path_parts)
        env["PYTHONPATH"] = os.pathsep.join(
            [str(self.gitbug_repo), env.get("PYTHONPATH", "")]
        )
        env.setdefault("DOCKER_API_VERSION", os.environ.get("DOCKER_API_VERSION", "1.44"))
        return env


def _strip_test_dirs(work_dir: Path) -> None:
    for test_dir in list(work_dir.rglob("src/test")):
        if test_dir.is_dir():
            shutil.rmtree(test_dir)


def _required_java_version(workdir: Path) -> str:
    workflow_version = _workflow_java_version(workdir)
    if workflow_version:
        return workflow_version
    return _pom_java_version(workdir / "pom.xml")


def _workflow_java_version(workdir: Path) -> str:
    for workflow in sorted((workdir / ".github" / "workflows").glob("*.y*ml")):
        try:
            text = workflow.read_text(encoding="utf-8")
        except Exception:
            continue
        match = re.search(r"(?im)^\s*java-version\s*:\s*['\"]?([^'\"\s]+)", text)
        if not match:
            continue
        version = _normalize_java_version(match.group(1))
        if version:
            return version
    return ""


def _pom_java_version(pom: Path) -> str:
    try:
        text = pom.read_text(encoding="utf-8")
    except Exception:
        return ""
    properties = dict(re.findall(r"<([^>/\s]+)>\s*([^<]+?)\s*</\1>", text))
    candidates = [
        properties.get("maven.compiler.release", ""),
        properties.get("maven.compiler.target", ""),
        properties.get("maven.compiler.source", ""),
        properties.get("java.version", ""),
    ]
    for candidate in candidates:
        resolved = _resolve_maven_property(candidate, properties)
        version = _normalize_java_version(resolved)
        if version:
            return version
    return ""


def _resolve_maven_property(value: str, properties: dict[str, str]) -> str:
    value = (value or "").strip()
    match = re.fullmatch(r"\$\{([^}]+)\}", value)
    if match:
        return properties.get(match.group(1), "")
    return value


def _normalize_java_version(value: str) -> str:
    value = (value or "").strip().strip("'\"")
    if not value or "${{" in value or "$(" in value:
        return ""
    match = re.search(r"(\d+)", value)
    if not match:
        return ""
    major = match.group(1)
    if major == "1":
        version_match = re.search(r"1\.(\d+)", value)
        if version_match:
            major = version_match.group(1)
    return major if major in {"8", "11", "17", "18", "19", "20", "21"} else ""


def _docker_java_home(java_version: str) -> str:
    if not java_version:
        return ""
    if java_version in {"18", "20"}:
        java_version = "21"
    return f"/usr/lib/jvm/temurin-{java_version}-jdk-amd64"


def _docker_java_mount_args(java_version: str) -> list[str]:
    if java_version != "19":
        return []
    host_jdk = Path(os.environ.get(
        "GITBUG_DOCKER_JDK19_HOME",
        "/data/output/tools/temurin-19-jdk-amd64",
    ))
    if not host_jdk.exists():
        return []
    return ["-v", f"{host_jdk}:/usr/lib/jvm/temurin-19-jdk-amd64:ro"]


def _workflow_command(workdir: Path) -> str:
    build_commands: list[str] = []
    for workflow in sorted((workdir / ".github" / "workflows").glob("*.y*ml")):
        commands = _extract_workflow_run_commands(workflow)
        for command in commands:
            lowered = command.lower()
            if "mvn " in lowered or lowered.startswith("mvn") or "gradle" in lowered:
                build_commands.append(command)
    for command in build_commands:
        if _is_workflow_test_command(command):
            return command
    # Setup-only workflow snippets such as `chmod +x gradlew` are not usable
    # verification commands. Fall back to the repository's direct test command.
    if (workdir / "pom.xml").exists():
        return "mvn -B --file pom.xml test"
    if (workdir / "gradlew").exists():
        return "./gradlew test"
    if (workdir / "build.gradle").exists() or (workdir / "build.gradle.kts").exists():
        return "gradle test"
    return "mvn -B --file pom.xml package"


def _is_workflow_test_command(command: str) -> bool:
    for raw_line in (command or "").splitlines() or [command]:
        try:
            parts = shlex.split(raw_line.strip())
        except ValueError:
            continue
        if not parts:
            continue
        tool = Path(parts[0]).name
        if tool in {"mvn", "mvnw"}:
            return any(part in {"test", "verify", "failsafe:integration-test"} for part in parts)
        if tool in {"gradle", "gradlew"} or tool.startswith("gradle"):
            return any(part in {"test", "check"} or part.startswith("test") for part in parts)
    return False


def _target_generated_test_command(
    command: str,
    *,
    failing_test_class: str | None,
    test_method_name: str | list[str] | None,
) -> str:
    """Prefer running only the injected method(s) during verification."""
    test_class = _outer_test_class_name((failing_test_class or "").strip())
    if isinstance(test_method_name, list):
        test_methods = [str(item).strip() for item in test_method_name if str(item).strip()]
    else:
        test_methods = [part.strip() for part in str(test_method_name or "").split(",") if part.strip()]
    if not test_class or not test_methods:
        return command

    maven_target = f"{test_class}#{'+'.join(test_methods)}"
    rewritten: list[str] = []
    changed = False
    for raw_line in command.splitlines() or [command]:
        line = raw_line.strip()
        prefix = raw_line[: len(raw_line) - len(raw_line.lstrip())]
        if not line:
            rewritten.append(raw_line)
            continue
        try:
            parts = shlex.split(line)
        except ValueError:
            rewritten.append(raw_line)
            continue
        if not parts:
            rewritten.append(raw_line)
            continue

        tool = Path(parts[0]).name
        if tool == "mvn" or tool == "mvnw":
            filtered = [
                part for part in parts
                if not part.startswith("-Dtest=")
                and part not in {"test", "verify", "package", "install", "check"}
            ]
            filtered.append(f"-Dtest={maven_target}")
            filtered.append("test")
            rewritten.append(prefix + shlex.join(filtered))
            changed = True
            continue

        if tool in {"gradle", "gradlew"} or tool.startswith("gradle"):
            filtered = []
            skip_next = False
            for part in parts:
                if skip_next:
                    skip_next = False
                    continue
                if part in {"check", "build"}:
                    continue
                if part == "--tests":
                    skip_next = True
                    continue
                if part.startswith("--tests="):
                    continue
                filtered.append(part)
            if "test" not in filtered:
                filtered.append("test")
            for method in test_methods:
                filtered.extend(["--tests", f"*{test_class}.{method}"])
            rewritten.append(prefix + shlex.join(filtered))
            changed = True
            continue

        rewritten.append(raw_line)

    return "\n".join(rewritten) if changed else command


def _outer_test_class_name(test_class: str) -> str:
    """Return the concrete source file class for nested JUnit display names."""
    return (test_class or "").split("$", 1)[0]


def _extract_workflow_run_commands(workflow: Path) -> list[str]:
    try:
        lines = workflow.read_text(encoding="utf-8").splitlines()
    except Exception:
        return []
    commands: list[str] = []
    idx = 0
    while idx < len(lines):
        line = lines[idx]
        stripped = line.strip()
        if stripped.startswith("run: |") or stripped.startswith("run: >"):
            indent = len(line) - len(line.lstrip())
            block: list[str] = []
            idx += 1
            while idx < len(lines):
                nested = lines[idx]
                nested_indent = len(nested) - len(nested.lstrip())
                if nested.strip() and nested_indent <= indent:
                    idx -= 1
                    break
                block.append(nested[indent + 2:] if len(nested) > indent + 2 else "")
                idx += 1
            command = "\n".join(part for part in block if part.strip()).strip()
            if command:
                commands.append(command)
        elif stripped.startswith("run:"):
            command = stripped.split("run:", 1)[1].strip().strip("'\"")
            if command:
                commands.append(command)
        idx += 1
    return commands


def _with_maven_repo(command: str) -> str:
    lines = command.splitlines() or [command]
    patched: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("mvn ") and "-Dmaven.repo.local=" not in stripped:
            prefix = line[: len(line) - len(line.lstrip())]
            patched.append(prefix + stripped.replace("mvn ", "mvn -Dmaven.repo.local=/tmp/m2 ", 1))
        else:
            patched.append(line)
    return "\n".join(patched)


def parse_surefire_results(project_path: Path) -> dict[str, Any]:
    report_paths: dict[str, Path] = {}
    for pattern in (
        "target/surefire-reports/TEST-*.xml",
        "target/failsafe-reports/TEST-*.xml",
        "build/test-results/**/TEST-*.xml",
    ):
        for report in project_path.rglob(pattern):
            report_paths[str(report.resolve(strict=False))] = report
    reports = sorted(report_paths.values())
    executed = 0
    skipped = 0
    failed_tests: list[dict[str, Any]] = []
    test_cases: list[dict[str, Any]] = []
    errors = 0
    for report in reports:
        try:
            root = ET.parse(report).getroot()
        except Exception:
            continue
        for suite in _iter_suites(root):
            executed += int(float(suite.attrib.get("tests", "0") or 0))
            skipped += int(float(suite.attrib.get("skipped", "0") or 0))
            errors += int(float(suite.attrib.get("errors", "0") or 0))
        for case in root.iter("testcase"):
            case_entry = {
                "classname": case.attrib.get("classname", ""),
                "name": case.attrib.get("name", ""),
            }
            test_cases.append(case_entry)
            failures = list(case.findall("failure")) + list(case.findall("error"))
            if not failures:
                continue
            failed_tests.append(
                {
                    "classname": case.attrib.get("classname", ""),
                    "name": case.attrib.get("name", ""),
                    "message": failures[0].attrib.get("message", "") if failures else "",
                    "type": failures[0].attrib.get("type", "") if failures else "",
                }
            )
    failing = len(failed_tests)
    return {
        "expected_tests": executed,
        "executed_tests": executed,
        "skipped_tests": skipped,
        "passing_tests": max(0, executed - failing - skipped),
        "failing_tests": failing,
        "errors": errors,
        "unexpected_tests": [],
        "missing_tests": [],
        "failed_tests": failed_tests,
        "test_cases": test_cases,
        "source": "surefire-reports",
    }


def _iter_suites(root: ET.Element) -> list[ET.Element]:
    if root.tag == "testsuite":
        return [root]
    return [suite for suite in root.iter("testsuite")]


def detect_existing_test_file(project_path: Path, failing_test_class: str) -> Path | None:
    test_classes = []
    raw = (failing_test_class or "").strip()
    if raw:
        test_classes.append(raw)
        outer = _outer_test_class_name(raw)
        if outer and outer != raw:
            test_classes.append(outer)
    for test_class in test_classes:
        rel = Path(*test_class.split(".")).with_suffix(".java")
        matches = list(project_path.rglob(str(Path("src/test/java") / rel)))
        if matches:
            return matches[0]
        for test_root in project_path.rglob("src/test"):
            if not test_root.is_dir():
                continue
            matches = list(test_root.rglob(str(rel)))
            if matches:
                return matches[0]
        for test_root in project_path.rglob("test"):
            if not test_root.is_dir():
                continue
            matches = list(test_root.rglob(str(rel)))
            if matches:
                return matches[0]
        simple = test_class.rsplit(".", 1)[-1] + ".java"
        candidates = list(project_path.rglob(simple))
        for candidate in candidates:
            if "src/test/java" in candidate.as_posix():
                return candidate
        for candidate in candidates:
            if f"{os.sep}src{os.sep}test{os.sep}" in candidate.as_posix() and candidate.suffix == ".java":
                return candidate
        for candidate in candidates:
            if f"{os.sep}test{os.sep}" in candidate.as_posix() and candidate.suffix == ".java":
                return candidate
    return None


def inject_test_method_into_existing_class(
    project_path: Path,
    test_method_code: str,
    test_method_name: str,
    failing_test_class: str,
) -> dict[str, Any]:
    test_file = detect_existing_test_file(project_path, failing_test_class)
    if test_file is None:
        return {
            "status": "error",
            "message": f"Cannot find existing test file for {failing_test_class}",
        }
    source = test_file.read_text(encoding="utf-8")
    method = _normalize_method_code(test_method_code, test_method_name)
    if not method:
        return {"status": "error", "message": "No test method code provided."}
    method = _avoid_ambiguous_fail(source, method)
    source = _remove_existing_method(source, test_method_name)
    insert_at = _find_last_top_level_brace(source)
    if insert_at < 0:
        return {"status": "error", "message": f"Cannot find class closing brace in {test_file}"}
    new_source = source[:insert_at] + "\n" + _indent_method(method) + "\n" + source[insert_at:]
    new_source = _ensure_test_import(new_source, method)
    test_file.write_text(new_source, encoding="utf-8")
    return {"status": "success", "test_file": str(test_file)}


def inject_generated_test_class_into_existing_class(
    project_path: Path,
    test_class_code: str,
    failing_test_class: str,
    preferred_names: list[str] | None = None,
) -> dict[str, Any]:
    """Inject all generated test methods from a class into an existing host class."""
    test_file = detect_existing_test_file(project_path, failing_test_class)
    if test_file is None:
        return {
            "status": "error",
            "message": f"Cannot find existing test file for {failing_test_class}",
        }
    source = test_file.read_text(encoding="utf-8", errors="replace")
    generated_imports = _extract_imports(test_class_code)
    parsed_methods = _extract_void_test_methods(test_class_code, require_test_annotation=True)
    if not parsed_methods:
        return {"status": "error", "message": "No test methods found in generated class."}

    existing_names = _extract_existing_method_names(source)
    used_names = set(existing_names)
    method_blocks: list[str] = []
    method_names: list[str] = []
    preferred_names = preferred_names or []
    for idx, (name, method) in enumerate(parsed_methods, 1):
        preferred = preferred_names[idx - 1] if idx - 1 < len(preferred_names) else ""
        new_name = _unique_generated_method_name(preferred or name or f"generatedTest{idx}", used_names)
        used_names.add(new_name)
        method = _normalize_method_code(method, new_name)
        if not method:
            continue
        method = _avoid_ambiguous_fail(source, method)
        method = _qualify_unqualified_junit_assertions_when_assertj_host(source, method)
        method_blocks.append(method)
        method_names.append(new_name)

    if not method_blocks:
        return {"status": "error", "message": "No injectable test methods remained after normalization."}

    stripped = source.rstrip()
    insert_at = _find_generated_method_insertion_point(stripped)
    if insert_at < 0:
        return {"status": "error", "message": f"Cannot find class closing brace in {test_file}"}
    method_blocks, generated_imports = _qualify_conflicting_generated_imports(source, generated_imports, method_blocks)
    support_members = _support_members_for_generated_methods(source, test_class_code, method_blocks)
    new_members_text = "\n".join([*method_blocks, *support_members])
    generated_imports.extend(_same_package_imports_for_generated_types(project_path, source, test_class_code, new_members_text))
    generated_imports.extend(_unique_project_imports_for_generated_types(project_path, source, generated_imports, new_members_text))
    generated_imports = _filter_generated_imports(source, generated_imports, new_members_text)
    prefix_support = [member for member in support_members if not _looks_like_type_member(member)]
    suffix_support = [member for member in support_members if _looks_like_type_member(member)]
    prefix_support_block = ("\n" + "\n".join(_indent_method(member) for member in prefix_support) + "\n") if prefix_support else ""
    suffix_support_block = ("\n" + "\n".join(_indent_method(member) for member in suffix_support) + "\n") if suffix_support else ""
    block = "\n\n".join(_indent_method(method) for method in method_blocks)
    new_source = stripped[:insert_at] + prefix_support_block + "\n" + block + suffix_support_block + "\n" + stripped[insert_at:]
    for imp in generated_imports:
        new_source = _add_import_if_needed(new_source, imp)
    for method in method_blocks:
        new_source = _ensure_test_import(new_source, method)
    if not new_source.endswith("\n"):
        new_source += "\n"
    test_file.write_text(new_source, encoding="utf-8")
    return {
        "status": "success",
        "test_file": str(test_file),
        "test_method_names": method_names,
        "import_count": len(generated_imports),
        "support_members": support_members,
    }


def evaluate_generated_suite_run(
    results: dict[str, Any],
    command: CommandResult,
    test_method_names: list[str],
) -> dict[str, Any]:
    """Classify a run that targeted several generated methods."""
    stdout_stderr = f"{command.stdout_tail}\n{command.stderr_tail}"
    if command.error:
        return {
            "status": "infra_error",
            "compile_ok": False,
            "passed": False,
            "message": command.error,
        }
    lower = stdout_stderr.lower()
    if command.returncode not in (0, None) and _looks_like_generated_compile_or_lint_failure(lower):
        return {
            "status": "compile_fail",
            "compile_ok": False,
            "passed": False,
            "message": _extract_compile_failure_message(stdout_stderr),
        }

    wanted = [str(name) for name in test_method_names if str(name)]
    failed_tests = results.get("failed_tests") or []
    generated_failures = [
        item for item in failed_tests
        if any(_matches_generated_method(str(item.get("name", "")), name) for name in wanted)
    ]
    if generated_failures:
        return {
            "status": "test_failed",
            "compile_ok": True,
            "passed": False,
            "message": f"Generated test method(s) failed: {generated_failures}",
            "failed_tests": generated_failures,
        }

    observed_names = {
        str(item.get("name", ""))
        for item in (results.get("test_cases") or [])
    }
    observed_generated = [
        name for name in wanted
        if any(_matches_generated_method(observed, name) for observed in observed_names)
    ]
    if not observed_generated:
        if command.returncode not in (0, None):
            if _looks_like_dependency_resolution_failure(lower):
                return {
                    "status": "infra_error",
                    "compile_ok": False,
                    "passed": False,
                    "message": _extract_infra_failure_message(stdout_stderr),
                }
            if _looks_like_test_execution_failure(lower):
                return {
                    "status": "test_failed",
                    "compile_ok": True,
                    "passed": False,
                    "message": _tail(stdout_stderr, 2500),
                    "failed_tests": failed_tests,
                }
            return {
                "status": "compile_fail",
                "compile_ok": False,
                "passed": False,
                "message": _extract_compile_failure_message(stdout_stderr),
            }
        return {
            "status": "infra_error",
            "compile_ok": True,
            "passed": False,
            "message": (
                "Generated test methods were not observed in any Surefire/Gradle report. "
                "Do not treat this as PASS."
            ),
        }

    if command.returncode not in (0, None):
        if failed_tests:
            return {
                "status": "test_passed",
                "compile_ok": True,
                "passed": True,
                "message": (
                    "Generated methods did not fail, although other tests failed. "
                    f"observed_generated={observed_generated}, "
                    f"executed_tests={results.get('executed_tests')}, "
                    f"failing_tests={results.get('failing_tests')}"
                ),
                "other_failed_tests": failed_tests[:10],
            }
        return {
            "status": "test_failed",
            "compile_ok": True,
            "passed": False,
            "message": _tail(stdout_stderr, 2500),
            "failed_tests": failed_tests,
        }

    return {
        "status": "test_passed",
        "compile_ok": True,
        "passed": True,
        "message": (
            f"Generated methods did not fail. observed_generated={observed_generated}, "
            f"executed_tests={results.get('executed_tests')}, "
            f"failing_tests={results.get('failing_tests')}"
        ),
    }


def evaluate_generated_method_run(
    results: dict[str, Any],
    command: CommandResult,
    test_method_name: str,
) -> dict[str, Any]:
    stdout_stderr = f"{command.stdout_tail}\n{command.stderr_tail}"
    if command.error:
        return {
            "status": "infra_error",
            "compile_ok": False,
            "passed": False,
            "message": command.error,
        }
    lower = stdout_stderr.lower()
    if command.returncode not in (0, None) and _looks_like_generated_compile_or_lint_failure(lower):
        return {
            "status": "compile_fail",
            "compile_ok": False,
            "passed": False,
            "message": _extract_compile_failure_message(stdout_stderr),
        }
    failed_tests = results.get("failed_tests") or []
    executed = int(results.get("executed_tests") or 0)
    if executed == 0:
        if command.returncode not in (0, None):
            if _looks_like_dependency_resolution_failure(lower):
                return {
                    "status": "infra_error",
                    "compile_ok": False,
                    "passed": False,
                    "message": _extract_infra_failure_message(stdout_stderr),
                }
            if _looks_like_test_execution_failure(lower):
                return {
                    "status": "test_failed",
                    "compile_ok": True,
                    "passed": False,
                    "message": _tail(stdout_stderr, 2500),
                    "failed_tests": failed_tests,
                }
            return {
                "status": "compile_fail",
                "compile_ok": False,
                "passed": False,
                "message": _extract_compile_failure_message(stdout_stderr),
            }
        return {
            "status": "infra_error",
            "compile_ok": True,
            "passed": False,
            "message": (
                "Generated test method was not observed in any test report. "
                "No tests were parsed from Surefire/Gradle reports; do not treat this as PASS."
            ),
        }
    generated_failures = [
        item for item in failed_tests
        if _matches_generated_method(str(item.get("name", "")), test_method_name)
    ]
    if generated_failures:
        return {
            "status": "test_failed",
            "compile_ok": True,
            "passed": False,
            "message": f"Generated test method failed: {generated_failures}",
            "failed_tests": generated_failures,
        }
    if command.returncode not in (0, None):
        if failed_tests:
            return {
                "status": "test_passed",
                "compile_ok": True,
                "passed": True,
                "message": (
                    "Generated test method did not fail, although other tests failed. "
                    f"executed_tests={results.get('executed_tests')}, "
                    f"failing_tests={results.get('failing_tests')}"
                ),
                "other_failed_tests": failed_tests[:10],
            }
        return {
            "status": "test_failed",
            "compile_ok": True,
            "passed": False,
            "message": _tail(stdout_stderr, 2500),
            "failed_tests": failed_tests,
        }
    return {
        "status": "test_passed",
        "compile_ok": True,
        "passed": True,
        "message": (
            f"Generated test method did not fail. "
            f"executed_tests={results.get('executed_tests')}, "
            f"failing_tests={results.get('failing_tests')}"
        ),
    }


def _matches_generated_method(observed: str, test_method_name: str) -> bool:
    return (
        observed == test_method_name
        or observed.startswith(f"{test_method_name}(")
        or observed.startswith(f"{test_method_name}[")
    )


def _extract_compile_failure_message(output: str) -> str:
    text = output or ""
    patterns = [
        "COMPILATION ERROR",
        "compileTestJava FAILED",
        "Compilation failed",
        "Compilation failure",
        "BUILD FAILURE",
        "cannot find symbol",
        "package org.junit",
        "unmappable character",
        "unclosed string literal",
        "illegal combination of modifiers",
        "repeated modifier",
        "reference to",
        "Formatting violations",
        "Unused import",
        "Checkstyle",
    ]
    positions = [text.lower().find(pattern.lower()) for pattern in patterns]
    positions = [pos for pos in positions if pos >= 0]
    if not positions:
        return _tail(text, 2500)
    start = max(0, min(positions) - 800)
    return text[start:start + 3500]


def _extract_infra_failure_message(output: str) -> str:
    text = output or ""
    patterns = [
        "Could not resolve",
        "Could not transfer",
        "Received status code 429",
        "status: 429",
        "Too Many Requests",
        "PluginResolutionException",
        "DependencyResolutionException",
    ]
    positions = [text.lower().find(pattern.lower()) for pattern in patterns]
    positions = [pos for pos in positions if pos >= 0]
    if not positions:
        return _tail(text, 2500)
    start = max(0, min(positions) - 800)
    return text[start:start + 3500]


def _looks_like_dependency_resolution_failure(lower_output: str) -> bool:
    return any(
        marker in lower_output
        for marker in (
            "status: 429",
            "too many requests",
            "could not transfer artifact",
            "could not resolve all files for configuration",
            "pluginresolutionexception",
            "dependencyresolutionexception",
        )
    )


def _looks_like_generated_compile_or_lint_failure(lower_output: str) -> bool:
    markers = (
        "compilation failure",
        "compilation error",
        "compilation failed",
        "compiletestjava failed",
        "cannot find symbol",
        "package org.junit.jupiter",
        "package org.junit does not exist",
        "failed to execute goal org.apache.maven.plugins:maven-compiler-plugin",
        "unmappable character",
        "unclosed string literal",
        "illegal combination of modifiers",
        "repeated modifier",
        "reference to fail is ambiguous",
        "reference to element is ambiguous",
        "reference to document is ambiguous",
        " is never thrown in body of corresponding try statement",
        "unused import",
        "redundant import",
        "formatting violations",
    )
    return any(marker in lower_output for marker in markers)


def _looks_like_spring_javaformat_failure(lower_output: str) -> bool:
    return (
        "spring-javaformat" in lower_output
        and "formatting violations" in lower_output
    )


def _looks_like_test_execution_failure(lower_output: str) -> bool:
    markers = (
        " task :test failed",
        "> task :test failed",
        "maven-surefire-plugin",
        "there are test failures",
        "tests run:",
        "junitplatformprovider",
        "surefire-reports",
    )
    return any(marker in lower_output for marker in markers)


def _extract_imports(source: str) -> list[str]:
    imports: list[str] = []
    for line in (source or "").splitlines():
        match = re.match(r"\s*import\s+([^;]+);\s*$", line)
        if match:
            imports.append(match.group(1).strip())
    return imports


def _extract_void_test_methods(source: str, *, require_test_annotation: bool = False) -> list[tuple[str, str]]:
    """Extract top-level-ish void test method blocks from a Java class/method blob."""
    text = source or ""
    fence = re.search(r"```(?:java)?\s*([\s\S]*?)```", text, re.IGNORECASE)
    if fence:
        text = fence.group(1)
    allowed_depth = 1 if re.search(r"\bclass\s+\w+", text) else 0
    header = re.compile(
        r"(?P<annotations>(?:@[\w.]+(?:\([^)]*\))?\s*)*)"
        r"(?:public|protected|private)?\s*"
        r"(?:static\s+)?"
        r"void\s+(\w+)\s*\([^)]*\)\s*(?:throws\s+[\w.,\s]+)?\s*\{",
        re.DOTALL,
    )
    out: list[tuple[str, str]] = []
    for match in header.finditer(text):
        if text[:match.start()].count("{") - text[:match.start()].count("}") != allowed_depth:
            continue
        if require_test_annotation and not re.search(r"@(?:[\w.]+\.)?Test\b", match.group("annotations") or ""):
            continue
        brace = text.find("{", match.end() - 1)
        end = _find_matching_brace(text, brace)
        if end is not None and end > match.start():
            out.append((match.group(2), text[match.start():end].strip()))
    return out


def _extract_existing_method_names(source: str) -> set[str]:
    names: set[str] = set()
    for name, _method in _extract_void_test_methods(source):
        names.add(name)
    return names


def _unique_generated_method_name(base: str, used_names: set[str]) -> str:
    clean = re.sub(r"\W+", "_", base or "generatedTest").strip("_") or "generatedTest"
    if clean[0].isdigit():
        clean = f"test_{clean}"
    if clean not in used_names:
        return clean
    candidate = f"{clean}_generated"
    suffix = 2
    while candidate in used_names:
        candidate = f"{clean}_generated{suffix}"
        suffix += 1
    return candidate


def _support_members_for_generated_methods(
    host_source: str,
    generated_source: str,
    method_blocks: list[str],
) -> list[str]:
    members: list[str] = []
    methods_text = "\n".join(method_blocks)
    if (
        re.search(r"\bthrown\s*\.", methods_text)
        and "ExpectedException thrown" in generated_source
        and not re.search(r"\bExpectedException\s+thrown\s*[=;]", host_source)
    ):
        members.append(
            "@Rule\n"
            "public ExpectedException thrown = ExpectedException.none();"
        )
    for name, member in _extract_nested_type_members(generated_source):
        if not re.search(rf"\b{re.escape(name)}\b", methods_text):
            continue
        if re.search(rf"\b(?:class|interface|enum|record)\s+{re.escape(name)}\b", host_source):
            continue
        members.append(member)
    return members


def _looks_like_type_member(member: str) -> bool:
    return bool(re.search(r"\b(?:class|interface|enum|record)\s+\w+\b", member or ""))


def _extract_nested_type_members(source: str) -> list[tuple[str, str]]:
    text = source or ""
    fence = re.search(r"```(?:java)?\s*([\s\S]*?)```", text, re.IGNORECASE)
    if fence:
        text = fence.group(1)
    allowed_depth = 1 if re.search(r"\bclass\s+\w+", text) else 0
    header = re.compile(
        r"(?P<annotations>(?:@[\w.]+(?:\([^)]*\))?\s*)*)"
        r"(?:public|protected|private)?\s*"
        r"(?:static\s+)?"
        r"(?:final\s+|abstract\s+)?"
        r"(?:class|interface|enum|record)\s+(\w+)[^{]*\{",
        re.DOTALL,
    )
    out: list[tuple[str, str]] = []
    for match in header.finditer(text):
        if text[:match.start()].count("{") - text[:match.start()].count("}") != allowed_depth:
            continue
        brace = text.find("{", match.end() - 1)
        end = _find_matching_brace(text, brace)
        if end is not None and end > match.start():
            out.append((match.group(2), text[match.start():end].strip()))
    return out


def _same_package_imports_for_generated_types(
    project_path: Path,
    host_source: str,
    generated_source: str,
    new_members: str,
) -> list[str]:
    generated_pkg = _host_package(generated_source)
    host_pkg = _host_package(host_source)
    if not generated_pkg or generated_pkg == host_pkg:
        return []
    imports: list[str] = []
    common = {
        "After",
        "AfterEach",
        "Assert",
        "Assertions",
        "Before",
        "BeforeEach",
        "Class",
        "Exception",
        "IOException",
        "Instant",
        "List",
        "Map",
        "Optional",
        "String",
        "StringWriter",
        "Test",
    }
    for simple in sorted(set(re.findall(r"\b[A-Z][A-Za-z0-9_]*\b", new_members or ""))):
        if simple in common:
            continue
        fqcn = f"{generated_pkg}.{simple}"
        rel = Path(*fqcn.split(".")).with_suffix(".java")
        if list(project_path.rglob(str(rel))):
            imports.append(fqcn)
    return imports


def _unique_project_imports_for_generated_types(
    project_path: Path,
    host_source: str,
    generated_imports: list[str],
    new_members: str,
) -> list[str]:
    host_pkg = _host_package(host_source)
    known = _non_static_imports_by_simple_name(host_source)
    for target in generated_imports:
        clean = target.strip().rstrip(";")
        if clean.startswith("static ") or clean.endswith(".*") or "." not in clean:
            continue
        known[clean.rsplit(".", 1)[-1]] = clean
    imports: list[str] = []
    common = {
        "After",
        "AfterEach",
        "Assert",
        "Assertions",
        "Before",
        "BeforeEach",
        "Class",
        "Exception",
        "IOException",
        "Instant",
        "List",
        "Map",
        "Optional",
        "String",
        "StringWriter",
        "Test",
    }
    for simple in sorted(set(re.findall(r"\b[A-Z][A-Za-z0-9_]*\b", new_members or ""))):
        if simple in common or simple in known:
            continue
        matches = [
            path for path in project_path.rglob(f"{simple}.java")
            if _fqcn_from_java_path(path)
        ]
        fqcns = sorted({_fqcn_from_java_path(path) for path in matches if _fqcn_from_java_path(path)})
        if len(fqcns) != 1:
            continue
        fqcn = fqcns[0]
        package = fqcn.rsplit(".", 1)[0] if "." in fqcn else ""
        if package and package != host_pkg:
            imports.append(fqcn)
    return imports


def _fqcn_from_java_path(path: Path) -> str:
    parts = list(path.with_suffix("").parts)
    markers = [
        ("src", "main", "java"),
        ("src", "test", "java"),
        ("main", "java"),
        ("test", "java"),
        ("test",),
    ]
    for marker in markers:
        n = len(marker)
        for idx in range(0, len(parts) - n + 1):
            if tuple(parts[idx: idx + n]) == marker:
                rel = parts[idx + n:]
                if rel:
                    return ".".join(rel)
    return ""


def _host_package(source: str) -> str:
    match = re.search(r"(?m)^\s*package\s+([\w.]+)\s*;\s*$", source or "")
    return match.group(1) if match else ""


def _non_static_imports_by_simple_name(source: str) -> dict[str, str]:
    imports: dict[str, str] = {}
    for target in _extract_imports(source):
        if target.startswith("static ") or target.endswith(".*"):
            continue
        imports[target.rsplit(".", 1)[-1]] = target
    return imports


def _assertj_static_present(source: str) -> bool:
    return bool(re.search(r"(?m)^\s*import\s+static\s+org\.assertj\.core\.api\.Assertions\.(?:\*|\w+)\s*;", source or ""))


def _avoid_ambiguous_fail(host_source: str, method: str) -> str:
    if not _assertj_static_present(host_source):
        return method
    if not re.search(r"(?<![\w.])fail\s*\(", method):
        return method
    if "import org.junit.jupiter.api.Test;" in host_source or "@org.junit.jupiter.api.Test" in method:
        return re.sub(r"(?<![\w.])fail\s*\(", "org.junit.jupiter.api.Assertions.fail(", method)
    return re.sub(r"(?<![\w.])fail\s*\(", "org.junit.Assert.fail(", method)


def _qualify_unqualified_junit_assertions_when_assertj_host(host_source: str, method: str) -> str:
    if not _assertj_static_present(host_source):
        return method
    if "import org.junit.jupiter.api.Test;" in host_source or "@org.junit.jupiter.api.Test" in method:
        owner = "org.junit.jupiter.api.Assertions"
    else:
        owner = "org.junit.Assert"
    names = [
        "assertEquals",
        "assertTrue",
        "assertFalse",
        "assertNull",
        "assertNotNull",
        "assertSame",
        "assertNotSame",
        "assertArrayEquals",
        "assertThrows",
    ]
    for name in names:
        method = re.sub(rf"(?<![\w.]){name}\s*\(", f"{owner}.{name}(", method)
    return method


def _qualify_conflicting_generated_imports(
    host_source: str,
    generated_imports: list[str],
    method_blocks: list[str],
) -> tuple[list[str], list[str]]:
    existing = _non_static_imports_by_simple_name(host_source)
    rewritten = list(method_blocks)
    kept_imports: list[str] = []
    for target in generated_imports:
        clean = target.strip().rstrip(";")
        if clean.startswith("static ") or clean.endswith(".*"):
            kept_imports.append(target)
            continue
        simple = clean.rsplit(".", 1)[-1]
        if simple in existing and existing[simple] != clean:
            rewritten = [re.sub(rf"\b{re.escape(simple)}\b", clean, block) for block in rewritten]
            continue
        kept_imports.append(target)
    return rewritten, kept_imports


def _filter_generated_imports(host_source: str, generated_imports: list[str], new_members: str) -> list[str]:
    host_pkg = _host_package(host_source)
    existing = _non_static_imports_by_simple_name(host_source)
    filtered: list[str] = []
    for target in generated_imports:
        clean = target.strip().rstrip(";")
        if not clean:
            continue
        if clean.startswith("static "):
            if clean.endswith(".*"):
                continue
            simple = clean.rsplit(".", 1)[-1]
            if not re.search(rf"\b{re.escape(simple)}\b", new_members):
                continue
            filtered.append(clean)
            continue
        if clean.endswith(".*"):
            # Wildcard imports are the common source of checkstyle failures and
            # simple-name ambiguity in host test classes. Keep existing host
            # imports; avoid copying generated wildcards into the host class.
            continue
        simple = clean.rsplit(".", 1)[-1]
        package = clean.rsplit(".", 1)[0] if "." in clean else ""
        if package == host_pkg:
            continue
        if simple in existing and existing[simple] != clean:
            continue
        if not re.search(rf"\b{re.escape(simple)}\b", new_members):
            continue
        filtered.append(clean)
    return filtered


def _add_import_if_needed(source: str, import_target: str) -> str:
    target = (import_target or "").strip().rstrip(";")
    if not target:
        return source
    if not target.startswith("static ") and target.endswith(".*"):
        return source
    if (
        target in {"static org.junit.jupiter.api.Assertions.*", "static org.junit.Assert.*"}
        and _assertj_static_present(source)
    ):
        return source
    if not target.startswith("static ") and not target.endswith(".*"):
        simple = target.rsplit(".", 1)[-1]
        existing = _non_static_imports_by_simple_name(source)
        if simple in existing and existing[simple] != target:
            return source
    line = f"import {target};"
    if line in source:
        return source
    # Avoid copying imports for the generated test class itself.
    if re.search(r"\bclass\s+" + re.escape(target.rsplit(".", 1)[-1]) + r"\b", source):
        return source
    last_import = source.rfind("import ")
    if last_import >= 0:
        end = source.find("\n", last_import)
        if end >= 0:
            return source[: end + 1] + line + "\n" + source[end + 1 :]
    pkg = re.search(r"(?m)^\s*package\s+[\w.]+\s*;\s*$", source)
    if pkg:
        return source[: pkg.end()] + "\n" + line + "\n" + source[pkg.end():]
    return line + "\n" + source


def _normalize_method_code(code: str, expected_name: str) -> str:
    source = (code or "").strip()
    fence = re.search(r"```(?:java)?\s*([\s\S]*?)```", source, re.IGNORECASE)
    if fence:
        source = fence.group(1).strip()
    if not source:
        return ""
    if not re.search(r"@(?:[\w.]+\.)?Test\b", source):
        source = "@Test\n" + source
    if not re.search(r"\bpublic\s+void\s+", source):
        source = re.sub(
            r"\b(?:public|protected|private)?\s*(?:static\s+)?void\s+",
            "public void ",
            source,
            count=1,
        )
    if expected_name:
        source = re.sub(
            r"(?m)^(\s*(?:@[\w.]+(?:\([^)]*\))?[ \t]*(?:\n\s*|[ \t]+))*"
            r"(?:public|protected|private)?\s*(?:static\s+)?(?:final\s+)?[\w<>,\[\].\s]+\s+)"
            r"\w+(\s*\()",
            rf"\1{expected_name}\2",
            source,
            count=1,
        )
    return source


def _indent_method(method: str) -> str:
    return "\n".join(("    " + line if line.strip() and not line.startswith("    ") else line) for line in method.splitlines())


def _ensure_test_import(source: str, method: str) -> str:
    inserts: list[str] = []
    has_jupiter_test = "import org.junit.jupiter.api.Test;" in source
    has_junit4_test = "import org.junit.Test;" in source
    has_jupiter_assertions = (
        "import static org.junit.jupiter.api.Assertions.*;" in source
        or "import org.junit.jupiter.api.Assertions" in source
        or "org.junit.jupiter.api.Assertions." in method
    )
    has_junit4_assertions = (
        "import static org.junit.Assert.*;" in source
        or "import org.junit.Assert" in source
        or "org.junit.Assert." in method
    )
    if "@Test" in method and not has_junit4_test and not has_jupiter_test:
        inserts.append("import org.junit.Test;")
    assertion_names = _unqualified_assertions_used(method)
    if assertion_names:
        if has_jupiter_test and not has_jupiter_assertions:
            if _assertj_static_present(source):
                inserts.extend(f"import static org.junit.jupiter.api.Assertions.{name};" for name in assertion_names if name != "fail")
            else:
                inserts.append("import static org.junit.jupiter.api.Assertions.*;")
        elif not has_jupiter_test and not has_junit4_assertions:
            if _assertj_static_present(source):
                inserts.extend(f"import static org.junit.Assert.{name};" for name in assertion_names if name != "fail")
            else:
                inserts.append("import static org.junit.Assert.*;")
    if (
        re.search(r"(?<![\w.])assertThat\s*\(", method or "")
        and "import static org.hamcrest.MatcherAssert.assertThat;" not in source
        and "import static org.hamcrest.MatcherAssert.*;" not in source
        and "import static org.junit.Assert.*;" not in source
        and "import static org.junit.Assert.assertThat;" not in source
        and not _assertj_static_present(source)
    ):
        inserts.append("import static org.hamcrest.MatcherAssert.assertThat;")
    inserts.extend(f"import static org.hamcrest.Matchers.{name};" for name in _unqualified_hamcrest_matchers_used(method))
    inserts = [item for idx, item in enumerate(inserts) if item not in inserts[:idx] and item not in source]
    if not inserts:
        return source
    insert_text = "\n".join(inserts) + "\n"
    last_import = source.rfind("import ")
    if last_import >= 0:
        end = source.find("\n", last_import)
        if end >= 0:
            return source[: end + 1] + insert_text + source[end + 1 :]
    pkg = re.search(r"(?m)^\s*package\s+[\w.]+\s*;\s*$", source)
    if pkg:
        return source[: pkg.end()] + "\n" + insert_text + source[pkg.end():]
    return insert_text + source


def _unqualified_assertions_used(method: str) -> list[str]:
    names = [
        "fail",
        "assertEquals",
        "assertTrue",
        "assertFalse",
        "assertNull",
        "assertNotNull",
        "assertSame",
        "assertNotSame",
        "assertArrayEquals",
        "assertThrows",
    ]
    return [name for name in names if re.search(rf"(?<![\w.]){name}\s*\(", method or "")]


def _unqualified_hamcrest_matchers_used(method: str) -> list[str]:
    names = [
        "allOf",
        "any",
        "anyOf",
        "anything",
        "both",
        "contains",
        "containsInAnyOrder",
        "containsString",
        "either",
        "empty",
        "emptyArray",
        "emptyCollectionOf",
        "emptyIterable",
        "emptyIterableOf",
        "equalTo",
        "greaterThan",
        "greaterThanOrEqualTo",
        "hasEntry",
        "hasItem",
        "hasItems",
        "hasKey",
        "hasSize",
        "hasToString",
        "hasValue",
        "instanceOf",
        "is",
        "lessThan",
        "lessThanOrEqualTo",
        "not",
        "notNullValue",
        "nullValue",
        "sameInstance",
        "startsWith",
    ]
    source = method or ""
    return [name for name in names if re.search(rf"(?<![\w.]){name}\s*\(", source)]


def _remove_existing_method(source: str, method_name: str) -> str:
    if not method_name:
        return source
    match = re.search(rf"(?m)^\s*(?:@[\w.]+(?:\([^)]*\))?[ \t]*(?:\n\s*|[ \t]+))*.*\b{re.escape(method_name)}\s*\([^)]*\)\s*\{{", source)
    if not match:
        return source
    brace = source.find("{", match.start())
    end = _find_matching_brace(source, brace)
    if end is None:
        return source
    return source[: match.start()] + source[end:]


def _find_last_top_level_brace(source: str) -> int:
    return source.rfind("}")


def _find_generated_method_insertion_point(source: str) -> int:
    inner = _find_first_top_level_inner_type(source)
    if inner >= 0:
        return inner
    return _find_last_top_level_brace(source)


def _find_first_top_level_inner_type(source: str) -> int:
    depth = 0
    line_depth = 0
    line_start = 0
    idx = 0
    while idx < len(source):
        ch = source[idx]
        if ch == "\n":
            line = source[line_start:idx]
            if _is_top_level_inner_type_line(line, line_depth):
                return _backtrack_annotations(source, line_start)
            line_start = idx + 1
            line_depth = depth
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth = max(0, depth - 1)
        idx += 1
    if _is_top_level_inner_type_line(source[line_start:], line_depth):
        return _backtrack_annotations(source, line_start)
    return -1


def _is_top_level_inner_type_line(line: str, depth: int) -> bool:
    return depth == 1 and bool(
        re.match(
            r"\s*(?:public|protected|private|static|final|abstract|\s)*"
            r"(?:class|interface|enum|record)\s+\w+\b",
            line,
        )
    )


def _backtrack_annotations(source: str, line_start: int) -> int:
    pos = line_start
    while pos > 0:
        prev_end = pos - 1
        prev_start = source.rfind("\n", 0, prev_end) + 1
        prev_line = source[prev_start:prev_end].strip()
        if not prev_line.startswith("@"):
            break
        pos = prev_start
    return pos


def _find_matching_brace(source: str, start: int) -> int | None:
    depth = 0
    for idx in range(start, len(source)):
        if source[idx] == "{":
            depth += 1
        elif source[idx] == "}":
            depth -= 1
            if depth == 0:
                return idx + 1
    return None

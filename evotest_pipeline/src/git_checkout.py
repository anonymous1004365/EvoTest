"""
General Git utilities used by dataset collectors.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Iterator


def git_checkout_branch(repo_path: Path, branch: str, remote: str = "origin") -> bool:
    """Fetch and check out a remote branch.

    Args:
        branch: Full branch ref like "origin/bugs-dot-jar_ACCUMULO-1044_9396979b"
               or just "bugs-dot-jar_ACCUMULO-1044_9396979b"
    """
    # Extract branch name after remote/ prefix if present
    if branch.startswith(f"{remote}/"):
        branch_name = branch[len(f"{remote}/"):]
    else:
        branch_name = branch

    # Fetch the branch to a local remote-tracking ref
    subprocess.run(
        ["git", "fetch", remote, f"refs/heads/{branch_name}:refs/remotes/{remote}/{branch_name}"],
        cwd=repo_path,
        capture_output=True,
    )
    # Checkout
    result = subprocess.run(
        ["git", "checkout", "-B", branch_name.split("/")[-1], f"{remote}/{branch_name}"],
        cwd=repo_path,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def git_show(repo_path: Path, commitish: str, file_path: str) -> str:
    """
    Return the content of a file at a specific commit.

    If the commit is missing locally, fetch it from origin for shallow clones.
    Returns "" if file not found at that path/commit.
    """
    # First try direct show
    result = subprocess.run(
        ["git", "show", f"{commitish}:{file_path}"],
        cwd=repo_path,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        return result.stdout

    # If failed, check if it's a "commit not found" error (shallow clone)
    # Try to fetch this specific commit from remote
    stderr = result.stderr.lower()
    if "bad object" in stderr or "not found" in stderr or "does not exist" in stderr:
        fetch_result = subprocess.run(
            ["git", "fetch", "origin", commitish],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=60,
        )
        if fetch_result.returncode == 0:
            # Retry show after fetch
            result = subprocess.run(
                ["git", "show", f"{commitish}:{file_path}"],
                cwd=repo_path,
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                return result.stdout

    # File doesn't exist at this path/commit, or commit unreachable
    return ""


def git_log_search(repo_path: Path, pattern: str, max_count: int = 50) -> str | None:
    """
    Search git log for a commit SHA matching the given pattern.
    Return the first matching full SHA.

    Note: git log --format + -n doesn't work reliably in Python subprocess,
    so we get all commits and search in Python instead.
    """
    result = subprocess.run(
        ["git", "log", "--format=%H %s"],
        cwd=repo_path,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    count = 0
    for line in result.stdout.strip().splitlines():
        if pattern in line:
            return line.split()[0]
        count += 1
        if count >= max_count:
            break
    return None


def extract_focal_file_from_diff(diff: str) -> str:
    """Extract the changed source file path from a unified diff, preferring the first src/main Java file."""
    if not diff:
        return ""
    # Find the first src/main/java Java file.
    matches = re.findall(
        r"^\+\+\+ b/(.+?\.java)$", diff, re.MULTILINE
    )
    for m in matches:
        if "src/main/java" in m or m.startswith("src/"):
            return m
    # Fallback: first Java file.
    for m in matches:
        return m
    return ""


def extract_focal_method_code(file_content: str, method_signature: str) -> str:
    """
    Extract the target method code, including Javadoc, from a complete Java class file.

    Args:
        file_content: complete Java class file content
        method_signature: method signature, such as "public void add(String key, Object value)"
                       or only a method name, such as "add"

    Returns:
        Only the target method code, including Javadoc and method body.
        Return "" when the method cannot be found.
    """
    _, code = extract_focal_method_info(file_content, method_signature)
    return code


def extract_focal_method_info(file_content: str, method_signature: str) -> tuple[str, str]:
    """
    Extract the full signature and code of the target method, including Javadoc, from a complete Java class file.

    Args:
        file_content: complete Java class file content
        method_signature: method signature, such as "public void add(String key, Object value)"
                       or only a method name, such as "add"

    Returns:
        (method_signature, method_code)
        method_signature: full method signature, such as "public void add(String key, Object value)"
        method_code: only the method code, including Javadoc and method body
        Return ("", "") when the method cannot be found.
    """
    if not file_content or not method_signature:
        return "", ""

    # Extract method name from signature
    method_name = method_signature.split("(")[0].split()[-1].strip()

    lines = file_content.split("\n")

    # Find the method declaration line
    method_start = -1
    method_sig = ""
    brace_depth = 0
    in_method = False

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Skip javadoc lines before method
        if stripped.startswith("/**") or stripped.startswith("*") or stripped.startswith("*/"):
            if method_start == -1:
                continue

        # Check if this line contains the method declaration
        if method_start == -1:
            # Look for method signature pattern
            if _line_contains_method_declaration(stripped, method_name):
                # Found the method - capture the signature
                method_sig = _extract_full_signature(stripped, lines, i)
                # Include any preceding javadoc
                javadoc_start = i
                for j in range(i - 1, max(0, i - 20), -1):
                    prev = lines[j].strip()
                    if prev.startswith("/**"):
                        javadoc_start = j
                        break
                    elif prev and not prev.startswith("*"):
                        break
                method_start = javadoc_start
                in_method = True
                brace_depth = 0

        if in_method:
            # Count braces to know when method ends
            brace_depth += line.count("{") - line.count("}")
            # Only consider method ended if brace_depth is 0 AND the current line doesn't have {
            # AND we've actually processed at least one line (not the declaration line itself)
            if method_start > 0 and brace_depth == 0 and "{" not in line and i > method_start:
                # Method ended
                method_end = i + 1
                return method_sig, "\n".join(lines[method_start:method_end])

    # Fallback: if we found method but didn't get brace closure
    if method_start != -1:
        return method_sig, "\n".join(lines[method_start:])

    return "", ""


def _extract_full_signature(first_line: str, all_lines: list[str], first_line_idx: int) -> str:
    """
    Extract a full method signature, possibly spanning multiple lines.

    e.g., "protected Object decode(\n    Channel channel, ..." -> "protected Object decode(Channel channel, ...)"
    """
    if not first_line:
        return first_line

    # If the line ends with { or ;, the signature is complete
    if first_line.strip().endswith("{") or first_line.strip().endswith(";"):
        return first_line.strip().rstrip("{").rstrip(";").strip()

    # Otherwise, look for closing ) and opening {
    sig_lines = [first_line]
    paren_depth = first_line.count("(") - first_line.count(")")

    for j in range(first_line_idx + 1, len(all_lines)):
        line = all_lines[j].strip()
        sig_lines.append(line)
        paren_depth += line.count("(") - line.count(")")
        if paren_depth <= 0:
            # Found closing )
            break

    sig = " ".join(sig_lines).replace("\n", " ")
    # Remove trailing { if present
    sig = sig.rstrip("{").rstrip(";").strip()
    return sig


def _line_contains_method_declaration(line: str, method_name: str) -> bool:
    """Check if a line contains a method declaration for the given method name."""
    if not line or not method_name:
        return False

    stripped = line.strip()

    # Skip comments and empty lines
    if stripped.startswith("//") or stripped.startswith("/*") or stripped.startswith("*") or not stripped:
        return False

    # Skip lines without the method name
    if method_name not in stripped:
        return False

    # Must have opening paren (it's a method call or declaration)
    if "(" not in stripped:
        return False

    # Look for the pattern: [modifiers] return_type method_name(
    # Extract the part before the method name
    idx = stripped.find(method_name)
    before = stripped[:idx].strip()

    # Check if it looks like a method declaration
    # Should have visibility modifier or be a constructor/class/record
    valid_starts = ["public", "private", "protected", "static", "final", "abstract",
                    "synchronized", "native", "strictfp", "transient", "volatile"]
    for start in valid_starts:
        if before.endswith(start) or before.startswith(start):
            # Must be followed by opening brace on same line (declaration) or
            # have proper structure (not just "methodName(args);")
            if "{" in stripped or ("=" not in stripped and ";" not in stripped.split("(")[0]):
                return True
            # Check if it's a method call after assignment like "obj.methodName(...)"
            if "=" in before:
                return False

    # Constructor (no return type before method name)
    # But only if it looks like a declaration, not a call
    if not before.strip():
        # Method call like "checkTemplateContracts(c);" - ends with ; and no {
        # Method declaration like "checkTemplateContracts() {" or "checkTemplateContracts() throws Exception {"
        if stripped.endswith(";"):
            return False  # It's a statement, not a declaration
        if "{" in stripped:
            return True  # Has opening brace, likely a declaration

    return False


def find_file_in_tree(repo_path: Path, ref: str, filename: str) -> str:
    """Search a git tree at a given ref for a filename and return its full path.

    Args:
        repo_path: repository path
        ref: git ref, such as a commit SHA or branch ref
        filename: file name, e.g., "PropertyListBuilderTest.java", or
                  partial path, e.g., "configurationdata/PropertyListBuilderTest.java"

    Returns:
        Full path, such as "src/test/java/ch/.../PropertyListBuilderTest.java".
        Return "" when no matching path is found.
    """
    result = subprocess.run(
        ["git", "-C", str(repo_path), "ls-tree", "-r", "--name-only", ref],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0:
        return ""
    for line in result.stdout.splitlines():
        if line.endswith("/" + filename) or line == filename:
            return line
    return ""


def extract_class_from_file_path(file_path: str) -> str:
    """Extract the class name from a file path for logging and diagnostics."""
    match = re.search(r"/([A-Z][^/]+)\.java$", file_path)
    if match:
        return match.group(1)
    return file_path.split("/")[-1].replace(".java", "")


def _run_clone(cmd: list[str], timeout: int = 180) -> subprocess.CompletedProcess:
    """Run a git clone command with proper timeout + child process cleanup."""
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        stdout, stderr = proc.communicate(timeout=timeout)
        return subprocess.CompletedProcess(cmd, proc.returncode, stdout, stderr)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()
        raise


def clone_or_update(url: str, dest: Path, branch: str = "master") -> bool:
    """
    Clone a repository to dest, skipping it if it already exists.

    Tries the specified branch first, then falls back to 'main' if the
    specified branch doesn't exist (common issue: many repos use 'main' as
    default branch instead of 'master').
    """
    if dest.exists() and (dest / ".git").exists():
        # Already cloned — skip pull (we only need historical commits, not latest)
        return True

    # Clone with specified branch
    try:
        result = _run_clone(
            ["git", "clone", "--branch", branch, url, str(dest)],
            timeout=180,
        )
        if result.returncode != 0:
            stderr = result.stderr.lower()
            # Only try 'main' fallback if the error is branch-not-found, not network failure
            is_network_error = any(s in stderr for s in [
                "could not resolve", "connection", "timed out", "unable to access",
                "failed to connect", "couldn't connect",
            ])
            if branch != "main" and not is_network_error:
                import shutil
                if dest.exists():
                    shutil.rmtree(dest, ignore_errors=True)
                result = _run_clone(
                    ["git", "clone", "--branch", "main", url, str(dest)],
                    timeout=180,
                )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        import shutil
        if dest.exists():
            shutil.rmtree(dest, ignore_errors=True)
        return False

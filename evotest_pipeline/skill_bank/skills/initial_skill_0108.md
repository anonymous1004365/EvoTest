---
name: interactive-shell-exit-code-verification
description: When a Shell interactively executes commands with execCommand option,
  verify that exitCode is properly set after each command execution, including built-in
  commands like 'about'. Use assertEquals assertions on getExitCode() to catch missing
  exitCode assignments.
code_tags:
- ARGUMENT_VALIDATION
- STATE_MUTATION
test_pattern: STATE_TEST
---

# interactive-shell-exit-code-verification

## Instructions

# Interactive Shell Exit Code Verification

## Instructions

- WHEN the system under test is an interactive shell class (e.g., `Shell`) that supports executing commands via `execCommand` option (e.g., `-e` or `--exec-command`), and the `Shell` has an `exitCode` field (e.g., `protected int exitCode = 0`) and a `getExitCode()` accessor
- THEN the test must verify that `getExitCode()` returns the correct value after each shell command execution. Specifically:
  - For any built-in shell command (e.g., `about`), after executing it via `shell.execCommand(command, true, true)`, assert that `shell.getExitCode()` equals the expected exit code (e.g., `assertEquals(0, shell.getExitCode())` for success, `assertTrue(shell.getExitCode() > 0)` for failure)
  - Test at least one command that does NOT explicitly set the exit code before returning — the `exitCode` field may retain a stale value from a previous failed command if the new command does not reset it
  - Verify the exit code immediately after the command's `execute()` method returns, before any surrounding shell logic modifies it

- Common pitfalls:
  - Testing only the output (stdout/stderr) without checking `getExitCode()` — the exit code may be wrong even when output looks correct
  - Assuming a successful command automatically sets `exitCode = 0` — the fix for this bug required adding `exitCode = 0` at the end of `AboutCommand.execute()`, meaning the exit code was not being set
  - Checking `getExitCode()` only after a failing command — also check after a successful command that previously might have had a failing command before it, to ensure the exit code is reset

### Example (correct)
```java
// Test that 'about' command sets exit code to 0
@Test
public void aboutCommandSetsExitCode() throws IOException {
  Shell shell = new Shell();
  // Execute the 'about' command
  shell.execCommand("about", true, true);
  assertEquals("Exit code should be 0 after successful 'about' command",
      0, shell.getExitCode());
}
```

### Example (incorrect — missing exit code check)
```java
// BAD: Only checks that something was printed, not the exit code
@Test
public void aboutTest() throws IOException {
  Shell shell = new Shell();
  shell.execCommand("about", true, true);
  // No assertion on getExitCode() — this would miss the bug
}
```

### Example (incorrect — wrong expected value)
```java
// BAD: Assumes exit code is 0 without actually asserting
@Test
public void aboutTest() throws IOException {
  Shell shell = new Shell();
  shell.execCommand("about", true, true);
  // If previous failed command set exitCode=1, this would still pass incorrectly
  // assertEquals(0, shell.getExitCode()) needed here
}
```
---
name: setiter-command-name-validation
description: When testing shell commands that configure iterators via the `setiter`
  command, the TG should verify that passing a class name without an explicit iterator
  name in the `-name` option causes an IllegalArgumentException. The bug manifests
  when `setiter -class <ClassName> -p <priority>` is used without `-name <name>` —
  the buggy code incorrectly requires a name but should infer it from the iterator's
  OptionDescriber.
code_tags:
- ARGUMENT_VALIDATION
- EXCEPTION_HANDLING
- USER_INPUT_EDGE_CASE
test_pattern: STATE_TEST
---

# setiter-command-name-validation

## Instructions

# SetIter Command Name Validation

## Instructions

- WHEN the TG encounters a shell command like `setiter -class VersioningIterator -p 1` (or any iterator class) that is called WITHOUT providing the `-name` option:
  - THEN the TG should test that the command **fails with a non-zero exit code** and the output contains `"java.lang.IllegalArgumentException"`.
  - The TG should verify that the `exec(command, false, "java.lang.IllegalArgumentException")` pattern correctly expects a bad exit with that exception message present in output.

- WHEN the TG encounters the `setiter` command with a `-class` option specifying a known iterator class like `VersioningIterator`, `RegExFilter`, `AgeOffFilter`, `ReqVisFilter`, or a fully-qualified class name:
  - THEN the TG should test TWO scenarios:
    1. **Without `-name`:** The command should fail (bad exit) because the iterator class name alone is not a valid iterator name — the code expects either an explicit `-name` or a name inferred from the OptionDescriber, but the buggy version fails to handle the case where no default name is available.
    2. **With `-name`:** The command should succeed (good exit) when a valid name is provided.

- WHEN the TG writes a test that involves the `exec` helper method from `ShellTest`:
  - THEN the TG should use the pattern `exec(commandString, expectGoodExit, expectedString)` where:
    - `commandString` is the raw shell command string (e.g., `"setiter -class VersioningIterator -p 1"`)
    - `expectGoodExit` is `false` for the bug-triggering case
    - `expectedString` is `"java.lang.IllegalArgumentException"` to verify the failure message

- Common pitfalls to avoid:
  - ❌ Testing only with `-name` provided — this will succeed and NOT catch the bug. The bug is specifically that `setiter -class VersioningIterator -p 1` (without `-name`) should work but throws an `IllegalArgumentException`.
  - ❌ Using `assertGoodExit` or expecting exit code 0 for the no-name case — the buggy version will return a non-zero exit code with the exception message.
  - ❌ Forgetting to create the table first — the test must call `exec("createtable test", true)` before running `setiter` commands, because `setiter` requires being in a table context.
  - ❌ Not resetting state between subtests — each test method should use `@Before` setup which creates a fresh shell and temporary config file.

### Correct test example:
```java
@Test
public void setIterTest() throws IOException {
    exec("createtable test", true);
    // This triggers the bug: no -name option provided
    exec("setiter -class VersioningIterator -p 1", false, "java.lang.IllegalArgumentException");
}
```

### Incorrect test example (will NOT catch the bug):
```java
@Test
public void setIterTest() throws IOException {
    exec("createtable test", true);
    // Always providing -name avoids the bug entirely
    exec("setiter -class VersioningIterator -p 1 -name myiter", true);
}
```
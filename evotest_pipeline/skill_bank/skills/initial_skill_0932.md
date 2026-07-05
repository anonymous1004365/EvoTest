---
name: cli-frontend-info-command-parsing
description: When testing command-line frontends that parse parameters from a String
  array and call an internal method like `info()`, the TG should verify the method
  correctly handles parameter ordering, unrecognized options, and missing required
  arguments by asserting non-zero return codes or specific output.
code_tags:
- ARGUMENT_VALIDATION
- BOUNDARY_CHECK
- NULL_CHECK
- EXCEPTION_HANDLING
- STATE_MUTATION
test_pattern: PARAMETRIC_TEST
---

# cli-frontend-info-command-parsing

## Instructions

# CLI Frontend Info Command Parameter Handling

## Instructions

- WHEN the TG encounters a command-line frontend class (e.g., `CliFrontend`) that has a method accepting a `String[]` of parameters and processes sub-commands via action strings such as `"info"`, `"run"`, `"list"`, etc., and the method is expected to parse these parameters for a job JAR path, parallelism flags (`-p`), or other options
- THEN the TG should write a test that:
  1. Creates an instance of the frontend using a valid configuration directory (e.g., `CliFrontendTestUtils.getConfigDir()`)
  2. Calls the method under test (e.g., `testFrontend.info(parameters)`) with various parameter arrays
  3. For valid inputs, asserts the return code is `0` and that the output (captured from stdout) contains expected content (e.g., `"parallelism": "17"` in execution plan JSON)
  4. For invalid/unrecognized options (e.g., `{"-v", "-l"}`) or missing required arguments (e.g., `{}`), asserts the return code is non-zero
  5. Captures stdout by replacing `System.out` with a `ByteArrayOutputStream` before the call and restoring it afterwards, then asserts on the captured buffer content

- WHEN testing parameter combinations, specifically test with:
  - Only the JAR path (no parallelism flag) — verify default parallelism in output
  - A parallelism flag followed by a value and then the JAR path (e.g., `{"-p", "17", "/path/to/jar"}`) — verify the specified parallelism appears in output
  - The `-f` flag before the JAR path (e.g., `{"/path/to/jar", "-f", "true"}`) — verify the execution plan is generated

- WHEN asserting on return codes, always use `assertTrue(retCode == 0)` for success and `assertTrue(retCode != 0)` for failure

- Common pitfalls to avoid:
  - Do NOT test the `info()` method directly by passing null or empty parameters without wrapping in try-catch — the method may throw exceptions instead of returning non-zero codes for truly invalid input
  - Do NOT forget to replace and restore `System.out` using `ByteArrayOutputStream` for tests that check stdout content; wrap the restore in a `finally` block
  - Do NOT assume that an invalid option like `-v` or `-l` causes an exception — the return code check (`assertTrue(retCode != 0)`) is the correct way to verify failure
  - Do NOT test parameter ordering inconsistently: the JAR path may come before or after certain flags depending on the command, so test both valid orderings

### Correct example

```java
@Test
public void testShowExecutionPlan() {
    PrintStream stdOut = System.out;
    ByteArrayOutputStream buffer = new ByteArrayOutputStream();
    System.setOut(new PrintStream(buffer));
    try {
        String[] parameters = new String[] { CliFrontendTestUtils.getTestJarPath(), "-f", "true"};
        CliFrontend testFrontend = new CliFrontend(CliFrontendTestUtils.getConfigDir());
        int retCode = testFrontend.info(parameters);
        assertTrue(retCode == 0);
        assertTrue(buffer.toString().contains("\"parallelism\": \"1\""));
    } catch (Exception e) {
        fail("Program caused an exception: " + e.getMessage());
    } finally {
        System.setOut(stdOut);
    }
}
```

### Incorrect example

```java
@Test
public void testInfoBad() {
    CliFrontend frontend = new CliFrontend(CliFrontendTestUtils.getConfigDir());
    // WRONG: passing only '-v' which is not a valid info option, expecting exception
    frontend.info(new String[]{"-v"}); // may not throw and may not return expected code
}
```
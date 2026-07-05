---
name: mutually-exclusive-option-validation
description: When shell commands define options that should be mutually exclusive
  (like -b and --begin-row), test that the command validates this exclusivity and
  produces proper help or error messages. Use this skill when adding options that
  conflict with each other.
code_tags:
- VALIDATION
- STATE_MUTATION
test_pattern: STATE_TEST
---

# mutually-exclusive-option-validation

## Instructions

# Mutually Exclusive Option Validation

## Instructions

- WHEN the TG encounters a shell command class (extending `ShellCommand` or using Apache Commons CLI `Options`) that defines options which should be mutually exclusive (e.g., a `-b`/`--begin-row` shortcut option and a `-`-/`--begin-row` long option on the same field, or any two options that conflict)
- THEN the TG should write a test that exercises the command's help/validation output **after adding** the conflicting options, and verify that the usage/help text reflects the exclusivity.
  - Specifically, the test should:
    1. Create an instance of the command (e.g., `new MergeCommand()`).
    2. Call the method that builds or returns options (e.g., `getOptions()`).
    3. Verify that when both conflicting options are present on the same `Options` object, the help text or validation output contains the expected restriction message (e.g., `"-b should say it is exclusive"`).
  - Use `assertEquals` or `assertTrue` on the string representation returned by the command's `getOptions()` or equivalent method.
  - The test should NOT assume the command runs against a live shell or ZooKeeper instance — it should be a unit test that only checks option metadata/help output.

- **Common pitfalls to avoid:**
  - Do NOT write integration tests that try to execute the shell command (e.g., invoke `execute()`), because that may require a full cluster or shell environment.
  - Do NOT test that the command "works" without the conflict — test that the conflict is correctly described in the help text.
  - Do NOT forget to call the method that actually assembles the options (e.g., `getOptions()`) — testing the command class's constructor alone is insufficient.
  - Do NOT test only the presence of options — test the specific wording or flag (e.g., `"exclusive"`, `"mutually exclusive"`, `"cannot be used with"`) that the fix introduced to describe the restriction.

### Correct Example (Covers the Bug):
```java
// MergeCommandTest.java
@Test
public void testBeginRowHelp() {
  MergeCommand command = new MergeCommand();
  String optionsHelp = command.getOptions().toString();
  assertTrue("Expected -b to mention exclusivity in help text, but got: " + optionsHelp,
      optionsHelp.contains("exclusive"));
}
```

### Incorrect Example (Missing the Bug):
```java
// Does not test that -b help says it is exclusive — only tests option existence
@Test
public void testBeginRowHelp_WRONG() {
  MergeCommand command = new MergeCommand();
  String optionsHelp = command.getOptions().toString();
  assertTrue(optionsHelp.contains("-b"));  // just checks option exists, not the exclusivity
}
```
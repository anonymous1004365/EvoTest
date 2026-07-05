---
name: cli-option-description-accuracy
description: Ensures CLI option descriptions accurately document inclusivity/exclusivity
  semantics. Use this when testing command-line option help texts to verify they correctly
  document boundary behavior (e.g., "-b begin-row (exclusive)").
code_tags:
- BOUNDARY_CHECK
test_pattern: STATE_TEST
---

# cli-option-description-accuracy

## Instructions

# CLI Option Description Accuracy

## Instructions

**WHEN** the TG encounters a command-line option (CLI) whose help description mentions row ranges, inclusivity, or exclusivity semantics — such as `startRowOpt()` / `endRowOpt()` methods in `OptUtil` returning an `Option` with a description like "begin row (exclusive)" or "end row (inclusive)" — **THEN** the TG should write a test that directly accesses the `Option` object from the command's `getOptions()` and verifies the description string contains the correct boundary keyword.

- **Concrete check**: For a `startRowOpt()` option (short opt `-b`, long opt `--begin-row`), assert that `getOption("b").getDescription()` contains `"(exclusive)"`. For an `endRowOpt()` option (short opt `-e`, long opt `--end-row`), assert that `getOption("e").getDescription()` contains `"(inclusive)"`.
- **Test pattern**: Construct the command object (e.g., `new DeleteRowsCommand()`), call `getOptions().getOption("b")`, then inspect the returned `org.apache.commons.cli.Option`'s description.
- **Failure expectation on buggy version**: The absence of the boundary keyword in the description string causes `assertTrue(...)` to fail.

**Common pitfalls to avoid**:
- Do NOT test only by parsing the default help output from the command; directly access the `Option` via `getOptions().getOption(opt)` to isolate the description text.
- Do NOT assume that because an option is named "begin-row" it is exclusive — always verify the description string contains the keyword.
- Do NOT test the `endRow` option description when the bug is in the `startRow` description (and vice versa); test each option independently.
- Do NOT use `assertEquals` with a full description string — the description may change in other ways; use `assertTrue(description.contains("(exclusive)"))` for robustness.

**Correct example** (testing that `-b` option description says it is exclusive):
```java
@Test
public void testBeginRowHelp() {
    assertTrue("-b should say it is exclusive",
        new DeleteRowsCommand().getOptions().getOption("b")
            .getDescription().contains("(exclusive)"));
}
```

**Incorrect example** (testing the wrong keyword or using wrong assertion):
```java
// BAD: testing that -b says "inclusive" when it should say "exclusive"
@Test
public void testBeginRowHelp() {
    assertTrue("-b should say it is inclusive",  // WRONG keyword
        new DeleteRowsCommand().getOptions().getOption("b")
            .getDescription().contains("(inclusive)"));
}
```
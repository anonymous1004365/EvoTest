---
name: shared-option-description-context-mismatch
description: When a shared utility method creates CLI options with a fixed help description,
  some commands may reuse the option with different semantics (e.g., inclusive vs
  exclusive). The test should verify that each command's option description matches
  that command's actual behavior, not just the shared factory's default.
code_tags:
- INPUT_VALIDATION
- STATE_MUTATION
- COMMAND_LINE_HELP_TEXT
- SHARED_OPTION_VARIANT_DESCRIPTION
test_pattern: PARAMETRIC_TEST
---

# shared-option-description-context-mismatch

## Instructions

# Shared Option Description Context Mismatch

## Instructions

- WHEN the TG encounters a shared/utility method that creates a CLI option with a fixed help description (e.g., `OptUtil.startRowOpt()` always returns `"begin row (exclusive)"`), AND that option is reused by multiple commands that may interpret the option differently (e.g., one command treats begin-row as exclusive, another treats it as inclusive)

- THEN the TG should:
  1. Identify ALL commands that reuse the same shared option from the utility class (e.g., `OptUtil.startRowOpt()`)
  2. For each command, determine what the option's description SHOULD be based on that command's actual semantics (e.g., for `DeleteRowsCommand`, the begin row is NOT inclusive — start rows are NOT deleted — so help text should say "(exclusive)")
  3. Create a test that instantiates each command (e.g., `new DeleteRowsCommand()`) and checks that `command.getOptions().getOption("b").getDescription()` contains the correct semantic descriptor (e.g., `contains("(exclusive)")`)
  4. If the command's own semantics differ from the shared factory's default, verify the test fails on buggy code and passes on fixed code

- Common pitfalls:
  - Only testing the shared utility method (`OptUtil.startRowOpt()`) instead of each command's actual option description. The shared factory may say "exclusive" but a particular command may need "inclusive" — yet the command just reuses the factory method without overriding.
  - Using `assertEquals` with the full description string when `contains()` is sufficient and more robust.
  - Forgetting that some commands (like `ScanCommand`) create their own variant option (`optStartRowInclusive`) separate from the shared utility, meaning both paths need testing.
  - Only testing one direction (e.g., only checking begin-row is exclusive) and missing cases where begin-row should be inclusive for other commands.

### Correct Example (DeleteRowsCommandTest)
```java
@Test
public void testBeginRowHelp() {
    assertTrue("-b should say it is exclusive",
        new DeleteRowsCommand().getOptions().getOption("b")
            .getDescription().contains("(exclusive)"));
}
```

### Pitfall Example (only testing the shared OptUtil)
```java
// WRONG: This only tests the shared factory, not the command
@Test
public void testBeginRowHelp() {
    Option opt = OptUtil.startRowOpt();
    assertTrue(opt.getDescription().contains("(exclusive)"));
}
```
The above test would pass even if the `DeleteRowsCommand` were changed to create its own option with "(inclusive)" because it never actually checks the command's own options.
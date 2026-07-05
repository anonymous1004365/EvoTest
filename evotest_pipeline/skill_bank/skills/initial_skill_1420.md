---
name: token-without-option-handling
description: When accepting tokens (with tokenClass option) without a password/pass
  option, the code must catch and handle ParameterException properly. This skill teaches
  how to test that no ParameterException leak occurs when a token is provided without
  its required options.
code_tags:
- ARGUMENT_VALIDATION
- BOUNDARY_CHECK
- NULL_CHECK
test_pattern: STATE_TEST
---

# token-without-option-handling

## Instructions

# Token Without Option Handling

## Instructions

- WHEN the TG encounters code that accepts a `--tokenClass` option (a token) without requiring the `--pass` (password) option — meaning the token is provided standalone without a password — THEN the TG should write a test that:
  - Constructs a shell command that includes only a `--tokenClass` argument without the `--pass` option.
  - Captures the output (e.g., `OutputStream`, `ByteArrayOutputStream`, or similar) to verify the shell's behavior.
  - Verifies that `ParameterException.class.getName()` does **NOT** appear in the output stream (meaning the exception was gracefully handled and not leaked to the user).
  - Conversely, also write a test where a token is provided with `--pass` (and possibly other valid options) and verify that the shell processes the command successfully.
- Common pitfalls:
  - **Testing only the valid-path scenario**: Do not assume all combinations of token/password are valid. A token without a password should be gracefully handled, not crash or leak exceptions.
  - **Forgetting to capture output in a test-friendly way**: Use a `PrintStream` wrapping a `ByteArrayOutputStream` (or similar) so you can inspect what the shell writes to the user.
  - **Testing only String type parameters**: The `--tokenClass` option accepts a `CtTypeReference<?>` or similar non-String type; ensure you pass the correct type when testing.
  - **Not asserting both positive and negative cases**: Write one test asserting the error message does NOT contain `ParameterException` for a token without password, and another test asserting it DOES contain `ParameterException` when both token and password are missing.

### Correct Example (Java)

```java
@Test
public void testTokenWithoutOptions() throws IOException {
  // Setup: Create a ByteArrayOutputStream to capture output
  ByteArrayOutputStream output = new ByteArrayOutputStream();
  Shell shell = new Shell();
  
  // Act: Execute config with only --tokenClass (no --pass)
  shell.config("--tokenClass", "some.token.Class");
  
  // Assert: No ParameterException should be in the output
  assertFalse(output.toString().contains(ParameterException.class.getName()));
}
```

### Incorrect Example (Java)

```java
@Test
public void testTokenWithoutOptions() throws IOException {
  // BAD: Only tests the valid path (token + password), never tests token alone
  Shell shell = new Shell();
  shell.config("--tokenClass", "some.token.Class", "--pass", "mypassword");
  
  // BAD: Does not check that missing password is handled gracefully
  // No assertion about ParameterException at all!
}
```
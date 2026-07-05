---
name: wicket-message-resolver-escape-value-validation
description: When testing resource message resolvers that support markup escaping
  via an escape parameter, the TG should test that both valid escape values (true/false)
  and invalid/malformed escape parameter values are handled correctly, especially
  when the escape value is parsed from a string attribute. The skill prevents silent
  fallback or incorrect escaping behavior when the escape attribute contains a non-boolean
  value.
code_tags:
- STRING_ESCAPE_HANDLING
- RESOURCE_RESOLUTION_FALLBACK
test_pattern: EXCEPTION_TEST
---

# wicket-message-resolver-escape-value-validation

## Instructions

# Wicket Message Resolver Escape Value Validation

## Instructions

- WHEN the TG encounters code that resolves `wicket:message` markup tags with an optional `escape` attribute (e.g., a boolean string like `"true"` or `"false"`)
- THEN it should test that:
  1. When the `escape` attribute is set to a valid boolean string (`"true"` or `"false"`), the message is resolved with the correct escaping behavior (escaped when `"true"`, raw/unescaped when `"false"`).
  2. When the `escape` attribute is set to a malformed or non-boolean value (e.g., an empty string `""`, a random string like `"invalid"`, or any value that is neither `"true"` nor `"false"`), the resolver must **not** silently fall through with incorrect escaping behavior — it should either throw an appropriate exception (e.g., `IllegalArgumentException`, `StringIndexOutOfBoundsException`) or clearly expose the failure. The test should verify this with an assertion on the exception type or by observing the incorrect fallback behavior (e.g., unexpected `StringIndexOutOfBoundsException`).


- **Concrete example from this codebase**: The `WicketMessageResolver` resolves `wicket:message` tags in markup. It reads the `escape` attribute value to decide whether to HTML-escape the resolved message. If the escape attribute value is set to an empty string `""` (or any invalid non-boolean value), the buggy version may throw a `StringIndexOutOfBoundsException` or silently fall back to incorrect escaping. The test `test_1` in `WicketMessageResolverTest` triggers this exact case using markup that has an empty `escape` value.

- **Common pitfalls**:
  - Testing only valid `"true"` / `"false"` escape values but not edge cases like empty string, null, or garbage values — these malformed values should provoke errors or clear failures.
  - Assuming the resolver gracefully handles all attribute values; a malformed escape parameter should be explicitly tested and the expected failure behavior documented/asserted.
  - Not testing the interaction between escape attribute parsing and the message lookup/resolution fallback path — the escape parsing happens regardless of whether the resource key exists.

- **Correct test approach**:
  ```java
  // Test with a valid escape=false value (message should NOT be escaped)
  // Expected: message text rendered as-is (raw HTML)

  // Test with a valid escape=true value (message should be escaped)
  // Expected: HTML special chars in message are escaped

  // Test with an INVALID escape value (e.g. empty string)
  // Expected: Should throw StringIndexOutOfBoundsException or similar
  //   because the code tries to charAt(0) on an empty string
  assertThrows(StringIndexOutOfBoundsException.class, () -> {
      tester.startPage(new WicketMessageResolverEscapePageWrongEscapeValue());
  });
  ```

- **Incorrect test approach**:
  ```java
  // WRONG: Only testing valid escape values, ignoring invalid ones
  // This would miss the bug where empty escape attribute causes
  // runtime exceptions or silent misbehavior
  tester.startPage(new WicketMessageResolverEscapePage());
  // No assertion for malformed escape values at all
  ```
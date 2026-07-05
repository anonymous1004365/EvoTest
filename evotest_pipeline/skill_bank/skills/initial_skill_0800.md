---
name: jmx-objectname-escape-control-chars
description: When testing JMX ObjectName escaping logic like Server.escape(), test
  that carriage return (\r) and newline (\n) characters are handled correctly to prevent
  MalformedObjectNameException. The bug was that \r was silently dropped but the test
  input had the wrong escape sequence, causing downstream JMX construction to fail.
code_tags:
- NULL_CHECK
- VALIDATION
- ARGUMENT_VALIDATION
- ESCAPING_SPECIAL_CHARACTERS
- INPUT_VALIDATION_SPECIAL_CHARS
test_pattern: PARAMETRIC_TEST
---

# jmx-objectname-escape-control-chars

## Instructions

# JMX ObjectName Control Character Escaping

## Instructions

- WHEN the TG encounters a method that escapes strings for JMX `ObjectName` construction (like `Server.escape(String name)`), and the method has a `switch`/`case` block handling control characters `\r` (carriage return) and `\n` (line feed):
  - THEN the TG should test BOTH `\r` and `\n` characters as distinct inputs.
  - THEN the TG should verify the expected escaped output string, and then use it to construct an `ObjectName` via `new ObjectName(String.format(LoggerContextAdminMBean.PATTERN, escapedName))` to ensure no `MalformedObjectNameException` is thrown.
  - THEN for `\r` (carriage return), the expected behavior is that it is silently **dropped** (replaced with empty string / `continue` without appending). Test with input `"a\rc"` and expect output `"ac"`.
  - THEN for `\n` (line feed), the expected behavior is that it is **replaced** with the literal two-character sequence `\\n` (backslash-n), AND the value must be quoted. Test with input `"a\nc"` and expect output `"\"a\\nc\""`.
  - THEN after obtaining the escaped string, verify it's valid by passing it to `new ObjectName(...)` — this is the critical integration check that catches the bug.

- **Common pitfalls to avoid**:
  - ❌ Testing only one of `\r` or `\n` — both must be tested separately as they have different escape behaviors.
  - ❌ Testing the escape output string but NOT constructing an `ObjectName` from it — the bug manifests as a `MalformedObjectNameException` at JMX construction time, not as a wrong string.
  - ❌ Confusing `\r` (carriage return) with `\n` (line feed) in test inputs — the test names `testEscapeEscapesLineFeed` and `testEscapeEscapesCarriageReturn` were swapped in the buggy version (line feed test used `\r` and carriage return test used `\n`).

- **Correct test example**:
```java
// Test carriage return (\r) is dropped
@Test
public void testEscapeEscapesCarriageReturn() throws Exception {
    final String ctx = "a\rc";
    final String ctxName = Server.escape(ctx);
    assertEquals("ac", ctxName);
    new ObjectName(String.format(LoggerContextAdminMBean.PATTERN, ctxName));
}

// Test line feed (\n) is replaced with \\n and quoted
@Test
public void testEscapeEscapesLineFeed() throws Exception {
    final String ctx = "a\nc";
    final String ctxName = Server.escape(ctx);
    assertEquals("\"a\\nc\"", ctxName);
    new ObjectName(String.format(LoggerContextAdminMBean.PATTERN, ctxName));
}
```

- **Incorrect test (buggy version)**:
```java
// WRONG: test names and inputs are swapped
@Test
public void testEscapeEscapesLineFeed() throws Exception {
    final String ctx = "a\rc";  // uses \r, not \n
    ...
}

@Test
public void testEscapeEscapesCarriageReturn() throws Exception {
    final String ctx = "a\nc";  // uses \n, not \r
    ...
}
```
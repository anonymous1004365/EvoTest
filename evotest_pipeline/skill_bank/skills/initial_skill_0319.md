---
name: jmx-escape-carriage-return-linefeed-handling
description: When testing a string escape method for JMX ObjectName values, the TG
  must verify that carriage return (\r) characters are properly dropped (removed)
  while line feed (\n) characters are replaced with the literal escape sequence "\\n".
  This skill applies to escape() methods that process control characters in JMX context.
code_tags:
- ESCAPE_ENCODING
- STRING_CHARACTER_REPLACEMENT
- SPECIAL_CHARACTER_HANDLING
test_pattern: PARAMETRIC_TEST
---

# jmx-escape-carriage-return-linefeed-handling

## Instructions

# JMX Escape: Carriage Return Dropping vs Line Feed Replacement

## Instructions

**WHEN** the TG encounters a method that escapes a `String` for use in JMX `ObjectName` values, specifically one that handles whitespace/control characters like `\r` (carriage return, 0x0D) and `\n` (line feed, 0x0A):

- **THEN** the TG MUST write separate tests that verify:
  1. **Carriage return (`\r`, char 0x0D)** is **silently dropped** (removed) from the output. For input `"a\rc"`, the escaped result should be `"ac"` (no quotes around it unless other special characters are present).
  2. **Line feed (`\n`, char 0x0A)** is **replaced with the literal string `"\\n"`** (two characters: backslash followed by `n`). For input `"a\nc"`, the escaped result should be `"\"a\\nc\""` (quoted value with escaped newline sequence).

- **THEN** the TG MUST verify that these two distinct control characters receive **different, opposite handling**: `\r` is removed entirely, while `\n` is escaped to a literal two-character sequence. The bug manifests when `\r` is mistakenly treated like `\n` (e.g., also replaced with `\\r` or `\\n` instead of being dropped).

- **THEN** the TG MUST write tests where:
  - The input string contains a `\r` character (Java literal `"\r"` or `String.valueOf((char) 0x0D)`)
  - The expected output is the input with `\r` simply removed (e.g., `"a\rc"` → `"ac"`)
  - The test assertion checks the exact returned String from the escape method

- **THEN** the TG MUST also write tests where:
  - The input string contains a `\n` character (Java literal `"\n"` or `String.valueOf((char) 0x0A)`)
  - The expected output contains the literal two-character sequence `\n` (not an actual newline)
  - The test assertion checks the exact returned String

**Common pitfalls to avoid:**
- ❌ Testing only `\n` (line feed) and assuming `\r` (carriage return) gets the same treatment
- ❌ Expecting `\r` to be replaced with `\\r` (the literal escape sequence "\\r") — `\r` is **dropped**, not escaped
- ❌ Not using `.equals()` on the raw `String` result, and instead only testing that no `MalformedObjectNameException` is thrown (the bug may not cause an exception, just produce incorrect output)
- ❌ Confusing `\r` (carriage return, 0x0D) with `\n` (line feed, 0x0A) when reading test failure messages — the diff shows `expected:<a[]c> but was:<a[\r]c>` meaning `\r` was present when it should have been removed

**Correct example:**
```java
// Tests that carriage return (\r) is *dropped* from the escaped output
@Test
public void testEscapeEscapesLineFeed() throws Exception {
    final String ctx = "a\rc";
    final String ctxName = Server.escape(ctx);
    assertEquals("ac", ctxName);  // \r is removed, output is "ac"
    new ObjectName(String.format(LoggerContextAdminMBean.PATTERN, ctxName));
}

// Tests that line feed (\n) is replaced with the literal string "\n"
@Test
public void testEscapeEscapesCarriageReturn() throws Exception {
    final String ctx = "a\nc";
    final String ctxName = Server.escape(ctx);
    assertEquals("\"a\\nc\"", ctxName);  // \n becomes the two-char sequence \n, and the value is quoted
    new ObjectName(String.format(LoggerContextAdminMBean.PATTERN, ctxName));
}
```

**Incorrect example (would miss the bug):**
```java
// BUG: This test only checks that no exception is thrown, but misses
// that \r was incorrectly NOT dropped from the output
@Test
public void testEscapeLineFeed() throws Exception {
    final String ctx = "a\nc";
    final String ctxName = Server.escape(ctx);
    assertNotNull(ctxName);  // Always passes — does not detect the bug
    new ObjectName(String.format(LoggerContextAdminMBean.PATTERN, ctxName));
}
```
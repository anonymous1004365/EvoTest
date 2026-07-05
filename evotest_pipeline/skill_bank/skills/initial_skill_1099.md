---
name: jmx-objectname-escaping-roundtrip
description: WHEN testing string escaping for JMX ObjectName values, THEN verify not
  only the escaped output format but also that the escaped string can be parsed back
  by ObjectName.getInstance() without throwing MalformedObjectNameException. This
  skill helps catch bugs where escaping is incorrect for special characters like double
  quotes.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- VALIDATION
- STRING_ESCAPING
test_pattern: EXCEPTION_TEST
---

# jmx-objectname-escaping-roundtrip

## Instructions

# JMX ObjectName Escaping Roundtrip Test

## Instructions

WHEN testing a static `escape(String)` method (e.g., `Server.escape()`) that is designed to escape strings for use as values in JMX `ObjectName` values:

- THEN test with input strings containing each special character defined by the JMX ObjectName specification: double quote (`"`), backslash (`\`), asterisk (`*`), question mark (`?`), comma (`,`), equals (`=`), colon (`:`), carriage return (`\r`), and line feed (`\n`)
- THEN verify that the escaped output string can be successfully passed to `new ObjectName(String.format(PATTERN, escapedValue))` without throwing a `MalformedObjectNameException`. This validates the round-trip correctness of the escaping.
- THEN specifically test the double-quote character (`"`) with input like `"a\"c"`, expecting the escape method to produce `"a\\"c"` (a backslash-escaped quote inside a quoted value)
- WHEN testing a character that should be escaped (like double quote `"`), verify that the character is preceded by a backslash in the output
- WHEN testing a character that should cause the value to be quoted (like comma `,`), verify the output is wrapped in surrounding double quotes but the comma itself is NOT backslash-escaped
- **Common pitfall**: Only testing that a special character is present in the output without also asserting the exact formatting. For example, asserting `ctxName.contains("\\\"")` passes for both `"a\\"c"` (correct) and `a"c` (incorrect — missing leading quote). Always use `assertEquals` with the full expected string.
- **Common pitfall**: Not testing round-trip `ObjectName` construction. A character may be "escaped" in a way that still produces an invalid `ObjectName`, or not escaped in a way that silently produces a different `ObjectName`.
- **Common pitfall**: Forgetting that the escape method must handle the full set of JMX special characters — especially the backslash itself, which must itself be escaped.

### Correct test pattern:
```java
@Test
public void testEscapeQuotesAndEscapesQuote() throws Exception {
    final String ctx = "a\"c";
    final String ctxName = Server.escape(ctx);
    assertEquals("\"a\\\"c\"", ctxName);
    new ObjectName(String.format(LoggerContextAdminMBean.PATTERN, ctxName)); 
    // no MalformedObjectNameException = success
}
```

### Incorrect test pattern (would NOT catch the bug):
```java
@Test
public void testEscapeQuote() {
    // Only checking containment, not exact format
    String result = Server.escape("a\"c");
    assertTrue(result.contains("\\\""));  // Too weak — passes for broken output too
}
```
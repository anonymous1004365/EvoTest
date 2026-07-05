---
name: config-lookup-npe-prevention
description: When testing MessagePatternConverter with a valid Configuration, verify
  that the lookup/StrSubstitutor
code_tags:
- NULL_CHECK
- CONFIG_LOOKUP_DISABLE
test_pattern: EXCEPTION_TEST
---

# config-lookup-npe-prevention

## Instructions

# Config Lookup NullPointerException Prevention

## Instructions

- WHEN the TG encounters MessagePatternConverter being tested with a non-null Configuration (e.g., `new DefaultConfiguration()`)
  THEN the TG MUST verify that the `format()` method handles lookups safely without throwing NullPointerException.
  Specifically, when `config.getStrSubstitutor().replace(event, value)` is called inside the `format()` method,
  the StrSubstitutor may return null for certain values (e.g., `"${date:now:buhu}"`), and the
  `StringBuilder.append(CharSequence)` method will throw NullPointerException when appending null.

  The TG should test with:
  1. A `SimpleMessage` containing a lookup pattern like `"${date:now:buhu}"` — this triggers the
     `config.getStrSubstitutor().replace(event, value)` path in the code.
  2. A `ParameterizedMessage` containing the same lookup pattern — this triggers the second branch
     of the `format()` method at the end.
  3. Use a real `Configuration` (e.g., `new DefaultConfiguration()`) so that `config != null` is true,
     which enables the lookup replacement logic.

- WHEN the TG writes the test assertion
  THEN the TG should NOT check the exact output (it may vary depending on configuration), but instead
  should verify that NO exception is thrown during the call. A simple way is:
  ```java
  converter.format(event, sb);
  // No assertion needed — the test passes if no exception is thrown
  ```
  Or optionally verify that the result is non-null and contains the expected partial output.

- Common pitfalls:
  - Testing with `config = null` only, which bypasses the lookup replacement logic entirely (since the
    code checks `if (config != null && !noLookups)`).
  - Testing only with `SimpleMessage` but not `ParameterizedMessage` — the bug may exist in both
    branches of the `format()` method.
  - Forgetting that `noLookups` must be false (the default) to exercise the lookup path.
  - Hard-coding the expected replacement result, which may differ across environments or configurations.

- Correct example:
```java
@Test
public void testSimpleMessageLookupWithConfiguration() {
    Configuration config = new DefaultConfiguration();
    MessagePatternConverter converter = MessagePatternConverter.newInstance(config, null);
    // Use SimpleMessage with a lookup pattern
    Message msg = new SimpleMessage("${date:now:buhu}");
    LogEvent event = Log4jLogEvent.newBuilder()
            .setLoggerName("MyLogger")
            .setLevel(Level.DEBUG)
            .setMessage(msg).build();
    StringBuilder sb = new StringBuilder();
    // This must not throw NullPointerException
    converter.format(event, sb);
    // Optional: verify output is reasonable
    assertNotNull(sb.toString());
}
```

```java
@Test
public void testParameterizedMessageLookupWithConfiguration() {
    Configuration config = new DefaultConfiguration();
    MessagePatternConverter converter = MessagePatternConverter.newInstance(config, null);
    // Use ParameterizedMessage with a lookup pattern
    Message msg = new ParameterizedMessage("${date:now:buhu}");
    LogEvent event = Log4jLogEvent.newBuilder()
            .setLoggerName("MyLogger")
            .setLevel(Level.DEBUG)
            .setMessage(msg).build();
    StringBuilder sb = new StringBuilder();
    // This must not throw NullPointerException
    converter.format(event, sb);
    assertNotNull(sb.toString());
}
```

- Incorrect example (too weak — config is null, so lookup path is never exercised):
```java
@Test
public void testPatternWithNullConfiguration() {
    MessagePatternConverter converter = MessagePatternConverter.newInstance(null, null);
    Message msg = new SimpleMessage("${date:now:buhu}");
    // ...
    converter.format(event, sb);
    // This passes even if the lookup path has a bug — config is null, lookup is skipped
}
```
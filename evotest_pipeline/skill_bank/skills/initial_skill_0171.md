---
name: console-appender-follow-attribute-validation
description: When testing builders that set boolean attributes on appender managers,
  validate that the boolean value is correctly propagated to the manager instead of
  being ignored/reset. This skill helps catch bugs where builder boolean parameters
  are not properly passed through to internal manager factories.
code_tags:
- VALIDATION
- NULL_CHECK
- ARGUMENT_VALIDATION
test_pattern: STATE_TEST
---

# console-appender-follow-attribute-validation

## Instructions

# ConsoleAppender Follow Attribute Validation

## Instructions

- WHEN the TG encounters a builder class (e.g., `ConsoleAppender.Builder`) that has a boolean attribute like `follow`, AND this attribute is used to construct an appender via a `getManager()` call that accepts the boolean parameter,
- THEN the TG should write a test that verifies the boolean attribute is correctly propagated to the created manager. The test should:
  1. Use a `DirectRouteBuilder` (or equivalent string-based builder API) to construct two appender instances — one with `follow=true` and one with `follow=false` (or default).
  2. For a `ConsoleAppender`, do NOT use `ConsoleAppender.newBuilder()` or `ConsoleAppender.Builder` directly. Instead, use the `DirectRouteBuilder` approach:
     ```java
     Configuration config = ConfigurationFactory.getInstance().getConfiguration();
     // Build with follow=true
     final ConsoleAppender appender1 = ConsoleAppender.newBuilder()
         .setName("test")
         .setFollow("true")
         .setLayout(PatternLayout.newBuilder().withPattern("%m%n").build())
         .build();
     // Also build with follow=false (or default)
     final ConsoleAppender appender2 = ConsoleAppender.newBuilder()
         .setName("test")
         .setFollow("false")
         .setLayout(PatternLayout.newBuilder().withPattern("%m%n").build())
         .build();
     // Cast the manager to check its follow state
     assertTrue(appender1.getManager() instanceof OutputStreamManager);
     // Verify that the manager's follow state differs based on the builder parameter
     ```
  3. For `ConsoleAppender`, the `getManager()` returns an `OutputStreamManager`. Check the manager's behavior by capturing output: set up a `ByteArrayOutputStream`/`ByteArrayOutputStream` manager and verify that the `follow=true` version produces the expected output while `follow=false` produces empty output (indicating the follow parameter was lost).
  4. The key assertion: when `follow=true`, the appender should flush/output messages. When `follow=false` (or default), the appender should NOT output messages (because the follow parameter controls whether the manager follows the System.out stream).

- Common pitfalls to avoid:
  - **DO NOT** assume that a string "true" value set on a builder will be automatically parsed and propagated to the underlying manager. Some builders parse and validate the string but then fail to pass the boolean to the `getManager()` method.
  - **DO NOT** test only with one value (e.g., only `follow=true`). Always test the boolean toggle with both `true` and `false` to catch propagation failures.
  - **DO NOT** rely solely on the builder's `toString()` or getter methods. The bug may be in the construction path, not in the builder's state.
  - **DO NOT** use `ConsoleAppender.Builder` directly (i.e., `new ConsoleAppender.Builder()`) — this may bypass the validation logic in `createAppender`. Always use the static `newBuilder()` method.

### Correct approach (catches the bug):
```java
@Test
public void testFollow() {
    final ConsoleAppender appender = ConsoleAppender.newBuilder()
        .setName("test")
        .setFollow("true")
        .setLayout(PatternLayout.newBuilder().withPattern("%m%n").build())
        .build();
    final OutputStreamManager manager = appender.getManager();
    // The manager should have follow=true behavior
    // Capture output to verify
    final ByteArrayOutputStream baos = new ByteArrayOutputStream();
    manager.setOutputStream(baos);
    appender.append(LogEvent...); // create a test log event
    assertEquals("Expected message%n", baos.toString());
}
```

### Incorrect approach (misses the bug):
```java
@Test
public void testFollow() {
    final ConsoleAppender appender = ConsoleAppender.newBuilder()
        .setName("test")
        .setFollow("true")
        .setLayout(PatternLayout.newBuilder().withPattern("%m%n").build())
        .build();
    // ONLY checks builder state, NOT manager behavior
    assertEquals("true", appender.getFollow()); // This might pass even if bug exists
}
```
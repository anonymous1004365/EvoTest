---
name: session-temporary-state-on-feedback
description: When testing session binding behavior that depends on feedback messages,
  ensure the mock session's temporary state is correctly managed. Use this skill when
  a test verifies that feedback messages trigger session binding (making a temporary
  session permanent).
code_tags:
- STATE_MUTATION
- ORDER_DEPENDENCY
test_pattern: STATE_TEST
---

# session-temporary-state-on-feedback

## Instructions

# Session Temporary State on Feedback Messages

## Instructions

- WHEN the test verifies that adding feedback messages (via `Session.info()`, `Session.error()`, `Session.warn()`, etc.) causes a temporary session to become permanent (non-temporary)
- THEN ensure the test properly sets up the mock session as temporary BEFORE adding feedback messages. Call `session.setTemporary(true)` explicitly in test setup if the default mock session state is not guaranteed to start as temporary
- WHEN the test checks that after a redirect, the session is no longer temporary, the test must also verify that `getSession().isTemporary()` returns `false` after the redirect (not just that the session exists or that no exception is thrown)
- Include a check that calls `assertFalse(session.isTemporary())` after the redirect to confirm the session binding occurred due to feedback messages
- Common pitfall: Testing only that feedback messages are displayed or that no error occurs during redirect, without verifying the session's `temporary` state changed from `true` to `false`. Without verifying `isTemporary()`, the test would miss the bug where feedback messages do NOT trigger session binding.

### Correct Example (catches the bug):
```java
@Test
public void bindSessionWhenThereAreFeedbackMessages()
{
    // The mock session starts as temporary
    assertTrue(tester.getSession().isTemporary());
    
    // Add a feedback message - this should trigger session binding
    tester.getSession().info("test message");
    
    // Execute a redirect (or any action that processes the request)
    tester.executeUrl("./some-page");
    
    // Verify the session is no longer temporary
    assertFalse(tester.getSession().isTemporary());
}
```

### Incorrect Example (misses the bug):
```java
@Test
public void bindSessionWhenThereAreFeedbackMessages()
{
    tester.getSession().info("test message");
    tester.executeUrl("./some-page");
    // Missing: assertFalse(tester.getSession().isTemporary());
    // Without this check, the test passes even if the session stays temporary
}
```
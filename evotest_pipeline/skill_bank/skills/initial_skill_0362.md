---
name: init-parameter-case-insensitivity
description: WHEN testing ServletContainerInitializer implementations that read context
  init parameters to decide whether to auto-initialize, THEN test that the parameter
  value comparison is case-insensitive for the string "true". This skill prevents
  bugs where only lowercase "true" is handled but "TRUE" or "True" is not.
code_tags:
- VALIDATION
- STATE_MUTATION
test_pattern: PARAMETRIC_TEST
---

# init-parameter-case-insensitivity

## Instructions

# Init Parameter Case-Insensitivity Validation

## Instructions

- WHEN the code under test reads a `ServletContext` init parameter via `getInitParameter(...)` and compares it to a string value (e.g., `"true"`) using `equalsIgnoreCase()` or a similar case-insensitive method, or when the code uses `Boolean.parseBoolean()` or similar

- THEN the test MUST cover the case where the parameter value is the same string but in a different case (e.g., `"TRUE"`, `"True"`, `"tRuE"`). Do NOT assume the comparison is case-insensitive — if the code uses `"true".equals(someValue)` instead of `"true".equalsIgnoreCase(someValue)`, it will fail for uppercase values like `"TRUE"`.

- Common pitfalls:
  - Testing only with the lowercase value `"true"` and not also with other case variants like `"TRUE"` or `"True"`
  - Assuming that because the production code says "set to 'true' to disable" in documentation, only the literal string `"true"` needs testing
  - Not testing with `null` parameter value to verify the default behavior works

- For the Log4jServletContainerInitializer specifically:
  - The constant `Log4jWebSupport.IS_LOG4J_AUTO_INITIALIZATION_DISABLED` has value `"isLog4jAutoInitializationDisabled"`
  - Test with parameter value `"true"` (lowercase) — should skip initialization
  - Test with parameter value `"TRUE"` (uppercase) — should also skip initialization if `equalsIgnoreCase` is used; would incorrectly proceed with initialization if only `equals` is used
  - Test with parameter value `"false"` — should proceed with initialization
  - Test with parameter value `null` — should proceed with initialization (default behavior)

### Example (correct):
```java
// Test with lowercase "true" — should disable initialization
given(servletContext.getInitParameter(eq(Log4jWebSupport.IS_LOG4J_AUTO_INITIALIZATION_DISABLED)))
    .willReturn("true");
containerInitializer.onStartup(null, servletContext);
// verify NO initialization happened

// Test with uppercase "TRUE" — should also disable initialization
given(servletContext.getInitParameter(eq(Log4jWebSupport.IS_LOG4J_AUTO_INITIALIZATION_DISABLED)))
    .willReturn("TRUE");
containerInitializer.onStartup(null, servletContext);
// verify NO initialization happened

// Test with null — should proceed with initialization
given(servletContext.getInitParameter(eq(Log4jWebSupport.IS_LOG4J_AUTO_INITIALIZATION_DISABLED)))
    .willReturn(null);
containerInitializer.onStartup(null, servletContext);
// verify initialization happened
```

### Example (incorrect — missing case variety):
```java
// BAD: Only tests lowercase "true"
given(servletContext.getInitParameter(eq(Log4jWebSupport.IS_LOG4J_AUTO_INITIALIZATION_DISABLED)))
    .willReturn("true");
containerInitializer.onStartup(null, servletContext);
// This passes even if the code uses "true".equals(value) — but would fail for "TRUE" in production
```
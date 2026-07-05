---
name: servlet-version-gate-check
description: When validating Servlet API version conditions that use both getMajorVersion()
  and getEffectiveMajorVersion(), test both the container-level and application-level
  version gates separately. This skill catches bugs where only one version check is
  tested or where edge cases like "container is 3.x but app is 2.x effective" are
  missed.
code_tags:
- VALIDATION
- NULL_CHECK
- ORDER_DEPENDENCY
test_pattern: STATE_TEST
---

# servlet-version-gate-check

## Instructions

# Servlet Version Gate Check

## Instructions

- WHEN the TG encounters a method that checks BOTH `getMajorVersion()` and `getEffectiveMajorVersion()` (or similar "declared vs effective" version pairs) as a combined condition to decide whether to proceed with initialization
- THEN the TG MUST write a test that stubs `getEffectiveMajorVersion()` to return a value LOWER than `getMajorVersion()` (e.g., container declares 3 but effective is 2) and verify that the method does NOT proceed with initialization (i.e., no filters are added, no listeners are registered, no lifecycle methods are called)
- Concrete example from this codebase: the condition is `servletContext.getMajorVersion() > 2 && servletContext.getEffectiveMajorVersion() > 2`. The test `testOnStartupWithServletVersion3_xEffectiveVersion2_x` stubs `getMajorVersion()` to return 3 and `getEffectiveMajorVersion()` to return 2, then verifies that no filter registration, listener addition, or lifecycle calls happen.
- Common pitfalls to avoid:
  - Testing only `getMajorVersion()` without also independently testing `getEffectiveMajorVersion()` — this misses the case where container version is high but the app's effective version is low.
  - Forgetting to stub `getEffectiveMajorVersion()` at all — this can cause NullPointerException or unexpected behavior if the mock returns default (0) which might accidentally pass the check.
  - Forgetting to verify that NO side effects occurred (no `addFilter`, `addListener`, `start()`, `setLoggerContext()` calls) when the version check should fail.
  
- **Correct example:**
```java
// Test that when container declares Servlet 3.x but effective version is 2.x,
// initialization is SKIPPED entirely (no filters, no listeners, no lifecycle)
@Test
public void testOnStartupWithServletVersion3_xEffectiveVersion2_x() throws Exception {
    given(servletContext.getMajorVersion()).willReturn(3);
    given(servletContext.getEffectiveMajorVersion()).willReturn(2);

    containerInitializer.onStartup(null, servletContext);

    // Verify NO interactions
    then(servletContext).should(never()).addFilter(anyString(), any(Class.class));
    then(servletContext).should(never()).addListener(any(EventListener.class));
}
```

- **Incorrect example (missing effective version stub):**
```java
// BAD: Only stubs getMajorVersion(), doesn't stub getEffectiveMajorVersion()
// The mock returns default int (0) for getEffectiveMajorVersion(), which might
// accidentally satisfy or fail the condition for the wrong reason
@Test
public void testOnStartupWithServletVersion3_x() throws Exception {
    given(servletContext.getMajorVersion()).willReturn(3);
    // MISSING: given(servletContext.getEffectiveMajorVersion()).willReturn(...);
    // Default Mockito behavior returns 0 for int, which would fail the >2 check
    // This gives a false sense of correctness — the test passes but the
    // effective version check is never properly exercised
    
    containerInitializer.onStartup(null, servletContext);
    // This passes but doesn't validate the effective version logic
}
```

- Use Mockito's `BDDMockito.given(...).willReturn(...)` to stub the servlet context version methods and `then(...).should(never()).method()` to verify no initialization actions occurred when the version gate should block.
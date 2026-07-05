---
name: servlet-initializer-failure-recovery
description: When testing a ServletContainerInitializer that performs multiple side-effect
  operations (adding filters, listeners, starting initializers), the TG must test
  failure recovery paths — verifying that partial failures (e.g., initializer.start()
  throwing) do not leave the ServletContext in an inconsistent state, and that earlier
  operations like filter registration still complete.
code_tags:
- ORDER_DEPENDENCY
- STATE_MUTATION
test_pattern: EXCEPTION_TEST
---

# servlet-initializer-failure-recovery

## Instructions

# Servlet Container Initializer Failure Recovery

## Instructions

- WHEN the TG encounters a `ServletContainerInitializer.onStartup()` method that performs sequential side-effect operations (adding a filter via `servletContext.addFilter()`, starting a `Log4jWebLifeCycle` via `initializer.start()`, calling `initializer.setLoggerContext()`, adding a listener via `servletContext.addListener()`, and configuring the filter),  
- THEN the TG should write tests that **inject failures** at intermediate steps (e.g., make `initializer.start()` throw an `IllegalStateException`) and verify that:
  1. The exception **propagates** to the caller (i.e., the test expects the same exception to be thrown from `onStartup()`).
  2. The **side effects that already happened** (e.g., filter registration via `servletContext.addFilter()`) are still observable/verifiable after the failure.
  3. The **actions that would have come after the failure** (e.g., `setLoggerContext()`, `addListener()`) **never** execute.

- WHEN testing a failure scenario where `servletContext.addFilter()` returns `null` (indicating a pre-existing filter with the same name),  
- THEN the TG should verify that `onStartup()` returns **without throwing an exception** and without calling any further initialization steps (no `getWebLifeCycle()`, no `initializer.start()`, no listener registration).

- Common pitfalls to avoid:
  - **Only testing the happy path**: Many developers test only when everything succeeds, missing the failure-recovery and partial-state scenarios.
  - **Asserting only the exception**: Catching the exception is not enough — the TG must verify that earlier side effects are preserved (e.g., the filter was registered) and later side effects are suppressed.
  - **Using `@Test(expected = ...)` instead of a try-catch**: The TG should use a try-catch block (or `assertThrows` with additional assertions after the exception) so that it can also verify side effects that survived the failure.
  - **Forgetting to mock intermediate state**: The TG must properly mock `servletContext.addFilter()` to return a non-null `FilterRegistration.Dynamic` when testing the `initializer.start()` failure path.

### Correct Example (testing failure of initializer.start())

```java
@Test
public void testOnStartupFailedDueToInitializerFailure() throws Exception {
    final FilterRegistration.Dynamic registration = mock(FilterRegistration.Dynamic.class);
    final IllegalStateException exception = new IllegalStateException("test");
    given(servletContext.getMajorVersion()).willReturn(3);
    given(servletContext.getEffectiveMajorVersion()).willReturn(3);
    given(servletContext.getInitParameter(eq(Log4jWebSupport.IS_LOG4J_AUTO_INITIALIZATION_DISABLED))).willReturn("false");
    given(servletContext.addFilter(eq("log4jServletFilter"), any())).willReturn(registration);
    given(servletContext.getAttribute(Log4jWebSupport.SUPPORT_ATTRIBUTE)).willReturn(initializer);
    willThrow(exception).given(initializer).start();

    try {
        this.containerInitializer.onStartup(null, this.servletContext);
        fail("Expected the exception thrown by the initializer; got no exception.");
    } catch (final IllegalStateException e) {
        assertSame("The exception is not correct.", exception, e);
    }

    // Verify filter was still registered despite the failure
    then(servletContext).should().addFilter(eq("log4jServletFilter"), any());
    // Verify start() was called (and threw)
    then(initializer).should().start();
    // Verify that later operations were NOT called
    then(initializer).should(never()).setLoggerContext();
    then(servletContext).should(never()).addListener(any());
}
```

### Correct Example (testing pre-existing filter cancellation)

```java
@Test
public void testOnStartupCanceledDueToPreExistingFilter() throws Exception {
    given(servletContext.getMajorVersion()).willReturn(3);
    given(servletContext.getEffectiveMajorVersion()).willReturn(3);
    given(servletContext.getInitParameter(eq(Log4jWebSupport.IS_LOG4J_AUTO_INITIALIZATION_DISABLED))).willReturn("false");
    given(servletContext.addFilter(eq("log4jServletFilter"), any())).willReturn(null); // filter already exists

    this.containerInitializer.onStartup(null, this.servletContext);

    // Verify filter was attempted
    then(servletContext).should().addFilter(eq("log4jServletFilter"), any());
    // Verify that no further initialization happens
    then(servletContext).should(never()).getAttribute(any());
    then(initializer).should(never()).start();
    then(servletContext).should(never()).addListener(any());
}
```

### Incorrect Example (missing side-effect assertions)

```java
// BAD: Only checks exception, does NOT verify side effects
@Test(expected = IllegalStateException.class)
public void testOnStartupFailedDueToInitializerFailure_BAD() throws Exception {
    given(servletContext.getMajorVersion()).willReturn(3);
    given(servletContext.getEffectiveMajorVersion()).willReturn(3);
    given(servletContext.addFilter(eq("log4jServletFilter"), any())).willReturn(registration);
    given(servletContext.getAttribute(Log4jWebSupport.SUPPORT_ATTRIBUTE)).willReturn(initializer);
    willThrow(new IllegalStateException()).given(initializer).start();

    this.containerInitializer.onStartup(null, this.servletContext);
    // No assertions about filter registration or that later calls never happened!
}
```
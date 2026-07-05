---
name: mdc-cleanup-after-exception
description: When a unit of work (like MDCUnitOfWork) has a clear() method that restores
  original MDC values, tests must verify that clear() is called even when an exception
  occurs during route processing. This skill teaches how to write tests that ensure
  MDC cleanup happens correctly on failure paths.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- VALIDATION
- MDC_CLEANUP_AFTER_EXCEPTION
- STATE_MUTATION
- EXCEPTION_HANDLING
test_pattern: STATE_TEST
---

# mdc-cleanup-after-exception

## Instructions

# MDC Cleanup After Exception

## Instructions

- WHEN the Test Generator encounters a class that extends `DefaultUnitOfWork` and overrides methods like `clear()`, `stop()`, or `afterProcess()` to manage SLF4J MDC context values — specifically when the code captures original MDC values (e.g., `originalExchangeId`, `originalMessageId`, `originalBreadcrumbId`, `originalCorrelationId`, `originalRouteId`, `originalCamelContextId`, `originalTransactionKey`) in the constructor and restores them in `clear()`
- THEN the TG must write a test that:
  1. Creates a route that enables MDC logging (via `context.setUseMDCLogging(true)`)
  2. Includes a route processor that throws a RuntimeException (or similar exception) during processing
  3. Verifies that after the exception is caught/handled, the MDC context on the thread is properly cleaned up — i.e., MDC keys like `camel.routeId`, `camel.exchangeId`, `camel.messageId`, `camel.correlationId`, `camel.breadcrumbId`, `camel.contextId` are either removed or restored to their original (pre-exchange) values
  4. Uses `try { ... } finally { MDC.clear() }` pattern in the test to ensure test isolation
  5. Calls `assertNull(MDC.get("camel.routeId"))` and `assertNull(MDC.get("camel.exchangeId"))` after the route completes with an exception to verify MDC cleanup

- Common pitfalls to avoid:
  - **Pitfall: Testing only the success path.** The bug manifests when an exception is thrown during route processing — the `clear()` method may not be called, leaving stale MDC values on the thread. Always test the failure path.
  - **Pitfall: Not isolating the test thread's MDC.** The test must save and restore MDC state before/after each test method using `MDC.getCopyOfContextMap()` and `MDC.setContextMap(...)` to avoid cross-test pollution.
  - **Pitfall: Assuming MDC keys are removed when they should be restored to previous values.** The `clear()` method in `MDCUnitOfWork` restores original values if they existed, or removes them if they didn't. Verify the expected final state correctly.

- Correct example (testing exception path):
```java
public void testMDCShouldBeCleanedAfterException() throws Exception {
    // Save current MDC
    Map<String, String> originalMdc = MDC.getCopyOfContextMap();
    try {
        MockEndpoint mock = getMockEndpoint("mock:result");
        mock.expectedMessageCount(0);

        // Send a message that triggers an exception in the route
        template.sendBody("direct:exceptionRoute", "Hello World");

        // After exception, MDC should be cleared on this thread
        assertNull("camel.routeId should be null after exception", MDC.get("camel.routeId"));
        assertNull("camel.exchangeId should be null after exception", MDC.get("camel.exchangeId"));
        assertNull("camel.messageId should be null after exception", MDC.get("camel.messageId"));
        assertNull("camel.correlationId should be null after exception", MDC.get("camel.correlationId"));
        assertNull("camel.breadcrumbId should be null after exception", MDC.get("camel.breadcrumbId"));
        assertNull("camel.contextId should be null after exception", MDC.get("camel.contextId"));
    } finally {
        // Restore original MDC
        MDC.clear();
        if (originalMdc != null) {
            MDC.setContextMap(originalMdc);
        }
    }
}
```

- Incorrect example (testing only success path):
```java
public void testMDCSuccessPath() throws Exception {
    // This only tests the happy path — if clear() is broken only on exception paths,
    // this test passes while the bug remains undetected
    MockEndpoint mock = getMockEndpoint("mock:result");
    mock.expectedBodiesReceived("Success");
    template.sendBody("direct:success", "Hello");
    assertMockEndpointsSatisfied();
    // No MDC assertions at all!
}
```

- In the route builder, the TG should add:
```java
from("direct:exceptionRoute").routeId("exception-route")
    .process(new Processor() {
        public void process(Exchange exchange) throws Exception {
            throw new RuntimeException("Forced exception to test MDC cleanup");
        }
    })
    .to("mock:result"); // This should never be reached
```
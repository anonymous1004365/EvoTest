---
name: exception-request-handler-chain-testing
description: Use this skill when testing stackable request handlers in listener-based
  error handling, like the onException handler in RequestCycle. It ensures multiple
  exception-triggered request handlers are correctly chained and executed sequentially
  without being dropped.
code_tags:
- NULL_CHECK
- MAP_OPERATIONS
- VALIDATION
test_pattern: STATE_TEST
---

# exception-request-handler-chain-testing

## Instructions

# Exception Request Handler Chain Testing

## Instructions

- WHEN the TG encounters a method that handles exceptions by iterating through `IRequestCycleListener` instances (e.g., `RequestCycle.onException()`) and returns an `IRequestHandler`, and the exception handling can result in a chain of handlers
- THEN the TG should write a test that:
  1. Registers **two or more** `IRequestCycleListener` instances whose `onException()` methods each return a non-null `IRequestHandler`
  2. Verifies that all returned handlers are executed in sequence (not just the first one)
  3. For each handler in the chain, checks that a side effect (e.g., counter increment, flag set) occurred
  4. Specifically expects that on the buggy version, only the first listener's handler is executed and the remaining listeners' handlers are skipped; on the fixed version, all are executed
- Common pitfalls to avoid:
  - Registering only one listener — that will not expose the handler-dropping bug
  - Checking only that no exception is thrown — the test must verify each listener's handler was **actually invoked**
  - Not verifying the order of execution — listeners may fire out of expected sequence
  - Forgetting that listener exceptions may be rethrown or suppressed — test must account for the actual exception propagation behavior

### Correct example (exposes the bug)
```java
@Test
public void testAllExceptionHandlersAreExecuted()
{
    final AtomicInteger handler1Count = new AtomicInteger(0);
    final AtomicInteger handler2Count = new AtomicInteger(0);

    RequestCycle cycle = new RequestCycle(...);
    cycle.getListeners().add(new AbstractRequestCycleListener()
    {
        @Override
        public IRequestHandler onException(RequestCycle cycle, Exception ex)
        {
            handler1Count.incrementAndGet();
            return new MyRequestHandler();
        }
    });
    cycle.getListeners().add(new AbstractRequestCycleListener()
    {
        @Override
        public IRequestHandler onException(RequestCycle cycle, Exception ex)
        {
            handler2Count.incrementAndGet();
            return new MyRequestHandler();
        }
    });

    try
    {
        cycle.scheduleRequestHandlerAfterCurrent(null);
        // ... trigger request that causes exception
    } catch (Exception e) { /* expected if propagate */ }

    // BUGGY: handler2Count will be 0 because only the first handler is returned and executed
    // FIXED: both handler1Count and handler2Count are 1
    assertEquals("Second listener's handler was not executed!", 1, handler2Count.get());
}
```

### Incorrect example (only tests a single listener — misses the bug)
```java
@Test
public void testExceptionHandler()
{
    final AtomicInteger count = new AtomicInteger(0);
    cycle.getListeners().add(new AbstractRequestCycleListener()
    {
        @Override
        public IRequestHandler onException(RequestCycle cycle, Exception ex)
        {
            count.incrementAndGet();
            return new MyRequestHandler();
        }
    });
    // BUG: Only one listener — the bug of dropping subsequent handlers is never triggered
    // The test passes on both buggy and fixed versions, giving a false sense of security
}
```
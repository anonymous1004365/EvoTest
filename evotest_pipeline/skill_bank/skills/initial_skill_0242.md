---
name: lifecycle-strategy-service-management
description: Teaches the TG to test that a LifecycleStrategy which is also a Service
  is properly auto-started when added to a CamelContext. Use this when the TG sees
  LifecycleStrategy implementations added via addLifecycleStrategy() and the strategy
  implements Service.
code_tags:
- STACK_OPERATION
test_pattern: STATE_TEST
---

# lifecycle-strategy-service-management

## Instructions

# LifecycleStrategy Service Auto-Start Testing

## Instructions

- WHEN the code adds a `LifecycleStrategy` implementation (via `addLifecycleStrategy(LifecycleStrategy strategy)`) and that implementation also implements `Service` (e.g., extends `ServiceSupport` or implements the `Service` interface directly) inside a `CamelContext`
- THEN the test MUST verify that the `LifecycleStrategy` Service is automatically started (i.e., its `start()` method is invoked) after being added to the `CamelContext`, WITHOUT the test needing to manually call `.start()` on the strategy.
- To assert this, the test should add the strategy to the context, then assert that `strategy.isStarted()` returns `true` (or `strategy.isRunAllowed()` returns `true`, depending on the `Service` implementation) — but only AFTER calling `context.start()` (or `context.startAllServices()`) if the context hasn't already been started.
- Common pitfall #1: Adding a `LifecycleStrategy` that is also a `Service` but never verifying that the strategy's lifecycle (start/stop) is managed by the context — the test may pass even if the strategy is never started, because there is no explicit start call.
- Common pitfall #2: Not calling `context.start()` before checking `strategy.isStarted()`. The context must be fully started for the auto-start mechanism to kick in.
- Common pitfall #3: Assuming that adding a `LifecycleStrategy` automatically starts it even if the context itself is not started. The context must be started (or already running) for the strategy's `start()` to be invoked.

### Correct Test Pattern Example

The test should:
1. Create a `CamelContext` (e.g., `new DefaultCamelContext()`)
2. Create a `LifecycleStrategy` that also implements `Service` (e.g., a test double extending `ServiceSupport` and implementing `LifecycleStrategy`)
3. Add the strategy to the context via `context.addLifecycleStrategy(strategy)`
4. Start the context: `context.start()`
5. Assert that the strategy is started: `assertTrue("LifecycleStrategy should be started", ((Service) strategy).isStarted())`

### Incorrect Test Pattern (would miss the bug)

```java
// BAD: Never starts the context, never checks the strategy's started state
CamelContext context = new DefaultCamelContext();
MyLifecycleStrategy strategy = new MyLifecycleStrategy();
context.addLifecycleStrategy(strategy);
// No context.start() called — strategy will NOT be started
// No assertion — the bug is invisible
```
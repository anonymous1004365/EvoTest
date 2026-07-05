---
name: lifecycle-strategy-context-start-on-restart
description: When testing CamelContext lifecycle with LifecycleStrategy hooks, ensure
  that onContextStart is called exactly once per start sequence, including on restart
  after a stop. This skill helps detect bugs where stateful observers fail to reset
  counters or where the context skips lifecycle callbacks on subsequent starts.
code_tags:
- ARGUMENT_VALIDATION
- BOUNDARY_CHECK
- INHERITANCE_CHECK
- STATE_MUTATION
- ORDER_DEPENDENCY
test_pattern: STATE_TEST
---

# lifecycle-strategy-context-start-on-restart

## Instructions

# LifecycleStrategy Context Start Counter Validation

## Instructions

- WHEN the TG encounters a `CamelContext` subclass (e.g., `DefaultCamelContext`) that supports lifecycle strategies via `LifecycleStrategy` (or `LifecycleStrategySupport`) with an `onContextStart(CamelContext)` method:
  - THEN the TG should write a test that:
    1. Creates a custom `LifecycleStrategy` subclass (extending `LifecycleStrategySupport`) that tracks the number of times `onContextStart` is called using an `AtomicInteger` counter.
    2. Registers an instance of this strategy on the `CamelContext` using `context.addLifecycleStrategy(strategy)` **before** the context is started (e.g., in `createCamelContext()`).
    3. Starts the context (which happens automatically in Camel test support via `createCamelContext()`), and verifies the counter is 1.
    4. Stops the context via `context.stop()`.
    5. Starts the context again via `context.start()`.
    6. Verifies the counter is now 2, proving `onContextStart` was called again on the restart.
  - The test should use `org.apache.camel.support.LifecycleStrategySupport` as the base class and `java.util.concurrent.atomic.AtomicInteger` for the counter.
  - Include a `getContextStartCounter()` method returning the `AtomicInteger`'s value.

- WHEN the TG writes a `LifecycleStrategy` test:
  - THEN the TG must verify that the counter increments on restart (context.stop() + context.start()) — not just on initial start.
  - The TG must use `context.stop()` and `context.start()` (not `suspend`/`resume`, which follow a different lifecycle path).

- Common pitfalls to avoid:
  - Testing only a single start without a stop/restart cycle — this misses the bug entirely.
  - Using a `LifecycleStrategy` that reports context start via a different callback (like `onContextStop`) instead of `onContextStart`.
  - Forgetting to add the strategy via `context.addLifecycleStrategy()` before the context is started.
  - Using the same `ProducerTemplate` instance after restart — the test must call `context.createProducerTemplate()` after restart to obtain a new valid template.

- Example of a correct test pattern:
  ```java
  public class MyRestartTest extends ContextTestSupport {
      private MyStrategy strategy = new MyStrategy();

      public void testRestart() throws Exception {
          // Initial start
          assertEquals(1, strategy.getContextStartCounter());

          // Stop and restart
          context.stop();
          context.start();

          // Verify onContextStart was called again
          assertEquals(2, strategy.getContextStartCounter());

          // Obtain new template after restart
          template = context.createProducerTemplate();
          // ... send messages and verify ...
      }

      @Override
      protected CamelContext createCamelContext() throws Exception {
          CamelContext context = super.createCamelContext();
          context.addLifecycleStrategy(strategy);
          return context;
      }

      private class MyStrategy extends LifecycleStrategySupport {
          private AtomicInteger counter = new AtomicInteger();
          @Override
          public void onContextStart(CamelContext context) throws VetoCamelContextStartException {
              counter.incrementAndGet();
          }
          public int getContextStartCounter() { return counter.get(); }
      }
  }
  ```

- Example of incorrect test (would miss the bug):
  ```java
  // BAD: Only tests initial start, never restarts
  public void testStart() throws Exception {
      assertEquals(1, strategy.getContextStartCounter());
      // Missing stop + restart cycle
  }
  ```
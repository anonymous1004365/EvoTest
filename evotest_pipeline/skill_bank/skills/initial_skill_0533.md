---
name: resource-lifecycle-graceful-close
description: When testing resource lifecycle management like Dubbo invokers, test
  that after closing/disconnecting a resource, its availability check returns false
  and that waiting for graceful close completes correctly. This skill catches bugs
  where the internal state changes (e.g., closing during timeout) are not properly
  reflected.
code_tags:
- STATE_MUTATION
- NULL_CHECK
- RESOURCE_LIFECYCLE
test_pattern: STATE_TEST
---

# resource-lifecycle-graceful-close

## Instructions

# Resource Lifecycle Graceful Close State Verification

## Instructions

- WHEN the code under test involves resource lifecycle methods such as `close()`, `disconnect()`, `destroy()`, `shutdown()`, `waitForClose()`, or methods that check resource health like `isAvailable()`:
  - THEN the TG MUST write a state test that:
    1. Opens/creates the resource and verifies it is initially available (e.g., `isAvailable()` returns `true`)
    2. Triggers a close operation (e.g., calling `destroy()` or closing a channel)
    3. The TG MUST simulate a condition where the close waits gracefully (e.g., a timeout or simulated network condition)
    4. After the graceful close completes, verifies that the resource is no longer available (e.g., `isAvailable()` returns `false`)
    5. Verifies that no exception is thrown during the graceful close wait
  - Concrete example: For a `DubboInvoker`, the test should create an invoker with a `ReferenceConfig` pointing to a real or mock `Channel`, call `invoker.destroy()` to trigger close, and then call `invoker.isAvailable()` to assert `false`. Additionally, the test should exercise a `waitForClose()` variant (or simulate a connection close event) and assert that `isAvailable()` returns `false` after the wait completes.
  - Common pitfalls to avoid:
    - Testing only `isAvailable()` without first closing the resource — this misses the bug entirely
    - Testing only the initial state (before close) and not the final state (after close)
    - Assuming that calling `destroy()` or `close()` is enough without verifying the state change with `isAvailable()`
    - Forgetting to simulate a connection close/event that triggers the graceful shutdown path (e.g., a `channel.close()` event or server disconnect)
    - Not including both String-typed and non-typed parameters in the test if the method signature uses generics with type erasure
- Correct example (Java-like pseudocode):
  ```java
  // Create resource
  DubboInvoker invoker = new DubboInvoker(serviceType, url, channel, refConfig);
  assertTrue(invoker.isAvailable());  // initially available
  
  // Trigger graceful close
  channel.close();  // simulate channel disconnect
  invoker.destroy();
  
  // Wait for graceful close
  invoker.waitForClose(CLOSE_TIMEOUT);
  
  // Verify state after close
  assertFalse(invoker.isAvailable());
  ```
- Incorrect example (missing state verification or only testing initial state):
  ```java
  DubboInvoker invoker = new DubboInvoker(serviceType, url, channel, refConfig);
  assertTrue(invoker.isAvailable());  // only tests initial state, never closes
  // Missing: close and verify isAvailable() becomes false
  ```
- The TG should recognize `STATE_MUTATION` risk signals (methods that change internal state like `destroy()`, `close()`) and combine them with `RESOURCE_LIFECYCLE` signals to write a two-phase state test.
---
name: network-receive-after-close-race
description: When testing async network or stream implementations where close() and
  receive() can race concurrently, test that receive() after close() does not hang/block
  indefinitely. Use timeout-based assertions to detect deadlock or infinite blocking
  scenarios.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- NULL_CHECK
test_pattern: PARAMETRIC_TEST
---

# network-receive-after-close-race

## Instructions

# Network Receive After Close Race

## Instructions

- WHEN the TG encounters an async network/stream implementation where `close()` or `shutdown()` is called on a connection while `receive()` or `read()` may be blocking on the same connection:
  - THEN it should write a test that calls `close()` first, then attempts a `receive()` operation, and verifies that the receive does not block indefinitely (e.g., no deadlock or hang).
  - Use a timeout-based mechanism (e.g., `assertTimeoutPreemptively` or `future.get(timeout, TimeUnit.MILLISECONDS)`) to fail the test if the receive hangs.
  - Expect that after close, a subsequent receive should either return a clean signal (e.g., `null`, `-1`, empty) or throw a specific exception indicating the connection is closed (e.g., `IOException`, `ClosedChannelException`).
  - If the implementation uses a blocking queue internally (e.g., `LinkedBlockingQueue`, `SynchronousQueue`, `ArrayBlockingQueue`), verify that the close operation correctly interrupts or unblocks any pending `take()` or `poll()` calls on that queue, so that future calls do not block forever.

- WHEN the TG is testing a resource that uses an internal queue for data transfer between producer and consumer threads:
  - THEN it should test that after closing the resource, a consuming operation does not block on the queue indefinitely.
  - Verify that the close logic either drains/interrupts the queue or otherwise unblocks waiting consumers.

- Common pitfalls:
  - Testing only the happy path where data is received before close, missing the race case where close happens first.
  - Assuming receive() will throw an exception after close without verifying — the implementation may silently hang instead.
  - Not using timeouts in the test — blocking tests without timeouts can cause CI hangs.
  - Testing close() and receive() sequentially in the same thread, missing the concurrent/interleaving scenario.

- Example of correct test approach:
```java
// Setup network connection
AsyncNetwork network = new AsyncNetwork(...);
network.start();

// Close first
network.close();

// Then receive — should not hang
assertTimeoutPreemptively(ofMillis(5000), () -> {
    byte[] data = network.receive();
    // Verify behavior: either null, empty, or exception
    assertNull(data);  // or assertThrows(IOException.class, ...)
});
```

- Example of incorrect test approach (missing close-before-receive scenario):
```java
// ❌ BAD: Only tests sequential close after receive
network.start();
byte[] data = network.receive();  // might block forever here
network.close();
```
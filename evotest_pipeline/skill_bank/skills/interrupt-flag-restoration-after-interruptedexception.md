---
name: interrupt-flag-restoration-after-interruptedexception
description: WHEN a method catches InterruptedException and throws a different exception
  (e.g., BackOffInterruptedException, RuntimeException), THEN verify that Thread.currentThread().interrupt()
  is called before throwing, so the interrupt flag is preserved. Test by using a mock/stub
  that throws InterruptedException, catching the resulting exception, and asserting
  Thread.interrupted() returns true.
code_tags:
- INTERRUPT_FLAG
- THREAD_INTERRUPTION
- EXCEPTION_HANDLING
- CONCURRENCY
- STATE_MUTATION
test_pattern: EXCEPTION_TEST
evolution:
  active: true
  priority: 0
  evidence:
    added: 1
retrieval:
  applicable_tiers:
  - BUG_DETECTED
  - PASS_BOTH
  transition_tags: []
  keywords:
  - interrupt
  - InterruptedException
  - Thread.interrupted
  - backOff
  - sleep
  - thread interruption
  - catch InterruptedException
  - interrupt flag
---

WHEN the TG encounters a catch block that catches InterruptedException and throws a custom/runtime exception, THEN write a test that: 1) Sets up a mock/stub that throws InterruptedException when called, 2) Invokes the method under test, 3) Catches the expected exception, 4) Asserts that Thread.interrupted() returns true (indicating the interrupt flag was restored). This catches bugs where the interrupt flag is swallowed. Common pitfall: using assertThrows which may clear the interrupt flag before the assertion — use try-catch instead.
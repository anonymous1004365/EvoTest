---
name: akka-actor-testable-wrapper-async-timing
description: WHEN testing an Akka actor wrapper that forwards messages to both a TestProbe
  and an actual actor, recognize that the actual actor processes messages asynchronously.
  Side effects (store persistence, state changes) cannot be asserted immediately after
  tell() without proper synchronization.
code_tags:
- ACTOR_TESTING
- ASYNC_PROCESSING
- PROBE_SYNCHRONIZATION
- STATE_MUTATION
- CONCURRENCY
test_pattern: STATE_TEST
evolution:
  active: true
  priority: 0
  evidence:
    added: 1
retrieval:
  applicable_tiers:
  - FAIL_ON_FIXED
  - BUG_DETECTED
  transition_tags: []
  keywords:
  - akka
  - actor
  - testkit
  - testprobe
  - testable
  - wrapper
  - forwarding
  - async
  - tell
  - probe
  - TestableCallContextProvider
  - actor testing
---

WHEN the TG encounters a testable actor wrapper class that forwards messages to both a TestProbe and an actual actor: 1) The probe receives the message synchronously because the wrapper actor tells the probe before telling the actual actor. 2) The actual actor processes messages asynchronously on its own dispatcher. 3) Assertions on side effects of the actual actor (store persistence, state changes) must NOT be made immediately after tell() — they require waiting for a response or using a probe to observe a completion message. 4) Safe tests include: verifying the probe receives the forwarded message, verifying the ref is non-null, and verifying message content.
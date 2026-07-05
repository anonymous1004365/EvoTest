---
name: taskmanager-reconnect-after-jobmanager-failure
description: WHEN a TaskManager encounters a JobManager failure and must reconnect/re-register,
  THEN test that the TaskManager successfully resumes operation by re-registering
  (sending a RegisterTaskManager message). This skill helps catch bugs where the TaskManager's
  reconnect logic fails under job manager failure scenarios.
code_tags:
- VALIDATION
- NULL_CHECK
- BOUNDARY_CHECK
- CONCURRENCY
- STATE_MUTATION
- ORDER_DEPENDENCY
test_pattern: STATE_TEST
---

# taskmanager-reconnect-after-jobmanager-failure

## Instructions

# TaskManager Reconnect After JobManager Failure

## Instructions

WHEN the TG encounters a test scenario where a TaskManager (TM) must reconnect after a JobManager (JM) failure:

- THEN the TG should verify that the TaskManager re-registers by expecting a `RegisterTaskManager` message (via `expectMsgClass(RegistrationMessages.RegisterTaskManager.class)`) within a reasonable timeout.
- Specifically, after simulating a JobManager failure (e.g., stopping the JobManager actor and starting a fresh one), the TaskManager must discover the new JobManager and send a registration request. The test MUST await this message using `expectMsgClass` with a timeout (e.g., `timeout` in milliseconds), NOT simply check for an already-received message in the mailbox.
- The test flow should be: (1) set up a TaskManager connected to a JobManager, (2) kill/stop the JobManager, (3) start a new JobManager, (4) verify the TaskManager reconnects by receiving `RegisterTaskManager`.
- Use `new JavaTestKit(javaSystem)` or `new TestKit(javaSystem)` to create test actors that can receive and inspect messages from the TaskManager.
- Common pitfalls to avoid:
  - **Pitfall 1**: Testing only the initial registration (before JM failure) without testing re-registration after JM failure.
  - **Pitfall 2**: Using insufficient timeout values (e.g., too short for network reconnection delays). Use at least a few seconds (e.g., `new Duration(5000, MILLISECONDS)`).
  - **Pitfall 3**: Not properly cleaning up ActorSystems between tests, leading to leftover state from previous tests.
  - **Pitfall 4**: Forgetting to set the TaskManager's `jobManagerURL` to the new JobManager's actor path after restart.
  - **Pitfall 5**: Relying on `expectMsg` instead of `expectMsgClass` — the former matches any message and can produce false positives if other messages arrive.

**Correct example** (pseudo-code):
```java
new JavaTestKit(javaSystem) {{
    // Step 1: Register initial JM
    // ... start JobManager, start TaskManager ...

    // Step 2: Kill JM
    // ... stop JobManager actor ...

    // Step 3: Start new JM
    // ... start new JobManager actor ...

    // Step 4: Verify TM re-registers
    expectMsgClass(Duration.ofSeconds(5), RegistrationMessages.RegisterTaskManager.class);
}};
```

**Incorrect example** (pitfall):
```java
// BAD: Only checks initial registration, not reconnection after failure
new JavaTestKit(javaSystem) {{
    // start JobManager, start TaskManager
    expectMsgClass(RegistrationMessages.RegisterTaskManager.class); // passes initially
    // never tests JM failure -> TM reconnection
}};
```

**Incorrect example 2** (pitfall):
```java
// BAD: Uses wrong message type — expecting Ack when TM sends RegisterTaskManager
new JavaTestKit(javaSystem) {{
    // kill JM, start new JM
    expectMsgClass(RegistrationMessages.Acknowledge.class); // wrong! TM sends RegisterTaskManager first
}};
```
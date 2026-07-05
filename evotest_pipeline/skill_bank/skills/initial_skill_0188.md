---
name: vm-queue-reference-count-multiple-consumers
description: When testing VmEndpoint with multiple consumers on remote routes, the
  test should verify that each consumer independently receives all messages, using
  mock endpoints with accurate counts to prevent timeout failures.
code_tags:
- STATE_MUTATION
- CONCURRENCY
test_pattern: STATE_TEST
---

# vm-queue-reference-count-multiple-consumers

## Instructions

# VM Queue Reference Count with Multiple Consumers

## Instructions

- WHEN the TG encounters a test that uses `VmEndpoint` with multiple consumers on a remote route (e.g., `vm:foo?multipleConsumers=true`)
- THEN the test should create at least two routes that consume from the same VM endpoint, plus a producer route that sends a known number of messages, and use separate `MockEndpoint` instances to verify that each consumer receives the correct count of messages independently.
- The test must configure the mock endpoints with `expectedMessageCount(int)` set to the total number of messages sent by the producer (not a subset), because with `multipleConsumers=true` each consumer receives every message independently.
- The test should call `assertMockEndpointsSatisfied()` with a reasonable timeout (e.g., 30 seconds via `assertMockEndpointsSatisfied(30000L)`) to avoid premature timeout failures caused by asynchronous queue processing.

### Concrete example (correct approach):
```java
// Correct: Each consumer expects the full message count
MockEndpoint mock1 = getMockEndpoint("mock:route1");
MockEndpoint mock2 = getMockEndpoint("mock:route2");
mock1.expectedMessageCount(10);
mock2.expectedMessageCount(10);

template.sendBody("vm:foo", "message");
// ... send 9 more times

assertMockEndpointsSatisfied(30000L);
```

### Common pitfalls to avoid:
- ❌ Setting different expected counts on each mock endpoint (e.g., `mock1.expectedMessageCount(5)` and `mock2.expectedMessageCount(5)` when sending 10 messages total) — this will cause a timeout since each consumer with `multipleConsumers=true` gets all 10 messages.
- ❌ Not specifying a timeout in `assertMockEndpointsSatisfied()` or using too short a timeout — the default timeout may be insufficient for async queue processing, especially under load.
- ❌ Forgetting that `multipleConsumers=true` means each consumer independently receives every message sent to the VM endpoint, unlike a competing-consumers pattern where messages are distributed among consumers.
- ❌ Using `mock:route1` and `mock:route2` endpoints where the route names differ from the mock endpoint URIs — ensure the route `.to()` matches the mock URI exactly.
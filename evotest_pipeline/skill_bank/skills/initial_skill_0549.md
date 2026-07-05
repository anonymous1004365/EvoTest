---
name: stream-iteration-watermark-propagation
description: When a StreamIterationHead operator forwards watermarks, it must not
  mutate the original watermark object since the downstream head operator already
  emitted it. Use this skill to test watermark emission after iteration in streaming
  dataflows.
code_tags:
- STATE_MUTATION
test_pattern: STATE_TEST
---

# stream-iteration-watermark-propagation

## Instructions

# Stream Iteration Watermark Emission After Polling

## Instructions

- WHEN the TG encounters code that handles watermark forwarding in streaming iteration operators (specifically `StreamIterationHead` or similar iteration head/sink operators that poll data from a blocking queue or iteration broker and forward watermarks)
- THEN the TG should write a test that:
  1. Sets up a `StreamIterationHead` operator with a `OneInputStreamOperator` (or head task)
  2. Injects a watermark into the iteration head via the `processWatermark` method
  3. Configures the operator with `isSerializingTimestamps()` returning `true` (e.g., by using `OperatorConfig...setAutoWatermarkInterval(0)` and setting `ExecutionConfig.enableAutoWatermarkGeneration()` or similar necessary configuration)
  4. Verifies that the watermark is properly emitted (collected) by the downstream output collector
  5. Specifically tests that a watermark with value X is emitted after polling — the bug causes the watermark to be dropped (expected: watermark emitted, actual: 0 emitted)

- **Common pitfalls:**
  - Not setting `isSerializingTimestamps()` to return `true`, which disables the code path that forwards watermarks during polling
  - Testing only the basic `StreamIterationHead.processWatermark()` signature without simulating the polling loop (`run()` method or head polling mechanism) — the bug manifests specifically when watermarks are forwarded *after* polling elements from the iteration queue
  - Not checking the actual watermark value emitted to the output collector — the bug causes watermarks to be lost entirely (value 0 instead of the expected watermark value)
  - Writing tests that merely check watermark object presence without verifying the watermark value reaches downstream operators

- **Example of correct approach:**
  ```java
  // Set up iteration head with timestamp serialization enabled
  StreamIterationHead head = new StreamIterationHead();
  // ... configure to enable isSerializingTimestamps()
  // Inject into the run/process loop
  head.processWatermark(new Watermark(42L));
  // Verify the watermark is emitted to the output
  assertEquals(1, output.getWatermarks().size());
  assertEquals(new Watermark(42L), output.getWatermarks().get(0));
  ```

- **Example of incorrect approach (too narrow):**
  ```java
  // BUGGY TEST: Only tests processWatermark() directly, missing the poll loop behavior
  StreamIterationHead head = new StreamIterationHead();
  head.processWatermark(new Watermark(42L));
  // The bug is only triggered during the iteration polling loop
  ```
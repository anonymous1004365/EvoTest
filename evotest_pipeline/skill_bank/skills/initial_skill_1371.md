---
name: watermark-forwarding-without-timestamps
description: When a CEP operator processes elements without timestamps, the watermark
  forwarding must handle the case where no timestamp has been assigned. This skill
  teaches the TG to test watermark forwarding in the absence of element timestamps
  and verify no NullPointerException occurs.
code_tags:
- NULL_CHECK
- VALIDATION
- STATE_MUTATION
- ORDER_DEPENDENCY
test_pattern: STATE_TEST
---

# watermark-forwarding-without-timestamps

## Instructions

# CEP Operator Watermark Forwarding Without Timestamps

## Instructions

- WHEN the TG encounters code that processes elements through a CEP operator (such as `AbstractCEPPatternOperator`, `CEPPatternOperator`, or `KeyedCEPPatternOperator`) and the test invokes `processElement` on events that have no assigned timestamp (`TimestampedValue` with `timestamp` field set to `Long.MIN_VALUE` or similar sentinel)
- THEN the TG should additionally verify that watermark forwarding (`processWatermark`) works correctly after processing such timestamp-less elements
- Specifically, the test should:
  1. Create events without timestamps (e.g., `new StreamRecord<>(event)` or `new StreamRecord<>(event, Long.MIN_VALUE)`)
  2. Call `processElement` with these events
  3. Call `processWatermark` with a valid watermark value (e.g., `new Watermark(2)`)
  4. Verify that no `NullPointerException` is thrown during watermark processing, and that the watermark is correctly forwarded (e.g., using `TestHarness.getOutput()` to check for the forwarded `Watermark`)
- Common pitfall: Testing only with timestamped records and assuming watermark forwarding works the same way — the bug is that the watermark forwarding code may assume a shared timestamp state is always initialized by `processElement`, which fails when processing timestamp-less elements
- Correct example:
```java
// Test watermarks after processing elements without timestamps
CEPOperatorTestHarness<...> harness = ...;
// Process an element without proper timestamp
harness.processElement(new StreamRecord<>(new SubEvent(40, "b", 1.0), Long.MIN_VALUE));
// Now advance watermark — this should NOT throw NullPointerException
harness.processWatermark(2);
// Verify watermark is forwarded
Watermark expectedWatermark = new Watermark(2);
assertThat(harness.getOutput(), contains(expectedWatermark));
```
- Incorrect example (does not catch the bug):
```java
// Only testing with timestamped elements — may miss the watermark forwarding NPE
harness.processElement(new StreamRecord<>(new SubEvent(40, "b", 1.0), 1000L));
harness.processWatermark(2);
// But the code only crashes when processing timestamp-less elements first
```
---
name: aggregate-send-empty-message-idle-batch
description: When testing batch consumers (like File, S3, APNS) that use sendEmptyMessageWhenIdle=true
  with an aggregator using completionFromBatchConsumer=true, the TG should verify
  that idle empty messages are propagated through the aggregation pipeline to the
  mock endpoint, not silently dropped. The test must ensure the aggregator receives
  and processes the empty message produced by the batch consumer during idle polling.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- VALIDATION
test_pattern: INTERACTION_TEST
---

# aggregate-send-empty-message-idle-batch

## Instructions

# Aggregate Batch Consumer Send Empty Message When Idle

## Instructions

- WHEN the TG encounters a test that combines a batch consumer (e.g., File, S3, APNS) with `sendEmptyMessageWhenIdle=true` AND an aggregator with `completionFromBatchConsumer=true` AND expects a final result at a mock endpoint
- THEN the TG should verify the entire chain from idle polling to aggregation to mock endpoint
  - Specifically: a polling event that yields no results (empty/notifyExchanges) should produce an empty message (via `sendEmptyMessageWhenIdle`)
  - That empty message should be delivered to the aggregator
  - The aggregator should propagate it (via `completionFromBatchConsumer`) to the output mock endpoint
  - Verify by asserting `mock.assertIsSatisfied()` with an expected message count ≥ 1
- Include concrete values: use `sendEmptyMessageWhenIdle=true` in the consumer URI and `completionFromBatchConsumer=true` in the aggregate definition
- Common mistakes to avoid:
  - Testing only the consumer side (e.g., only verifying the consumer produces an empty message) without checking the aggregator can handle it
  - Adding a `aggregationStrategy` that silently drops the empty message (null body) rather than propagating it
  - Omitting `sendEmptyMessageWhenIdle=true` from the consumer URI configuration
  - Not setting `completionFromBatchConsumer=true` on the aggregator
  - Writing the test without `mock.expectedMessageCount(1)` and `mock.assertIsSatisfied()` to catch missing propagation

### Correct Example (from the actual test)
```java
// Given: a route using File consumer (or similar batch consumer) with sendEmptyMessageWhenIdle=true
//        connected to an aggregator with completionFromBatchConsumer=true
// Then: on idle polling, an empty message is produced and MUST reach the mock endpoint
context.start();
mock.assertIsSatisfied(); // expect at least 1 message received at mock
```

### Incorrect Example
```java
// BUG: Testing the aggregator without the idle empty message scenario
// or using an aggregationStrategy that returns null for empty exchanges
context.start();
mock.assertIsSatisfied(); // fails with "Received message count 0, expected at least 1"
```
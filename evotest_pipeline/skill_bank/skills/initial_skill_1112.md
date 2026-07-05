---
name: stream-resequencer-reject-out-of-sequence
description: This skill teaches how to test stream resequencers for correct rejection
  of out-of-sequence messages when capacity limits are reached. Use when testing batch
  resequencing engines that buffer, sort, and release messages based on sequence order
  and capacity thresholds.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- NULL_CHECK
- STATE_MUTATION
- ORDER_DEPENDENCY
test_pattern: STATE_TEST
---

# stream-resequencer-reject-out-of-sequence

## Instructions

# Stream Resequencer: Reject Out-of-Sequence Messages After Capacity Reached

## Instructions

- WHEN the TG encounters a `ResequencerEngine` (or similar batch resequencer) that buffers incoming messages, sorts them by sequence number, and releases them in order (e.g., `ResequencerEngine.capacity` defines the buffer size), and the engine supports a rejection policy (e.g., `isOldExchangeUuid()` checking whether a message's sequence ID is older than already-released messages)
- THEN the TG should write a state-based test that:
  1. Creates a resequencer with a small `capacity` (e.g., `capacity=5`) so the buffer fills quickly
  2. Sends messages with a **strictly increasing but incomplete sequence** (e.g., B, C, D, E, F) — these fill the buffer to capacity but none are released because gaps remain
  3. Then sends a message with a **lower sequence number** than what is expected next (e.g., message A after B,C,D,E,F have been sent) — this simulates an out-of-sequence "old" message that should be rejected
  4. Verifies that the out-of-sequence old message triggers a `MessageRejectedException` and is NOT delivered to the output
  5. Verifies that messages already buffered (B through F) remain in the buffer awaiting their turn and are NOT corrupted or lost
  6. The test should call the sender/release logic exactly as in production (e.g., `resequencer.send(sequence, exchange)` and `resequencer.release(exchange)`)

- **Common pitfalls:**
  - Testing only with a linear sequence (e.g., A, B, C, D, E, F) — this won't trigger the capacity+out-of-sequence condition
  - Testing rejection only when buffer is NOT full (e.g., capacity=10, only 2 elements sent, then an older element) — this would pass on the buggy version because the bug only manifests at capacity boundary
  - Not verifying that the resequencer's internal state remains consistent after a rejected message (e.g., the next expected sequence number should still be the same)
  - Forgetting to test `isOldExchangeUuid()` logic specifically — the bug is that an old exchange is NOT rejected when the capacity buffer is full and its turn hasn't come yet, causing it to skip ahead in the output order

- **Correct example (what to do):**
  ```java
  // Arrange: create resequencer with small capacity = 5
  ResequencerEngine<String> resequencer = createResequencer(comparator, 5);
  resequencer.setSequenceComparator(comparator);
  // register handler that throws on rejection
  resequencer.setHandler(new DefaultResequencerErrorHandler() { ... });
  
  // Act: fill buffer with 5 messages but leave a gap (skip A)
  resequencer.send("B", exchangeB);
  resequencer.send("C", exchangeC);
  resequencer.send("D", exchangeD);
  resequencer.send("E", exchangeE);
  resequencer.send("F", exchangeF);
  // Buffer is full, none released because A is missing
  // Now send message A (older than what's buffered)
  assertThrows(MessageRejectedException.class, () -> {
      resequencer.send("A", exchangeA);
  });
  // Assert: exchangeA should NOT be delivered
  ```

- **Incorrect example (what to avoid):**
  ```java
  // Only tests rejection when buffer is not full — won't catch the bug
  ResequencerEngine<String> resequencer = createResequencer(comparator, 10);
  resequencer.send("B", exchangeB);
  resequencer.send("A", exchangeA); // This triggers rejection but not via capacity path
  assertThrows(MessageRejectedException.class, () -> {
      resequencer.send("A", exchangeA);
  });
  // This test passes on both buggy and fixed versions — useless
  ```
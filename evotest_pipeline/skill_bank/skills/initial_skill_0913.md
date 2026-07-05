---
name: session-window-count-trigger-collision
description: When session windows are combined with CountTrigger, overlapping session
  windows that merge can produce incorrect aggregated results because the count-based
  firing/eviction logic does not account for merged state. Use this skill to write
  tests that detect incorrect aggregations.
code_tags:
- NULL_CHECK
- VALIDATION
- TYPE_CONVERSION
- STATE_MUTATION
test_pattern: STATE_TEST
---

# session-window-count-trigger-collision

## Instructions

# Session Window + CountTrigger Collision

## Instructions

- WHEN the TG encounters a `WindowOperator` that uses `SessionWindowTimeGapExtractor` (or fixed-size session gaps like `ProcessingTimeSessionWindows.withGap()`) combined with a `CountTrigger` (e.g., `CountTrigger.of(3)`) on a `MergingWindowSet`
- THEN the TG should write a test that:
  1. Creates a `WindowOperator` with session windows AND a `CountTrigger` (not a `ProcessingTimeTrigger` or `EventTimeTrigger`)
  2. Pushes multiple events for the **same key** with timestamps that cause **overlapping session windows to merge** — i.e., the gap between consecutive events is smaller than the session gap
  3. **Verifies the count of elements in the window after firing** — specifically, the test should assert that after a full merge (session gap closes between two groups of events), the emitted result contains the **total aggregate of ALL events** that belong to the merged window, not just a subset
  4. Uses a `ListStateDescriptor` with a `SumAggregate` or custom `AggregateFunction` and a `PassThroughWindowFunction`
- Concrete example: send 3 elements with timestamps 0, 1, 2 (session gap 5000ms) AND 2 more elements with timestamps 3, 4 (same key) — then **verify the final output after session gap passes** contains the aggregation of all 5 elements (value = sum of all fields), not just the first 3 that triggered the `CountTrigger`

- Common pitfalls to avoid:
  - ❌ Testing only one burst of events where `CountTrigger` fires without any session merging — this passes on buggy code
  - ❌ Testing only session windows with `ProcessingTimeTrigger` or `EventTimeTrigger` — the bug is specific to `CountTrigger` interaction
  - ❌ Using different keys for each event — the bug requires **same key** so windows merge
  - ❌ Expecting exactly 2 windows instead of 1 merged window — account for session merging behavior
  - ❌ **Forgetting to wait for the session gap to elapse** so the merged window actually fires — without advancing time past the gap, no output is produced

- Correct test approach:
  ```java
  // Set up WindowOperator with session windows (gap=5000ms) and CountTrigger.of(3)
  // Send 5 events for same key with timestamps 0, 1, 2, 1000, 1001
  // First 3 events cause CountTrigger to fire (partial window)
  // Events at 1000 and 1001 merge with first window since gap=5000ms > 1001-0
  // After advancing watermark past 6000, expect ONE result with count=5 (sum of all 5 values)
  ```

- Incorrect test approach (would not catch the bug):
  ```java
  // Set up with EventTimeTrigger instead of CountTrigger
  // Send 3 events for same key — this works correctly on both buggy and fixed
  ```
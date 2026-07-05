---
name: multi-source-combiner-state-reset
description: When a Combiner iterator has multiple sources and one source gets deleted,
  the state (topKey, topValue, kvs) may not be properly reset for the remaining sources,
  leading to stale values being combined. Use this skill to test that the Combiner
  correctly handles source deletions and resumes combining fresh.
code_tags:
- STATE_MUTATION
- EDGE_CASE_INPUT
- ORDER_DEPENDENCY
test_pattern: STATE_TEST
---

# multi-source-combiner-state-reset

## Instructions

# Multi-Source Combiner State Reset After Source Deletion

## Instructions

- WHEN the TG encounters a `Combiner` that iterates over multiple `SortedKeyValueIterator` sources and calls `findTop()` to locate the top key across sources
- THEN the TG should verify that when one source is deleted (its top key removed), the Combiner correctly resets its internal state (`topKey`, `topValue`, `kvs`) and re-evaluates remaining sources — it should NOT continue to use stale values from the deleted source
- The test should set up at least two sources with overlapping keys, combine all columns, delete a key from one source via `source.seek()` with a `Range` that skips it, call `next()`, and verify that values from the deleted source are no longer included in the combined result
- Expect that the buggy behavior combines stale values (e.g., adding values from a deleted source that should no longer contribute), producing an incorrect aggregated result like sum or max
- Common pitfalls: 
  - Testing only a single source (the bug only manifests with multiple sources)
  - Testing only the happy path where no sources are deleted
  - Testing deletion via `remove()` instead of simulating a delete via `seek()` to a range that excludes the deleted key
  - Not calling `next()` on the Combiner after the delete to trigger state recalculation

### Example (Correct Test Approach)

```java
// Setup: two sources with the same key "a" having values 5 and 4
// combineAllColumns = true, combiner = summing
iterator.next(); // first call combines 5+4=9, topValue=9
// Now simulate deleting value 5 from source1 by seeking it past "a"
source1.seek(new Range("b", true, null, true), ...);
iterator.next(); // BUG: still combines stale value 5 with fresh value 4 => 9 instead of 4
// Expected (fixed): topValue should be 4 (only remaining source)
// Actual (buggy): topValue is 9 (stale 5 + fresh 4)
```

### Example (Incorrect Test — Misses the Bug)

```java
// Only one source — will never trigger the stale-state bug
iterator.next(); // combines 5+4=9, topValue=9 (correct for both versions)
source.seek(...);
iterator.next(); // works fine with single source
// This test passes on both buggy and fixed — useless for catching the bug
```
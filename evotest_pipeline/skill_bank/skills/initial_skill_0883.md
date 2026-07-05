---
name: compaction-map-consistency
description: When testing state-mutating data structures like compaction maps, generate
  and verify specific keys after compaction and force the removal of individual records,
  then check that removed keys are indeed absent from the final map.
code_tags:
- STATE_MUTATION
test_pattern: STATE_TEST
---

# compaction-map-consistency

## Instructions

# Compaction Map Key Consistency

## Instructions

- WHEN the TG encounters a compaction map or similar state container (e.g., `Map<RecordId, RecordId> compactionMap`) that is populated during segment compaction,
- THEN the TG should write a test that:
  1. **Creates a fixed set of entries** in the map by generating deterministic keys (e.g., using `new RecordId(...)` with known segment IDs and record numbers).
  2. **Compacts the map** by invoking the compaction method that processes entries.
  3. **Removes a specific entry from the map** (e.g., by calling a method like `remove(key)`).
  4. **Verifies the removed key is absent** — asserts that `compactionMap.containsKey(removedKey)` returns `false`.
  - Use `assertEquals(false, compactionMap.containsKey(removedKey))` or `assertNull(compactionMap.get(removedKey))`.
  - The test should fail on the buggy version (where `containsKey` incorrectly returns `true`) and pass on the fixed version.

- **Common pitfalls to avoid:**
  - Do NOT only test the size of the map after removal — a size check may not reveal that a stale mapping still exists.
  - Do NOT rely solely on `map.remove(key)` returning the previous value — the bug is in `containsKey`, not in the return value of `remove`.
  - Do NOT forget to call the compaction process before the removal — the bug only manifests after entries have been written during compaction.
  - Do NOT use the same key type for all tests — ensure both the record ID types used (e.g. `SegmentId`, `RecordId`) are correctly compared.

- **Correct example (detects the bug):**
  ```java
  // Given a compactionMap (Map<RecordId, RecordId>)
  RecordId key = new RecordId(segmentId1, 10);
  compactionMap.put(key, new RecordId(segmentId2, 20));
  // ... compaction runs ...
  compactionMap.remove(key);
  assertFalse("Compaction map must not contain removed key", compactionMap.containsKey(key));
  ```

- **Incorrect example (misses the bug):**
  ```java
  compactionMap.put(key, value);
  compactionMap.remove(key);
  assertEquals(0, compactionMap.size()); // This might pass even with the bug
  ```
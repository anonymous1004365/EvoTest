---
name: list-record-iteration-boundary
description: When testing multi-level list data structures with recursive getEntries/getEntry
  calls, test boundary sizes like LEVEL_SIZE and LEVEL_SIZE * LEVEL_SIZE + 1 to catch
  bucket size calculation errors that cause IllegalArgumentException during iteration.
code_tags:
- NULL_CHECK
- RESOURCE_MANAGEMENT
- VALIDATION
test_pattern: EXCEPTION_TEST
---

# list-record-iteration-boundary

## Instructions

# ListRecord Iteration Boundary Test

## Instructions

- WHEN the TG encounters a `ListRecord` (or similar multi-level list data structure) that uses a `bucketSize` calculated from a `size` parameter with a `LEVEL_SIZE` constant, where the list can span multiple levels when `size > LEVEL_SIZE`
- THEN the TG should test iteration via `getEntries()` or similar bulk retrieval methods with sizes that are exactly at key boundaries: `LEVEL_SIZE` (full first level), `LEVEL_SIZE + 1` (one item over the first level bound), `LEVEL_SIZE * LEVEL_SIZE` (full two-level tree), and `LEVEL_SIZE * LEVEL_SIZE + 1` (one item over the two-level bound)
- The test should iterate ALL entries returned by `getEntries()` and verify each entry matches the expected value AND matches `getEntry(i)` at the same index. Catch any `IllegalArgumentException` thrown during iteration and fail the test with a descriptive marker like `fail("OAK-1287")`
- **Common pitfall**: Only testing with small sizes (e.g., size=1) or sizes that exactly match `LEVEL_SIZE` powers — this misses bugs in the recursive bucket traversal when `bucketSize` doesn't evenly divide the total size and the `size - bucketIndex * bucketSize` calculation produces values that cause `getEntry()` in deeper buckets to go out of bounds
- The bug occurs because the `bucketSize` computation uses `while (bs * LEVEL_SIZE < size)` (strict less-than), so for `size = LEVEL_SIZE * LEVEL_SIZE + 1`, the bucketSize becomes `LEVEL_SIZE` instead of `LEVEL_SIZE * LEVEL_SIZE`, creating a two-level tree where intermediate bucket sizes may not match expectations

### Correct test approach (example from RecordTest):
```java
ListRecord level2p = writeList(LEVEL_SIZE * LEVEL_SIZE + 1, blockId);
try {
    int count = 0;
    for (RecordId entry : level2p.getEntries()) {
        assertEquals(blockId, entry);
        assertEquals(blockId, level2p.getEntry(count));
        count++;
    }
    assertEquals(LEVEL_SIZE * LEVEL_SIZE + 1, count);
} catch (IllegalArgumentException e) {
    fail("OAK-1287");
}
```

### Incorrect test approach (doesn't catch the bug):
```java
// Only testing getEntry() individually doesn't expose the recursive bucket traversal bug
ListRecord level2p = writeList(LEVEL_SIZE * LEVEL_SIZE + 1, blockId);
assertEquals(blockId, level2p.getEntry(0));
assertEquals(blockId, level2p.getEntry(LEVEL_SIZE * LEVEL_SIZE));
// Missing: iterating through ALL entries via getEntries()
```
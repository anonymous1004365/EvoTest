---
name: filter-deleted-key-handling
description: WHEN an iterator or filter skips entries based on key properties (like
  isDeleted()), THEN the test should verify behavior with deleted keys to ensure filtering
  logic correctly handles them and does not skip non-deleted entries that share certain
  characteristics with deleted ones.
code_tags:
- VALIDATION
- STATE_MUTATION
test_pattern: STATE_TEST
---

# filter-deleted-key-handling

## Instructions

# Filter Deleted Key Handling

## Instructions

WHEN the TG encounters an `org.apache.accumulo.core.iterators.Filter` subclass (or similar iterator pattern) that calls `source.getTopKey().isDeleted()` as part of its filtering/skipping logic in a `findTop()` method,

THEN the TG should write a test that creates `Key` objects with and without the delete flag set, and verifies that:

1. A `Key` with the delete flag set (e.g. `key.setDeleted(true)`) is correctly skipped by the filter.
2. A `Key` without the delete flag but otherwise identical content (same row, column family, column qualifier, timestamp) is NOT skipped by the filter.
3. The filter correctly passes through keys that should be accepted (or rejected based on negate mode) regardless of their deleted status.
4. Use `Key.setDeleted(true)` to mark a key as deleted.
5. Use `assertEquals(expectedCount, actualCount)` to assert the number of entries returned by the iterator after seeking.

For the test fixture:
- Use `SortedMapIterator` as the source, populated with `TreeMap<Key, Value>`.
- Use `new Range()` for the full range and `EMPTY_COL_FAMS` (empty `Collection<ByteSequence>`) with `false` for the column families parameter when seeking.
- Iterate using `hasTop()` and `next()` to count results.

Common pitfalls to avoid:
- Testing only non-deleted keys and assuming deleted-key behavior is the same.
- Forgetting that `Key.setDeleted(true)` marks the key as a delete tombstone.
- Testing with keys that differ in multiple dimensions (row, colf, colq, timestamp) alongside the delete flag, which makes it hard to isolate the delete-flag effect.
- Not testing both the "accept" and "reject" paths (e.g. not testing a filter with `negate=false` and `negate=true`).

**Correct example:**
```java
// Test that deleted keys are properly filtered out
@Test
public void testDeletedKeys() throws IOException {
  TreeMap<Key,Value> tm = new TreeMap<>();
  Key liveKey = new Key(new Text("row1"), new Text("cf"), new Text("cq"), 100L);
  Key deletedKey = new Key(new Text("row2"), new Text("cf"), new Text("cq"), 100L);
  deletedKey.setDeleted(true);
  tm.put(liveKey, new Value("live".getBytes()));
  tm.put(deletedKey, new Value("deleted".getBytes()));

  Filter filter = new SimpleFilter(); // assumes SimpleFilter returns true for all
  filter.init(new SortedMapIterator(tm), EMPTY_OPTS, null);
  filter.seek(new Range(), EMPTY_COL_FAMS, false);
  
  assertEquals("Expected only live key, deleted key should be skipped", 1, countResults(filter));
}
```

**Incorrect example:**
```java
// WRONG: Only tests with non-deleted keys, assumes behavior is the same
@Test
public void testDeletedKeys() throws IOException {
  TreeMap<Key,Value> tm = new TreeMap<>();
  Key k = new Key(new Text("row1"), new Text("cf"), new Text("cq"));
  tm.put(k, new Value("test".getBytes()));

  Filter filter = new SimpleFilter();
  filter.init(new SortedMapIterator(tm), EMPTY_OPTS, null);
  filter.seek(new Range(), EMPTY_COL_FAMS, false);
  
  // This test never exercises the deleted-key code path
  assertEquals(1, countResults(filter));
}
```
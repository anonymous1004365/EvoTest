---
name: lane-selection-order-in-path-iterator
description: When a method selects a lane (bucket) based on content and iterates entries,
  test that the iteration order and lane selection logic correctly partition entries.
  This skill is applicable when you see PathIterator or similar multi-lane iteration
  with skip/take logic.
code_tags:
- RESOURCE_MANAGEMENT
- STATE_MUTATION
- ORDER_DEPENDENCY
test_pattern: STATE_TEST
---

# lane-selection-order-in-path-iterator

## Instructions

# Lane Selection Order in PathIterator

## Instructions

### WHEN the TG encounters:
- A `PathIterator` (or similar multi-lane iterator) that selects a "lane" based on a hash of a property value (e.g., `string.hashCode() & Integer.MAX_VALUE` modulo number of lanes) and only iterates entries belonging to that specific lane
- The lane selection determines which entries are returned and which are skipped
- The iterator is used by a `getNext`-style method that repeatedly calls it

### THEN the TG should:
1. **Verify that lane selection correctly partitions entries by content**, not by some other property like iteration index or entry order
2. **Insert entries in an interleaved order** (e.g., lane-0 entry, lane-1 entry, lane-0 entry) to ensure the iterator does not skip or include entries based on their position in the store
3. **Assert that only entries matching the selected lane are returned** — specifically, for lane `k`, only entries whose hash modulo lane count equals `k` should appear
4. **Assert that entries from non-matching lanes are correctly filtered out** (not returned at all)
5. **Assert that all matching entries are returned** (none are skipped)
6. **Expect an assertion error on the buggy version** if the iterator incorrectly matches entries (e.g., by index position instead of content hash)

### Common pitfalls to avoid:
- ❌ Inserting only entries from a single lane — this masks bugs where lane filtering doesn't work correctly
- ❌ Inserting entries in sequential order (all lane-0, then all lane-1) — this may pass a buggy implementation that uses insertion index instead of content hash
- ❌ Only testing that some entries are returned without checking that **all** matching entries are returned
- ❌ Not testing the exact set of expected entries against actual results

### Example (correct):
```java
// Interleave entries from different lanes
// "aaa" hashes to lane 0 with 2 lanes
store.put("aaa_key1", "val1");  // lane 0
store.put("bbb_key2", "val2");  // lane 1
store.put("aaa_key3", "val3");  // lane 0

PathIterator it = new PathIterator(filter, "indexName", pathPrefix, prependPathPrefix);
List<String> results = new ArrayList<>();
while (it.hasNext()) {
    results.add(it.next());
}
// Only lane-0 entries should be returned
assertEquals(Arrays.asList("val1", "val3"), results);
```

### Example (incorrect — may not catch the bug):
```java
// All entries from same lane — doesn't test lane filtering
store.put("aaa_key1", "val1");  // lane 0
store.put("aaa_key2", "val2");  // lane 0
store.put("aaa_key3", "val3");  // lane 0

PathIterator it = new PathIterator(filter, "indexName", pathPrefix, prependPathPrefix);
List<String> results = new ArrayList<>();
while (it.hasNext()) {
    results.add(it.next());
}
assertEquals(3, results.size()); // Buggy version would also pass this!
```
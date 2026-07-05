---
name: content-mirror-store-lane-iteration
description: When iterating through indexed property values stored in a multi-lane
  content mirror structure, the test should verify that each lane's entries are correctly
  traversed in order and that the last lane is properly returned, not skipped. Apply
  this skill when testing multi-lane ordered iteration over property index entries.
code_tags:
- EMPTY_INDEX_HANDLING
- STATE_MUTATION
test_pattern: PARAMETRIC_TEST
---

# content-mirror-store-lane-iteration

## Instructions

# Content Mirror Store Lane Iteration

## Instructions

WHEN the TG encounters a `ContentMirrorStoreStrategy.getNext()` or similar method that iterates over multiple "lane" indexes (e.g., `getNext(path, index, count)` or `getNext(from, to, index)`) to find the next available entry in a property index:

- THEN the TG should write a test that creates multiple lanes with entries, and verifies that **the highest lane (e.g., lane index 2) with available entries is correctly returned**, not skipped.
- Specifically, when the test sets up entries in lane 0 and lane 2 (but NOT lane 1), calling `getNext` from a key that is before all entries should return the first entry from lane 0, and then the next call should return the entry from lane 2.  
- The test must **verify that the middle lane being empty does NOT prevent iteration from reaching the highest lane**.
- The test should use concrete `String` keys (e.g., `"a"`, `"b"`, `"c"`) and explicitly construct the multi-lane index structure so that lane 0 has some entries, lane 1 is empty, and lane 2 has entries further in sort order.

**Common pitfalls to avoid:**
- Testing only entries in contiguous lanes (e.g., only lanes 0 and 1), which would miss the bug where a gap in lanes causes the last lane to be skipped.
- Assuming `getNext` returns the correct result when the highest occupied lane is not the last occupied lane in the iteration order — the bug manifests when entries exist in lane 0 and lane 2 but lane 1 is missing.
- Using non-deterministic or overly complex setup that obscures the lane structure — prefer a simple, explicit setup like `IndexEntry.of("a", 0, "/a")` for lane 0 and `IndexEntry.of("b", 2, "/b")` for lane 2.

**Correct example (catches the bug):**
```java
@Test
public void getNextWithGapInLanes() throws Exception {
    // Build a multi-lane structure with entries only in lane 0 and lane 2 (lane 1 is missing)
    // This simulates the scenario where lanes were renumbered/compacted
    
    // lane 0 has "a", lane 2 has "d" — lane 1 has nothing
    // getNext starting from before "a" should find "a" then "d"
    
    // Assuming we can construct the internal multi-lane map:
    Map<String, String> map = Maps.newHashMap();
    map.put("a", "/a");        // lane 0
    map.put("d", "/d");        // lane 2 (after compaction/renumbering)
    
    // The test should call getNext(...) and assert the returned entries
    // On buggy version: after returning "a" (from lane 0), getNext would fail to find "d" (from lane 2)
    // On fixed version: both "a" and "d" are correctly returned
}
```

**Incorrect example (misses the bug):**
```java
@Test
public void getNextSimple() throws Exception {
    // Only tests contiguous lanes (0 and 1) — never detects the gap bug
    Map<String, String> map = Maps.newHashMap();
    map.put("a", "/a");        // lane 0
    map.put("b", "/b");        // lane 1
    // This passes on both buggy and fixed versions
}
```
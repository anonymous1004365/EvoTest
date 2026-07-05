---
name: mock-table-sorted-map-ordering
description: When a key comparison implementation in a custom Key subclass violates
  the Comparator contract by returning inconsistent results (e.g., reversed ordering,
  breaking symmetry), the backing SortedMap/ConcurrentSkipListMap becomes corrupted,
  causing entries to disappear. Use this skill to test custom Comparable.compareTo
  methods for consistency.
code_tags:
- ORDER_DEPENDENCY
- STATE_MUTATION
test_pattern: STATE_TEST
---

# mock-table-sorted-map-ordering

## Instructions

# MockTable MockMemKey.compareTo Ordering Consistency

## Instructions

- WHEN the TG encounters a custom Key subclass that overrides `compareTo(Key)` and the backing data structure is a `SortedMap` (e.g., `ConcurrentSkipListMap`), and the purpose is to store multiple Mutations with different ordering based on an extra counter field

- THEN the TG should write a unit test that directly tests the `compareTo` method's compliance with the `Comparator` contract, specifically:
  - **Symmetry**: If `a.compareTo(b) > 0`, then `b.compareTo(a)` must be `< 0` (not also `> 0`)
  - **Transitivity**: If `a.compareTo(b) > 0` and `b.compareTo(c) > 0`, then `a.compareTo(c) > 0`
  - **Consistency with equals**: `a.compareTo(b) == 0` should imply `a.equals(b)` is `true` (for SortedMap correctness)
  - Test with pairs of objects that have equal base Keys but different count values AND test with a normal Key (non-subclass) to ensure asymmetry doesn't occur

- Specifically, for `MockMemKey.compareTo`: test that when `super.compareTo(o) == 0` and `o` is NOT a `MockMemKey`, the method returns `1`. Then test symmetry: if `a` is `MockMemKey` and `b` is a plain `Key` (not MockMemKey), ensure `a.compareTo(b) == 1` and `b.compareTo(a) == -1`.

- Common pitfalls to avoid:
  - Testing only with `MockMemKey` to `MockMemKey` comparisons — the bug involves asymmetry when comparing `MockMemKey` with plain `Key` objects
  - Not testing that `ConcurrentSkipListMap` actually contains the expected number of entries after multiple puts with mixed key types
  - Assuming that `SortedMap` silently handles inconsistent `compareTo` implementations — it does NOT; entries get silently lost or cause unexpected ordering
  - Forgetting that `SortedMap` uses `compareTo` (not `equals`) for identity, so an inconsistent comparator can lose entries permanently

### Correct test example:
```java
@Test
public void testMockMemKeyCompareToSymmetry() {
    Key baseKey = new Key(new Text("row"), new Text("cf"), new Text("cq"), new Text(""), 0, false);
    Key plainKey = new Key(baseKey);
    MockMemKey memKey = new MockMemKey(baseKey, 1);
    
    // MockMemKey vs plain Key
    assertTrue("memKey should be > plainKey when keys are equal", memKey.compareTo(plainKey) > 0);
    // BUT plain Key vs MockMemKey MUST be negative for symmetry
    assertTrue("plainKey should be < memKey for symmetry", plainKey.compareTo(memKey) < 0);
    
    // Two MockMemKeys with different counts
    MockMemKey memKey1 = new MockMemKey(baseKey, 1);
    MockMemKey memKey2 = new MockMemKey(baseKey, 2);
    assertTrue("memKey1 with count=1 should be < memKey2 with count=2", memKey1.compareTo(memKey2) < 0);
    assertTrue("memKey2 should be > memKey1 for symmetry", memKey2.compareTo(memKey1) > 0);
}
```

### Incorrect test (would miss the bug):
```java
@Test
public void testMockMemKeyCompareToWrong() {
    Key baseKey = new Key(new Text("row"), new Text("cf"), new Text("cq"), new Text(""), 0, false);
    MockMemKey memKey1 = new MockMemKey(baseKey, 1);
    MockMemKey memKey2 = new MockMemKey(baseKey, 2);
    // Only testing MockMemKey-to-MockMemKey — this does NOT catch the symmetry bug
    assertTrue(memKey1.compareTo(memKey2) < 0);
    assertTrue(memKey2.compareTo(memKey1) > 0);
    // Missing: what happens when comparing MockMemKey to plain Key!
}
```

### Full integration test (how to exercise the bug via MockTable):
```java
@Test
public void testMockTableUpdate() throws Exception {
    // Create connector and table
    Connector c = new MockConnector("root");
    c.tableOperations().create("test");
    BatchWriter bw = c.createBatchWriter("test", 10000L, 1000L, 4);
    
    // Write initial mutation
    Mutation m1 = new Mutation("r1");
    m1.put("cf1", "cq1", new Value("v1".getBytes()));
    bw.addMutation(m1);
    bw.flush();
    
    // Write update to same row/col
    Mutation m2 = new Mutation("r1");
    m2.put("cf1", "cq1", new Value("v2".getBytes()));
    bw.addMutation(m2);
    bw.close();
    
    // Verify all entries present
    Scanner scanner = c.createScanner("test", Constants.NO_AUTHS);
    int count = 0;
    for (Entry<Key,Value> entry : scanner) {
        count++;
    }
    // Buggy: returns 1 instead of 2 (one entry lost due to compareTo asymmetry)
    assertEquals("Both mutations should be present", 2, count);
}
```
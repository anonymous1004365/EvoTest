---
name: first-entry-per-row-iterator-edge-cases
description: When testing an iterator that filters to show only the first entry per
  row, test with seek ranges that start or end mid-row, ranges with exclusivity flags,
  and ranges that skip the first row. This skill helps catch bugs where the iterator's
  consume() logic or seek() logic fails to properly handle the boundary between rows.
code_tags:
- BOUNDARY_CHECK
test_pattern: STATE_TEST
---

# first-entry-per-row-iterator-edge-cases

## Instructions

# First Entry Per Row Iterator Edge Cases

## Instructions

WHEN the TG encounters an iterator that filters entries to return only the first entry per row (e.g., `FirstEntryInRowIterator` which wraps a `SortedKeyValueIterator` and skips all entries in a row except the first one),

THEN the TG should write state-based tests that:

1. **Test with a seek range whose start key is NOT at the beginning of a row**
   - Create a `Range` whose `startKey` is a specific key somewhere in the middle of a row, with the start key inclusive and exclusive variants
   - Verify that the iterator correctly returns only the first entry of each row that falls within the range, not just the first entry starting from the seek start key
   - Example: if row `000001` has entries at column families 1-99, seek to `newKey(0, 10, 0, 0)` (mid-row) and verify the iterator returns `row 1` (next row) not `row 0`

2. **Test with an exclusive end key that cuts off a row boundary**
   - Create a `Range` whose end key is a specific key, using `false` for `endKeyInclusive`
   - Verify the iterator does NOT return entries at or beyond the exclusive end key
   - Example: `new Range(newKey(1, 1, 3, 6), newKey(3, 3, 3, 6))` (inclusive both ends) vs `new Range(newKey(1, 1, 3, 6), false, newKey(3, 3, 3, 6), false)` (exclusive end) — the latter should skip row 3

3. **Test with both start and end key exclusivity simultaneously**
   - Create a `Range` where both start key is exclusive and end key is exclusive
   - Verify the iterator skips entries at the start boundary and end boundary correctly

4. **Verify that `hasTop()` returns `false` after consuming all expected entries**
   - After iterating through all expected rows within the range, call `hasTop()` and assert it returns `false`

5. **Common pitfalls to avoid:**
   - ❌ Testing only with a default `new Range()` (unbounded range) — this misses seek boundary bugs
   - ❌ Using only inclusive bounds — exclusive bounds trigger different code paths in the `consume()` method
   - ❌ Testing with perfectly row-aligned start keys — the bug manifests when the seek starts mid-row
   - ❌ Not resetting the iterator state between seeks — the `finished` field and `lastRowFound` must be re-initialized on each `seek()` call

### Correct test pattern example:

```java
// Create data with multiple entries per row
TreeMap&lt;Key,Value&gt; tm = new TreeMap&lt;&gt;();
for (int r = 0; r &lt; 5; r++) {
  for (int cf = r; cf &lt; 100; cf++) {
    for (int cq = 3; cq &lt; 6; cq++) {
      put(tm, r, cf, cq, 6, r * cf * cq);
    }
  }
}

FirstEntryInRowIterator fei = new FirstEntryInRowIterator();
fei.init(new SortedMapIterator(tm), EMPTY_MAP, null);

// Seek starting mid-row (startKey at r=0, cf=10, cq=0 — within row 0)
fei.seek(new Range(newKey(0, 10, 0, 0), null), EMPTY_SET, false);
// Should skip row 0 (start key is past the first entry of row 0), return row 1 first
testAndCallNext(fei, 1, 1, 3, 6, 1 * 1 * 3);
testAndCallNext(fei, 2, 2, 3, 6, 2 * 2 * 3);
// ... continue until done
assertFalse(fei.hasTop());
```

### Incorrect test pattern (would miss the bug):

```java
// ❌ Only testing full-range seek with row-aligned start
TreeMap&lt;Key,Value&gt; tm = new TreeMap&lt;&gt;();
put(tm, "r1", "cf1", "cq1", 5, "v1");
put(tm, "r1", "cf1", "cq3", 5, "v2");
put(tm, "r2", "cf1", "cq1", 5, "v3");

FirstEntryInRowIterator fei = new FirstEntryInRowIterator();
fei.init(new SortedMapIterator(tm), EMPTY_MAP, null);
fei.seek(new Range(), EMPTY_SET, false);
testAndCallNext(fei, "r1", "cf1", "cq1", 5, "v1");
testAndCallNext(fei, "r2", "cf1", "cq1", 5, "v3");
assertFalse(fei.hasTop());
// ❌ This test passes on both buggy and fixed — it doesn't exercise the bug
```
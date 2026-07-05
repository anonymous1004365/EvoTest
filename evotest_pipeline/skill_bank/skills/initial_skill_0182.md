---
name: iterator-hasnext-boundary-for-sparse-collection
description: When testing custom iterators over sparse array-backed collections where
  elements may be interleaved with null slots, verify that hasNext() and next() correctly
  handle the boundary between the actual element count and perceived capacity. The
  iterator's hasNext() condition must account for internal null-key gaps, not just
  a raw index-vs-size comparison.
code_tags:
- NULL_CHECK
- STRING_CONVERSION
- EDGE_CASE_INPUT
- STATE_MUTATION
- ARRAY_ITERATION
test_pattern: STATE_TEST
---

# iterator-hasnext-boundary-for-sparse-collection

## Instructions

# Iterator hasNext() Boundary Condition for Sparse Array-Backed Collections

## Instructions

- WHEN the TG encounters a custom collection or map that stores entries in parallel arrays (keys array + values array) where null keys represent empty slots, and the collection provides iterators via `keySet()`, `entrySet()`, or `values()` views
- THEN the TG should test that the iterator's `hasNext()` and `next()` behave correctly when:
  - The collection size is small (e.g. 1) relative to the maximum capacity (e.g. 3)
  - The underlying array has only one non-null key but the iterator tracks a position counter that could incorrectly compare against `size - 1` instead of counting actual remaining non-null entries
  - **Specifically test that after consuming the only element via `iterator.next()`, calling `iterator.next()` again throws `java.util.NoSuchElementException`**

- WHEN the iterator's `hasNext()` implementation uses a condition like `i < size - 1` (where `i` is a positional counter and `size` is the number of entries)
- THEN the TG should recognize this as a potential off-by-one bug: `hasNext()` may return `false` one step too early when `i` increments past the check condition, or the `next()` method can incorrectly advance past valid entries. The TG should test with a MiniMap of capacity > 1 containing exactly 1 entry, iterate through `keySet().iterator()`, `entrySet().iterator()`, and `values().iterator()`, and verify:
  - `hasNext()` returns `true` for the first call
  - `next()` returns the single entry
  - `hasNext()` returns `false` after consuming the entry, not before
  - A subsequent `next()` throws `NoSuchElementException`
  
- Common pitfall: Testing with a full map (size == capacity) or with maps where array indices and iteration order happen to align (e.g., entry at index 0 with size 1 in a capacity-1 map). The bug only manifests when the sparse array's null gaps interact with the `hasNext()` boundary condition — test concretely with a MiniMap of capacity 3 containing exactly 1 entry.

- Example of correct test pattern (MiniMap with capacity 3, one entry):
```java
MiniMap<Object, Object> m = new MiniMap<>(3);
Object FOO = new Object();
Object BAR = new Object();
m.put(FOO, BAR);

// test keySet() iterator
Iterator<?> i = m.keySet().iterator();
assertTrue(i.hasNext());
Object key = i.next();
assertEquals(FOO, key);
assertFalse(i.hasNext());
try {
    i.next();
    fail("Expected i.next() to fail with NoSuchElementException");
} catch (NoSuchElementException e) {
    // expected
}

// test entrySet() iterator identically
Iterator<Map.Entry<Object, Object>> ei = m.entrySet().iterator();
assertTrue(ei.hasNext());
Map.Entry<Object, Object> entry = ei.next();
assertEquals(FOO, entry.getKey());
assertEquals(BAR, entry.getValue());
assertFalse(ei.hasNext());
try {
    ei.next();
    fail("Expected ei.next() to fail with NoSuchElementException");
} catch (NoSuchElementException e) {
    // expected
}

// test values() iterator identically
Iterator<Object> vi = m.values().iterator();
assertTrue(vi.hasNext());
Object value = vi.next();
assertEquals(BAR, value);
assertFalse(vi.hasNext());
try {
    vi.next();
    fail("Expected vi.next() to fail with NoSuchElementException");
} catch (NoSuchElementException e) {
    // expected
}
```

- Example of incorrect (insufficient) test that would miss the bug:
```java
// BAD: Only tests with full map (size == capacity), missing the sparse scenario
MiniMap<Object, Object> m = new MiniMap<>(1);
// ... only one slot, no sparse array issue
```
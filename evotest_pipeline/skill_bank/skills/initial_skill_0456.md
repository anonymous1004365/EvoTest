---
name: deepcopy-state-restoration
description: When testing SortedKeyValueIterator implementations with deepCopy() that
  maintain internal state (like copied iterators with position), verify that the original
  iterator's state is preserved after deepCopy, and exercise the copy independently.
code_tags:
- STATE_MUTATION
test_pattern: STATE_TEST
---

# deepcopy-state-restoration

## Instructions

# DeepCopy State Restoration

## Instructions

WHEN the TG encounters a `SortedKeyValueIterator` implementation that overrides `deepCopy(IteratorEnvironment)` and captures the result as a cast of `super.deepCopy(env)`, e.g. `(GrepIterator) super.deepCopy(env)`, THEN the TG should write a test that:

1. Creates the iterator, advances it past some entries (e.g., via `next()` or `seek()` with a non-minimal range), then calls `deepCopy(null)` on the partially-consumed iterator.
2. Verifies that calling `deepCopy` does NOT alter the internal state of the **original** iterator—the original should continue iterating from where it left off.
3. Exercises the **copy** independently (e.g., seeks it to a different range, calls `next()` on it) to confirm the copy works correctly without corruption.
4. Verifies the correctness of values returned by both the original and the copy after the deepCopy operation.

### Concrete example (GrepIterator)

```java
// Setup
GrepIterator gi = new GrepIterator();
gi.setTerm("xyz");

// Insert test data using SortedMapIterator or similar source
TreeMap<Key,Value> data = new TreeMap<>();
// Add entries: "abc xyz:xyz [] 1 true", "dfh xyz:xyz [] 1 true", etc.
SortedMapIterator smi = new SortedMapIterator(data);
gi.init(smi, null, null);

// Advance past some entries
gi.seek(new Range(), ...);
gi.next(); // advance past first entry

// Deep copy at this point — buggy version lost the position
SortedKeyValueIterator<Key,Value> copy = gi.deepCopy(null);

// Original should still work from current position
assertTrue(gi.hasTop());           // Buggy version returns false
assertEquals(expectedKey, gi.getTopKey());  // Buggy version wrong/empty

// Copy should also work correctly
copy.seek(new Range(...), ...);
assertTrue(copy.hasTop());
```

### Common pitfalls

- **Testing only a freshly initialized iterator**: A freshly initialized iterator may not expose the deepCopy bug. The bug manifests only after the iterator has been partially consumed (called `next()` or `seek()` to a non-trivial range).
- **Not exercising the copy**: Simply calling `deepCopy` and checking that the original still works is not enough. Also call methods on the copy to verify it is fully functional.
- **Assuming deepCopy resets position**: `deepCopy` should create an independent copy at the same logical position. Do not assume the copy starts from the beginning.
- **Testing only one path**: Test both calling `deepCopy` on the initial state (before iteration) AND on a partially consumed iterator (after one or more `next()` calls).

### Incorrect (insufficient) approach

```java
// Only tests deepCopy on a fresh iterator — misses the bug
GrepIterator gi = new GrepIterator();
gi.init(smi, null, null);
SortedKeyValueIterator<Key,Value> copy = gi.deepCopy(null);
// Only checks copy, not original after deepCopy
assertTrue(copy.hasTop());
```

### Correct approach

```java
GrepIterator gi = new GrepIterator();
gi.init(smi, null, null);
gi.seek(new Range(), ...);
gi.next(); // consume first entry — this is where state matters

SortedKeyValueIterator<Key,Value> copy = gi.deepCopy(null);

// Verify original still works
assertTrue("Original should still have data after deepCopy", gi.hasTop());
assertEquals("Expected key after first next", expectedKey, gi.getTopKey());

// Verify copy is functional
copy.next();
assertTrue("Copy should have data", copy.hasTop());
```
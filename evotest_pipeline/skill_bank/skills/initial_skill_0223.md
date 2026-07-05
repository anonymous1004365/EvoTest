---
name: clone-state-consistency
description: When an object is cloned or copied, its internal state (especially collection
  counters or caches) must be properly reset or updated. This skill helps detect bugs
  where clone() leaves stale state that causes iteration/modification inconsistencies.
code_tags:
- ARGUMENT_VALIDATION
- EDGE_CASE_INPUT
- STATE_MUTATION
test_pattern: STATE_TEST
---

# clone-state-consistency

## Instructions

# Clone State Consistency After Mutation

## Instructions

- WHEN the TG encounters a class that implements `clone()` (or has a manual copy/copy-constructor pattern) and also maintains internal collection metadata (e.g., a `List`, `Map`, or counter fields that track collection size, modification count, or index position)
- THEN the TG must write a test that:
  1. Creates an instance of the class
  2. Mutates its internal state (e.g., adds elements to a collection, removes elements, sets a counter)
  3. Clones the instance (calls `clone()` or the copy method)
  4. Mutates the clone further (e.g., adds more elements to the clone's collection)
  5. Iterates or processes the original AND the clone, verifying that their states are independent and internally consistent
  6. Verifies that any shared mutable state (e.g., arrays, ArrayList references) was deep-copied or properly re-initialized in the clone, NOT shared with the original

- The TG must test that operations on the clone do NOT corrupt the original's internal state (e.g., modification counts, size fields, cached hash values, iterator positions)

- Common pitfalls:
  - Testing only shallow field equality (e.g., `assertEquals(original.size(), clone.size())`) without checking **behavioral independence** after mutation
  - Testing clone() in isolation without first mutating the original — the bug may only surface when the original has non-trivial state before cloning
  - Assuming `clone()` on a collection field (e.g., `(ArrayList)list.clone()`) produces a fully independent copy — the elements themselves may still be shared references
  - Not testing iteration over the original after the clone has been modified

**Correct example (catches the bug):**
```java
// Bug: clone() copies a stale reference to internal collection/array 
// that stores per-instance metadata. After clone(), mutated elements added 
// to the clone change the shared underlying array, corrupting the original's state.
OriginalClass original = new OriginalClass();
original.addElement("A");          // populates internal collection
OriginalClass cloned = original.clone(); // buggy: shares internal array
cloned.addElement("B");            // may corrupt original's internal state

// Assert that original's state is consistent and independent
assertEquals(1, original.size());  // buggy: may return 2 due to shared array
Iterator it = original.iterator();
assertTrue(it.hasNext());
assertEquals("A", it.next());
assertFalse(it.hasNext());         // buggy: may throw ConcurrentModificationException 
                                    // or have extra element "B"
```

**Incorrect example (misses the bug):**
```java
// Only checks that clone returns similar values, not independent behavior
OriginalClass original = new OriginalClass();
original.addElement("A");
OriginalClass cloned = original.clone();
assertEquals(original.size(), cloned.size()); // passes but misses bug
cloned.addElement("B");
// Never checks original after clone mutation — bug remains hidden
```
---
name: empty-map-iteration-safety
description: When iterating over a collection that could be empty, test with empty
  collections to catch NPEs or edge cases in the loop logic. Also test with both null
  and non-null elements to verify safe iteration.
code_tags:
- COLLECTION_ITERATION_MODIFICATION
test_pattern: PARAMETRIC_TEST
---

# empty-map-iteration-safety

## Instructions

# Empty Collection Iteration Safety

## Instructions

- WHEN the TG encounters a method that iterates over a collection (via for-each, iterator, or indexed loop) and the collection is passed as a parameter or could be empty/null
- THEN the TG should:
  1. Write a dedicated test case with an **empty collection** (e.g., `Collections.emptyMap()`, `Collections.emptyList()`, `new HashMap<>()`) as input
  2. Verify that the method completes without throwing a **NullPointerException** or **ConcurrentModificationException**
  3. Write a second test case with a **single-element collection** to verify basic iteration works
  4. If the method separates iteration into a helper/abstract method (e.g., `forEach`, `entrySet().iterator()`), also test that helper with an empty collection directly

- Common pitfalls to avoid:
  - ❌ Testing only with non-empty collections (size >= 2 or size >= 1), missing the empty-collection edge case
  - ❌ Assuming the collection is never null — test with null input separately if the API allows it
  - ❌ Only testing with the most common element type (e.g., String) when the method handles generic types — test with the actual generic parameter types used in the codebase

## Example

**Correct test (catches the bug):**
```java
@Test
public void testEmpty() {
    RecordIdMap map = new RecordIdMap();
    // Iterate over the map - must not throw NPE or CME
    for (Map.Entry<RecordId, RecordId> entry : map.entrySet()) {
        // should not reach here
    }
}
```

**Incorrect test (misses the bug):**
```java
@Test
public void testWithEntries() {
    RecordIdMap map = new RecordIdMap();
    map.put(recordId1, recordId2);
    // Only tests populated map, misses empty-iteration edge case
    for (Map.Entry<RecordId, RecordId> entry : map.entrySet()) {
        assertNotNull(entry.getKey());
    }
}
```
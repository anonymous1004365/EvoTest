---
name: map-copy-shared-collection
description: When a method copies a collection (e.g., Map, List) from an input object
  and stores it as a field, the copy may be too shallow — it might only copy the container,
  not the values inside. Use this skill to detect shared mutable state where element
  modifications can leak between objects.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
- ARRAY_INDEX_ACCESS
test_pattern: STATE_TEST
---

# map-copy-shared-collection

## Instructions

# Map Copy Shared Collection Mutation

## Instructions

- WHEN the TG encounters a class that copies a `Map` or `Collection` from an input object into its own field via a constructor or factory method
- THEN it should test that the copy is **deep enough** to prevent mutations to the original object's data from affecting the new object's state
- Specifically, verify that **modifying elements** (e.g., values in a map, items in a list) via the original object does **not** change the data accessible from the new object
- Use the following concrete pattern:
  - Create an original node/object
  - Add structured data to it (e.g., insert properties into a map collection on the original)
  - Create a copy of the original (e.g., via copy constructor `new Node(original)`)
  - **Modify the original** (e.g., remove a property from the original)
  - **Assert** that the copy's data remains unchanged (e.g., assert that the removed property is still present in the copy, with its original size/value)
- **Common pitfalls to avoid:**
  - Testing only modification of the copied object after construction (not testing modification of the **original** after copy)
  - Using shallow copy (e.g., `new HashMap<>(original.getMap())`) for container but not ensuring value objects are immutable or independent
  - Testing only that the copy has the same data initially, without checking that changes to the original don't propagate

### ✅ Correct Example
```java
// Original has a map 'properties' with entries
Node original = new Node();
original.insertProperty("p1", "v1");
Node copy = new Node(original);
original.removeProperty("p1");
assertEquals(1, copy.getProperties().size()); // copy still has the property
```

### ❌ Incorrect Example (would pass buggy code)
```java
Node original = new Node();
original.insertProperty("p1", "v1");
Node copy = new Node(original);
assertEquals(1, copy.getProperties().size()); // only checks initial state, not isolation
copy.removeProperty("p1");
assertEquals(0, copy.getProperties().size()); // only checks copy mutation, not original mutation
```
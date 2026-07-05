---
name: content-mirror-index-property-null-check
description: When an index strategy stores property values that may be null, the TG
  should test that null values are handled correctly without throwing NullPointerException
  or causing incorrect ordering. Use with ContentMirrorStoreStrategy and OrderedContentMirrorStorageStrategy.
code_tags:
- NULL_CHECK
- STATE_MUTATION
- BOUNDARY_CHECK
test_pattern: STATE_TEST
---

# content-mirror-index-property-null-check

## Instructions

# Content Mirror Index Property Null Handling

## Instructions

- WHEN the TG encounters an index strategy that stores property values from child nodes (e.g., `ContentMirrorStoreStrategy`) where the property may not exist on some nodes (returning `null` from `getProperty`),
  - THEN the TG should write a test that:
    1. Creates multiple child nodes under a parent, at least one of which **does not have** the indexed property
    2. For each child, retrieves the property value (which may be `null`) and attempts to use it in sorting/ordering/comparison logic
    3. Verifies that no `NullPointerException` (NPE) or `NullKeyModeViolation` occurs when the property is absent from some nodes
    4. Verifies that the resulting state (e.g., the order of indexed keys) is correct and deterministic
    5. Tests both:
       - All children having the property (happy path)
       - Some children missing the property (null-producing path)
    6. Tests adding a node with the property value AFTER some null-producing nodes have already been added, to verify that `setNext` or equivalent ordering methods handle dynamic additions correctly

- WHEN the TG is testing a `StorageStrategy` (e.g., `OrderedContentMirrorStorageStrategy`) that uses the index location path to store `TRIPLE`-type properties,
  - THEN the TG should verify the behavior of `setNext` or similar ordering methods when the previous/next node reference involves a node whose property value is `null` in the index tree.

- Common pitfalls to avoid:
  - ❌ Testing only the case where all nodes have the property — this misses the null-producing bug
  - ❌ Assuming `getProperty` always returns a non-null value — in content indexing, missing properties return `null`
  - ❌ Not checking for NPE when null is passed to comparison/sorting logic (e.g., `Comparable.compareTo`, `TreeMap`, `SortedSet`)
  - ❌ Not verifying the resulting collection size or order when nulls are involved
  - ❌ Only testing a single node at a time — the bug may only manifest when multiple nodes are added in sequence

### Example (Correct — catches the bug)

```java
@Test
public void testSetNextWithNullPropertyValues() {
    ContentMirrorStoreStrategy strategy = new ContentMirrorStoreStrategy();
    NodeBuilder indexBuilder = /*…*/;
    
    // Add a node WITHOUT the indexed property -> returns null
    NodeBuilder child1 = indexBuilder.child("a");
    // child1 has no "myProp" property
    
    // Add a node WITH the indexed property
    NodeBuilder child2 = indexBuilder.child("b");
    child2.setProperty("myProp", "value1");
    
    // Attempt to set ordering — this may fail with NPE
    // on buggy version if the strategy doesn't guard against null
    String key = strategy.setNext(indexBuilder, "myProp", child1, child2);
    // Should not throw NullPointerException
}
```

### Example (Incorrect — misses the bug)

```java
@Test
public void testSetNext() {
    ContentMirrorStoreStrategy strategy = new ContentMirrorStoreStrategy();
    NodeBuilder indexBuilder = /*…*/;
    
    // Only tests with nodes that ALL have the property
    NodeBuilder child1 = indexBuilder.child("a");
    child1.setProperty("myProp", "value1");
    NodeBuilder child2 = indexBuilder.child("b");
    child2.setProperty("myProp", "value2");
    
    String key = strategy.setNext(indexBuilder, "myProp", child1, child2);
    // This passes even when null values would cause failures
}
```
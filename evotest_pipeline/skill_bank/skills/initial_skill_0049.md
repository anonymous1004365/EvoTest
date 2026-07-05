---
name: collidable-object-filtering
description: WHEN testing object filtering logic that checks collision properties
  via interface implementation, THEN verify that the filter correctly excludes non-collidable
  objects (e.g., those missing a collidable interface) and does not include them in
  the filtered collection. This skill is applicable when a collection of heterogeneous
  objects is filtered based on a type/interface check.
code_tags:
- STATE_MUTATION
- NULL_CHECK
- VALIDATION
test_pattern: STATE_TEST
---

# collidable-object-filtering

## Instructions

# Collidable Object Filtering Validation

## Instructions

- WHEN the TG encounters code that filters a collection of objects based on whether they implement a specific interface (e.g., `ICollidable`) or have a collision-related method/property
- THEN the TG should write a test that:
  1. Creates a collection containing a mix of objects: some that implement the collidable interface and some that do NOT implement it (e.g., plain `Object` instances or objects of a class that only implements a different interface)
  2. Calls the filtering method to collect only the "collidable" objects
  3. Asserts that the resulting collection:
     - Includes all objects that implement the collidable interface
     - Excludes ALL objects that do NOT implement the collidable interface
     - Has a size equal to the number of collidable objects (not including non-collidable ones)
  4. If the filtering is expected to return non-null results, also verify the result is not null before checking its size

- Common pitfalls to avoid:
  - Testing only with collidable objects and not checking that non-collidable objects are excluded (this misses the bug entirely)
  - Assuming the filter will throw an exception for non-collidable objects (the bug is about silent mis-inclusion, not exceptions)
  - Only testing with objects of the same type (the bug manifests when different types are mixed in the input collection)
  - Not checking the count/size of the filtered result (the bug is about wrong count, not missing elements)

## Example (Correct)

```java
@Test
public void testOnlyCollidableObjects() {
    // Create a list with both collidable and non-collidable objects
    List<Object> mixedObjects = new ArrayList<>();
    mixedObjects.add(new CollidableObject());   // implements ICollidable
    mixedObjects.add("not collidable");          // String does not implement ICollidable
    mixedObjects.add(new CollidableObject());   // implements ICollidable
    
    // Call the filtering method
    List<Object> result = detector.getCollidables(mixedObjects);
    
    // Verify only collidable objects are included
    assertNotNull("Result should not be null", result);
    assertEquals("Should contain exactly 2 collidable objects", 2, result.size());
}
```

## Example (Incorrect)

```java
// BAD: Only tests with collidable objects, never checks non-collidable exclusion
@Test
public void testCollidableObjects() {
    List<Object> allCollidable = new ArrayList<>();
    allCollidable.add(new CollidableObject());
    allCollidable.add(new CollidableObject());
    
    List<Object> result = detector.getCollidables(allCollidable);
    
    // This passes on buggy code because the bug is in how NON-collidable items are handled
    assertEquals(2, result.size());
}
```
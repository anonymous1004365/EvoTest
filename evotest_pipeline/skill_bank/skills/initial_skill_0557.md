---
name: comparator-null-collection-handling
description: When implementing equals/comparator methods that compare collections,
  the code may throw NullPointerException when one collection is null and the other
  is empty. TG should test equality between null and empty collections to catch missing
  null-guard logic.
code_tags:
- VALIDATION
- STATE_MUTATION
test_pattern: EXCEPTION_TEST
---

# comparator-null-collection-handling

## Instructions

# Comparator Null Collection Exception Handling

## Instructions

- WHEN the TG encounters a comparator, equals method, or any comparison logic that iterates over two collections/lists, particularly in a class that implements `Comparator` or overrides `equals(Object)`  
- THEN the TG should write a test that creates a scenario where one collection is `null` and the other is an **empty collection** (e.g., `Collections.emptyList()`), and the comparison method is invoked with these as arguments  
  - The test should verify that the comparison method does **not** throw a `NullPointerException` when one side has a null collection and the other has an empty collection  
  - Specifically, the test should assert that the comparison returns a boolean or comparison result without throwing (or if a null guard is intentionally present, the test should document the expected behavior)  
- The test pattern is: create an instance of the class under test, set one collection field to `null`, the other to an empty collection, and call the comparison method (from both perspectives: `a.equals(b)` and `b.equals(a)` if applicable)  
- Common pitfalls to avoid:  
  - ❌ Testing only with two non-null collections or two null collections, missing the asymmetric null vs empty case  
  - ❌ Testing only one direction (e.g., only `a.equals(b)` but not `b.equals(a)`) – the null could be on either side  
  - ❌ Using a non-empty collection on both sides – this misses the bug where the iteration over the non-null empty collection triggers a special code path  
- Correct example:  
  ```java
  // Given: comparator with left.names=null and right.names=empty list
  CtTypeReference left = factory.Type().createReference("LeftType");
  left.setActualTypeArguments(null);
  CtTypeReference right = factory.Type().createReference("RightType");
  right.setActualTypeArguments(Collections.emptyList());
  
  // When comparing
  boolean result = left.equals(right);
  // Then: no NullPointerException should be thrown
  assertTrue(result); // or assertFalse depending on expected behavior
  ```
- Incorrect example (misses the bug):
  ```java
  // Only tests with both non-null collections
  CtTypeReference left = ...;
  left.setActualTypeArguments(Arrays.asList(someType));
  CtTypeReference right = ...;
  right.setActualTypeArguments(Arrays.asList(someType));
  // This passes even if null vs empty would fail
  ```
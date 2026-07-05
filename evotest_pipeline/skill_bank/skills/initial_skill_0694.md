---
name: indexed-property-array-bounds-validation
description: When a method accesses an indexed child property using an integer parameter,
  test that out-of-bounds index values (negative and exceeding size) throw ArrayIndexOutOfBoundsException
  to prevent silent failures or data corruption.
code_tags:
- ARRAY_INDEX_ACCESS
- BOUNDARY_CHECK
- VALIDATION
test_pattern: EXCEPTION_TEST
---

# indexed-property-array-bounds-validation

## Instructions

# Indexed Property Array Bounds Validation

## Instructions

WHEN the TG encounters a method that accesses a child component or property by integer index (e.g., `get(int index)` or any method that takes an `int` parameter used to index into an internal list/array of children or components),

THEN the TG should write an exception test that:
1. Creates a container/component with a known number of children (e.g., 0 children for an empty container, or N children for a populated container).
2. Calls the indexed method with an index that is **equal to the size** of the internal list (one past the last valid index).
3. Verifies that `ArrayIndexOutOfBoundsException` (or `IndexOutOfBoundsException`) is thrown.
4. Also tests with a **negative index** (e.g., -1) to verify that negative indices also throw the expected exception.
5. Uses `assertThrows(ArrayIndexOutOfBoundsException.class, () -> ...)` or the JUnit 4 `@Test(expected = ArrayIndexOutOfBoundsException.class)` annotation.

**Common pitfalls to avoid:**
- Only testing with valid indices within bounds — the bug is specifically about out-of-bounds indices.
- Testing only one out-of-bounds case — test both negative indices and indices equal to/exceeding the container size.
- Testing with a non-empty container where the index equals size but the test passes because `size()` returns the wrong value — test with an empty container (size=0) to make the boundary condition clearer.
- Forgetting that `get(int index)` on a List throws `IndexOutOfBoundsException`, but the underlying implementation might use a raw array access (`children[index]`) that throws `ArrayIndexOutOfBoundsException`.

**Example (correct):**
```java
@Test(expected = ArrayIndexOutOfBoundsException.class)
public void getIndexedOutOfBounds()
{
    MarkupContainer container = new MarkupContainer(Mockito.mock(String.class));
    container.get(0); // empty container, size=0, index 0 is out of bounds
}
```

**Example (incorrect — misses the bug):**
```java
@Test
public void getWithValidIndex()
{
    MarkupContainer container = new MarkupContainer(Mockito.mock(String.class));
    container.add(new Label("child"));
    assertEquals(Label.class, container.get(0).getClass());
    // This tests only the happy path and does not catch the missing bounds check
}
```
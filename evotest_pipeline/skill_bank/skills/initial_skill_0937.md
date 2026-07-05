---
name: micro-map-iterator-exhaustion
description: When testing custom Map implementations (like MicroMap) that override
  entrySet(), keySet(), or values() with anonymous Iterator classes, verify that after
  consuming all elements, hasNext() returns false and next() throws NoSuchElementException.
  This skill detects iterator contract violations in small-capacity collections.
code_tags:
- BOUNDARY_CHECK
- STATE_MUTATION
- ITERATOR_CONTRACT_VIOLATION
test_pattern: EXCEPTION_TEST
---

# micro-map-iterator-exhaustion

## Instructions

# MicroMap Iterator Exhaustion Testing

## Instructions

WHEN the TG encounters a custom Map implementation (especially `MicroMap`, `MiniMap`, or any `Map<K,V>` with a capacity limit of 1) that provides its own `keySet()`, `entrySet()`, or `values()` collections via anonymous `Iterator` classes:

- THEN the TG MUST test the iterator contract after consuming all elements by:
  1. Creating an instance of the map and adding exactly one entry (e.g., `map.put(FOO, BAR)`)
  2. Obtaining the iterator from `keySet().iterator()`, `entrySet().iterator()`, and `values().iterator()`
  3. Calling `next()` once to consume the single element
  4. Verifying `hasNext()` returns `false`
  5. Verifying `next()` throws `java.util.NoSuchElementException` using `Assert.fail("Expected i.next() to fail with NoSuchElementException")` inside a try-catch block

WHEN the map has size 0 (empty):

- THEN the TG MUST also test the empty-map case: obtain an iterator, verify `hasNext()` returns `false`, and verify `next()` throws `NoSuchElementException`

WHEN the custom map's `values()` returns an `AbstractList<V>`:

- THEN the TG MUST verify its `iterator()` follows the same contract after consuming all elements (since `AbstractList.iterator()` delegates to `get(index)` which may have its own bounds checking)

Common pitfalls to avoid:

- Do NOT test only `hasNext()` without verifying that `next()` throws the correct exception. A buggy iterator may have `hasNext()` returning `false` but still fail to throw `NoSuchElementException` in `next()` (or vice versa).
- Do NOT assume that because `size()` returns 1, there is only one call to `next()` — test the boundary after exhausting the single element.
- Do NOT use `assertThrows(NoSuchElementException.class, () -> i.next())` unless using JUnit 5; on JUnit 4 (as in this codebase), use try-catch with `fail()` as shown below.
- Do NOT test only `keySet()` — repeat for `entrySet()` and `values()` since each has its own anonymous iterator implementation that may have bugs in `next()`.

Example (correct):

```java
@Test
public void testMicroMap()
{
    MicroMap<Object, Object> m = new MicroMap<>();
    m.put(FOO, BAR);

    // Test keySet iterator exhaustion
    Iterator<?> i = m.keySet().iterator();
    assertTrue(i.hasNext());
    Object key = i.next();
    assertEquals(FOO, key);
    assertFalse(i.hasNext());
    try
    {
        i.next();
        fail("Expected i.next() to fail with NoSuchElementException");
    }
    catch (NoSuchElementException e)
    {
        // Swallow this.
    }

    // Test entrySet iterator exhaustion
    i = m.entrySet().iterator();
    assertTrue(i.hasNext());
    i.next();
    assertFalse(i.hasNext());
    try
    {
        i.next();
        fail("Expected entrySet iterator to fail with NoSuchElementException");
    }
    catch (NoSuchElementException e)
    {
        // Swallow this.
    }

    // Test values iterator exhaustion
    i = m.values().iterator();
    assertTrue(i.hasNext());
    i.next();
    assertFalse(i.hasNext());
    try
    {
        i.next();
        fail("Expected values iterator to fail with NoSuchElementException");
    }
    catch (NoSuchElementException e)
    {
        // Swallow this.
    }
}
```

Example (incorrect — missing iterator exhaustion check):

```java
// BAD: Only checks hasNext() and next() but doesn't verify
// that next() throws on the exhausted iterator
Iterator<?> i = m.keySet().iterator();
assertTrue(i.hasNext());
assertEquals(FOO, i.next());
// Missing: assertFalse(i.hasNext());
// Missing: try { i.next(); fail(...); } catch (NoSuchElementException e) { }
```
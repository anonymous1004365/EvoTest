---
name: zero-size-cache-validation
description: WHEN a cache or buffer is constructed with a maximum size/memory parameter,
  THEN test that constructing with zero or negative values throws the appropriate
  IllegalArgumentException. The bug was that CacheLIRS allowed creation with maxMemory=0,
  which caused "Max memory must be larger than 0" failures.
code_tags:
- VALIDATION
- BOUNDARY_CHECK
test_pattern: EXCEPTION_TEST
---

# zero-size-cache-validation

## Instructions

# Zero-Size Cache Validation

## Instructions

WHEN the TG encounters a cache or buffer class that accepts a `maxMemory`, `maxEntries`, or `maxSize` parameter in its constructor, or a `setMaxMemory(long)` / `setMaxSize(...)` method:

- THEN the TG MUST test that constructing or configuring with a **zero** value (e.g., `maxMemory = 0`) throws `IllegalArgumentException` with a message containing "Max memory must be larger than 0" or similar.
- The TG MUST also test that constructing or configuring with a **negative** value (e.g., `maxMemory = -1`) throws `IllegalArgumentException`.
- Concrete example: `CacheLIRS<Integer, Integer>(0)` should throw `IllegalArgumentException`.
- Concrete example: `cache.setMaxMemory(0)` should throw `IllegalArgumentException`.
- Common pitfalls: 
  - DO NOT assume the constructor only validates negative values. Zero is a distinct boundary case that is often missed.
  - DO NOT assume validation lives in the public API only — check the internal constructor parameters too.
  - DO NOT only test the `setMaxMemory()` method — also test the constructor that takes `maxMemory` or `maxEntries` directly.
  - The test should use `@Test(expected = IllegalArgumentException.class)` or a try-catch with `fail()` pattern.

### Correct Example
```java
@Test(expected = IllegalArgumentException.class)
public void testZeroMaxMemory() {
    new CacheLIRS<Integer, Integer>(0);
}

@Test(expected = IllegalArgumentException.class)
public void testNegativeMaxMemory() {
    new CacheLIRS<Integer, Integer>(-1);
}

@Test
public void testSetZeroMaxMemory() {
    CacheLIRS<Integer, Integer> cache = new CacheLIRS<Integer, Integer>(10);
    try {
        cache.setMaxMemory(0);
        fail("Expected IllegalArgumentException");
    } catch (IllegalArgumentException e) {
        assertEquals("Max memory must be larger than 0", e.getMessage());
    }
}
```

### Incorrect Example (only testing negative values, missing zero)
```java
@Test(expected = IllegalArgumentException.class)
public void testInvalidMaxMemory() {
    new CacheLIRS<Integer, Integer>(-1);
}
// Missing: test for maxMemory = 0
```
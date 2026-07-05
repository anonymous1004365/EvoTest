---
name: structured-data-filter-map-null-protection
description: When creating StructuredDataFilter or MapFilter from a configuration,
  the getMap() method may return null if the underlying StringMap is null. Tests must
  verify that null maps are handled gracefully (returning an empty or non-null map)
  rather than causing a NullPointerException.
code_tags:
- NULL_CHECK
test_pattern: EXCEPTION_TEST
---

# structured-data-filter-map-null-protection

## Instructions

# StructuredDataFilter Map Null Protection

## Instructions

- WHEN the TG encounters a `StructuredDataFilter` or `MapFilter` being created via `createFilter()` or a configuration-based factory method (e.g., from an XML config parsed into a `Map<String, List<String>>`), and the filter's internal `getStringMap()` method returns `null`
- THEN the TG should test that calling `getMap()` on such a filter (which internally delegates to `getStringMap()`) does NOT throw a `NullPointerException`. The method should either return an empty map or gracefully handle the null case.
- Include concrete types: The bug is in `MapFilter` (and its subclass `StructuredDataFilter`), where `getMap()` calls `getStringMap().toMap()` without null-checking the return value of `getStringMap()`.
- The test should verify that when a filter is constructed without initializing its internal `StringMap` (e.g., using a constructor path that leaves it null), subsequent calls to `getMap()` do not throw `NullPointerException` — they should return an empty `Map<String, List<String>>`.
- **Common pitfall**: Testing only the happy path where the map is populated. Failing to test the case where the filter is constructed in a way that leaves its internal state incomplete (e.g., `isAnd` set to `false` but `localMap`/`stringMap` never initialized).

### Example: Correct Test (catches the bug)

```java
@Test
public void testGetMapReturnsEmptyWhenStringMapIsNull() {
    // Construct a StructuredDataFilter (or MapFilter) in a way that
    // leaves its internal stringMap null. For example, the constructor
    // may accept a Map<String, List<String>> but not initialize the field.
    StructuredDataFilter filter = StructuredDataFilter.createFilter(
        new HashMap<>(), false, null, null);
    
    // Without the fix, this throws NullPointerException.
    // After the fix, it should return an empty Map.
    Map<String, List<String>> map = filter.getMap();
    assertNotNull("getMap() should not return null even if stringMap is null", map);
    assertTrue("getMap() should be empty when filter has no configured map", map.isEmpty());
}
```

### Example: Incorrect Test (will NOT catch the bug)

```java
@Test
public void testGetMapWithValidData() {
    Map<String, List<String>> input = new HashMap<>();
    input.put("key", Arrays.asList("val1", "val2"));
    StructuredDataFilter filter = StructuredDataFilter.createFilter(
        input, true, null, null);
    
    Map<String, List<String>> map = filter.getMap();
    assertEquals(1, map.size());  // This works both before and after the fix
    // BUT this test does NOT cover the null-stringMap scenario
}
```
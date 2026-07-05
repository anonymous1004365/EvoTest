---
name: duplicated-key-array-retrieval
description: When a ValueMap stores multiple values under the same key (via the `add`
  method), getStringArray(key) must return ALL values as a String[]. Test that repeated
  keys in the constructor string produce an array with all values preserved, not just
  one value. Only applicable when the map uses `LinkedHashMap<String, Object>` and
  values can be Object (String or String[]).
code_tags:
- NULL_CHECK
- ACCESS_CONTROL_EVALUATION
- ARGUMENT_VALIDATION
test_pattern: PARAMETRIC_TEST
---

# duplicated-key-array-retrieval

## Instructions

# Duplicated Key Array Retrieval in ValueMap

## Instructions

- WHEN the TG encounters a class extending `LinkedHashMap<String, Object>` (like `ValueMap`) that:
  - Has an `add(String key, Object value)` method that does NOT overwrite existing values but instead converts to `String[]` when the same key appears again
  - Has a `getStringArray(String key)` method that retrieves values
  - Has a string-parsing constructor (e.g., `new ValueMap("a=1,a=2,a=3")`) that calls `add()` for each key-value pair

- THEN the TG should write a test that:
  1. Creates a `ValueMap` using the string constructor with repeated keys: `new ValueMap("a=1,a=2,a=3")`
  2. Calls `getStringArray("a")` on the resulting map
  3. Asserts the returned `String[]` has length 3
  4. Asserts the array contains `"1"`, `"2"`, and `"3"` in order
  5. Also tests with a single key: `new ValueMap("a=1")` and verifies `getStringArray("a")` returns `["1"]`
  6. Also tests with no matching key: verifies `getStringArray("nonexistent")` returns `null`

- Common pitfalls to avoid:
  - Testing only with distinct keys (e.g., `"a=1,b=2,c=3"`) — this misses the bug entirely since the bug only manifests with repeated keys
  - Assuming `getStringArray` returns the raw stored object without proper type handling — the method must handle both `String` and `String[]` stored values
  - Not testing the ordering — since `ValueMap` extends `LinkedHashMap`, insertion order must be preserved in the returned array
  - Using `get("key")` instead of `getStringArray("key")` — only `getStringArray` has the conversion logic to handle multi-value storage

**Correct example:**
```java
@Test
public void testGetStringArrayWithDuplicatedKeys()
{
    ValueMap parameters = new ValueMap("a=1,a=2,a=3");
    String[] a = parameters.getStringArray("a");
    assertEquals(3, a.length);
    assertEquals("1", a[0]);
    assertEquals("2", a[1]);
    assertEquals("3", a[2]);
    
    // Also test single value
    ValueMap single = new ValueMap("a=1");
    String[] singleResult = single.getStringArray("a");
    assertEquals(1, singleResult.length);
    assertEquals("1", singleResult[0]);
    
    // Also test missing key
    assertNull(parameters.getStringArray("nonexistent"));
}
```

**Incorrect example (misses the bug):**
```java
@Test
public void testGetStringArray()
{
    ValueMap parameters = new ValueMap("a=1,b=2,c=3"); // distinct keys only
    String[] a = parameters.getStringArray("a");
    assertEquals(1, a.length); // This passes even on buggy code
}
```
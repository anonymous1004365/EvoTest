---
name: primitive-array-casting-prevention
description: WHEN the code uses value.getClass().isArray() followed by a cast to Object[],
  the TG should test with primitive array values like int[], boolean[], etc. to detect
  ClassCastException bugs where the code incorrectly assumes all arrays are Object[].
code_tags:
- TYPE_CONVERSION
- NULL_CHECK
- VALIDATION
test_pattern: EXCEPTION_TEST
---

# primitive-array-casting-prevention

## Instructions

# Primitive Array Casting in `asArray(Map<String, Object>)`

## Instructions

- WHEN the TG encounters a method like `JsonUtils.asArray(Map<String, Object>)` that:
  1. Checks `value.getClass().isArray()` to detect arrays
  2. Then casts directly to `Object[]` with `(Object[]) value`
  3. Iterates over the cast array
- THEN the TG should test with a **primitive array value** (e.g., `int[]`, `boolean[]`, `byte[]`, `char[]`, `short[]`, `long[]`, `float[]`, `double[]`) as a map entry value
- The test MUST verify that the method **does not throw a `ClassCastException`** when encountering a primitive array
- Specifically for `JsonUtils.asArray()`, test with:
  - `map.put("ints", new int[]{1, 2, 3})`
  - `map.put("bools", new boolean[]{true, false})`
- The expected behavior is that the method should handle primitive arrays gracefully (e.g., by iterating over them or skipping them), not crash with `ClassCastException`
- **Common pitfall #1**: Testing only with `Object[]` arrays (like `{"a", "b"}`) — this will NOT trigger the bug because `Object[]` casts succeed; the bug only manifests with primitive arrays like `int[]` or `boolean[]`
- **Common pitfall #2**: Assuming `value.getClass().isArray()` followed by `(Object[]) value` is safe for all arrays — it is NOT; primitive arrays (e.g., `int[]`, `boolean[]`) return `true` for `isArray()` but cannot be cast to `Object[]`, causing `ClassCastException`

### Correct example (bug-catching test):
```java
Map<String, Object> map = new HashMap<>();
map.put("ints", new int[]{1, 2, 3});
// This should NOT throw ClassCastException
// On buggy version: ClassCastException because int[] cannot be cast to Object[]
JsonUtils.asArray(map);
```

### Incorrect example (won't catch the bug):
```java
Map<String, Object> map = new HashMap<>();
map.put("strings", new String[]{"a", "b"});  // Object[] — fine, bug hidden
JsonUtils.asArray(map);  // passes on buggy version too
```
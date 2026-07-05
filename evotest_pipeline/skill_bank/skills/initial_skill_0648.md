---
name: parameter-set-preserves-position
description: When testing PageParameters.set() for an existing named parameter, the
  TG should verify that set() preserves the original position/index of the parameter
  rather than appending it. This catches bugs where set() uses add() internally and
  loses position tracking.
code_tags:
- NULL_CHECK
- EXCEPTION_HANDLING
test_pattern: STATE_TEST
---

# parameter-set-preserves-position

## Instructions

# PageParameters.set() Must Preserve Named Parameter Position

## Instructions

- WHEN the TG encounters code that uses `PageParameters.set(String, Object, Type)` or `PageParameters.set(String, Object, int, Type)` to overwrite an existing named parameter
- THEN the TG should verify that **the original position of the named parameter is preserved** after the set operation. Specifically:
  1. Create a `PageParameters` instance and add at least two named parameters with known positions using `add(name, value, type)` — e.g., `add("named1", "value1", Type.MANUAL)` and `add("named2", "value2", Type.MANUAL)`
  2. Assert initial positions with `getPosition("named1")` (should be 0) and `getPosition("named2")` (should be 1)
  3. Call `set("named1", "newValue", Type.MANUAL)` to overwrite the first parameter
  4. Assert that `getPosition("named1")` is still 0 (not appended to the end)
  5. Assert that `get("named1").toString()` returns `"newValue"` — the value was updated
  6. Assert that `getPosition("named2")` is still 1 — other parameters are unaffected
- Common pitfalls to avoid:
  - Testing `set()` only with parameters that don't already exist (appending case). The bug only manifests when overwriting a parameter that was previously added.
  - Testing `set()` without checking `getPosition()` — checking only the value change is insufficient to catch the position bug.
  - Assuming `set()` internally uses proper index-preserving logic when it actually uses `add()` which always appends.

### Correct test pattern:
```java
PageParameters parameters = new PageParameters();
parameters.add("named1", "value1", INamedParameters.Type.MANUAL);
parameters.add("named2", "value2", INamedParameters.Type.MANUAL);

assertEquals(0, parameters.getPosition("named1"));
assertEquals(1, parameters.getPosition("named2"));

// overwrite it — must preserve position
parameters.set("named1", "newValue", INamedParameters.Type.MANUAL);
parameters.set("named3", "value3", INamedParameters.Type.MANUAL);

assertEquals(0, parameters.getPosition("named1"));
assertEquals("newValue", parameters.get("named1").toString());
assertEquals(1, parameters.getPosition("named2"));
assertEquals(2, parameters.getPosition("named3"));
```

### Incorrect test (would miss the bug):
```java
PageParameters parameters = new PageParameters();
parameters.set("named1", "value1", INamedParameters.Type.MANUAL);
// Only tests appending — never tests overwriting an existing key
assertEquals(0, parameters.getPosition("named1"));
```
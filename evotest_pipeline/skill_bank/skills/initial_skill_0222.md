---
name: invalid-script-throws-exception
description: When applying a user-provided script or algorithm string, the TG should
  test that invalid/unsupported script syntax raises a meaningful exception instead
  of silently failing or producing wrong results.
code_tags:
- ARGUMENT_VALIDATION
- EXCEPTION_HANDLING
- EDGE_CASE_INPUT
test_pattern: EXCEPTION_TEST
---

# invalid-script-throws-exception

## Instructions

# Invalid Script Input Throws Exception

## Instructions

- WHEN the TG encounters a method that evaluates or applies a user-supplied algorithm/script string (e.g., `apply(String script, ...)`)
- THEN it should test that **invalid script inputs** cause the method to throw a meaningful exception (e.g., `MolgenisDataException`, `IllegalArgumentException`, or a custom checked exception) instead of silently returning a wrong/empty result
- The test must include at least: (1) a null or empty script, (2) a syntactically invalid script (e.g., misspelled function name like `toStrung(.)` instead of `toString(.)`), and (3) a script with mismatched parentheses/braces
- Verify the exception message indicates what went wrong (contains the invalid script fragment or a descriptive error)
- Do NOT assume that only null input causes failure — test **malformed scripts** too, especially when expression evaluation uses domain-specific language (DSL) or custom function resolution
- Common mistake: testing only with `null` or empty strings but forgetting to test with syntactically incorrect but non-null scripts, which might silently produce unexpected results

### Correct Example (catches the bug)
```java
@Test(expectedExceptions = SomeException.class)
public void testApplyWithInvalidScript() {
    AlgorithmService algoService = new AlgorithmServiceImpl(...);
    algoService.apply("toStrung(${firstName})", entity, someMap);
}
```

### Incorrect Example (misses the bug)
```java
// Only tests null — does NOT catch malformed script bugs
@Test
public void testApplyWithNullScript() {
    AlgorithmService algoService = new AlgorithmServiceImpl(...);
    // Malformed scripts not tested — buggy version silently produces wrong result
}
```
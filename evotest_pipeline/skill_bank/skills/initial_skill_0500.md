---
name: validate-graph-generator-parameters
description: When a graph generator accepts numeric parameters (like vertex count
  or edge count) that could be zero or negative, test that the generator validates
  these inputs and throws an appropriate exception before attempting to create a graph.
  Use this skill for any graph generator or factory method that accepts numeric parameters
  without obvious validation.
code_tags:
- VALIDATION
test_pattern: EXCEPTION_TEST
---

# validate-graph-generator-parameters

## Instructions

# Validate Graph Generator Numeric Parameters

## Instructions

- WHEN a graph generator constructor or factory method accepts a numeric parameter representing a count (e.g., number of vertices, number of edges, degree, dimension) that cannot reasonably be zero or negative to produce a valid graph,
- THEN the test should call the generator constructor with an invalid value (e.g., `0` or `-1`) and verify that an `IllegalArgumentException` is thrown.
  - Example: `WattsStrogatzGraphGenerator(0, 3, 0.5)` should throw `IllegalArgumentException` because zero vertices is invalid.
  - Example: `WattsStrogatzGraphGenerator(-1, 3, 0.5)` should also throw `IllegalArgumentException`.
- Include tests for BOTH zero AND negative values — the fix often adds validation for both cases.
- Verify the exception message mentions the invalid parameter (e.g., contains the parameter name or value).
- Common mistakes:
  - Testing only one invalid value (e.g., testing `-1` but missing `0`, or vice versa).
  - Testing invalid values only on the `generateGraph` method without testing the constructor itself — the validation should happen at construction time if the broken state is immediately detectable.
  - Forgetting to assert on the exception type (`IllegalArgumentException`) — catching the wrong exception type would miss the bug.
  - Only testing happy-path (valid inputs) — the bug is that validation is missing entirely.

Correct test pattern:
```java
@Test(expected = IllegalArgumentException.class)
public void testNonIntegerVertices() {
    new WattsStrogatzGraphGenerator(0, 3, 0.5);
}
```

Incorrect test pattern (only tests one invalid value):
```java
@Test(expected = IllegalArgumentException.class)
public void testNegativeVertices() {
    new WattsStrogatzGraphGenerator(-1, 3, 0.5);
}
```

Both `0` and negative values should be tested independently to ensure all invalid inputs are caught.
---
name: template-type-reference-substitution
description: WHEN the TG encounters code that substitutes type access references in
  code templates (e.g., replacing type references like CtTypeReference or String parameters),
  THEN it should test with both primitive types and parameterized types to catch broken
  type access resolution. Use this skill when testing template substitution logic
  that validates or replaces type references.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
- ARRAY_INDEX_ACCESS
- TEMPLATE_TYPE_REFERENCE_VALIDATION
test_pattern: PARAMETRIC_TEST
---

# template-type-reference-substitution

## Instructions

# Template Type Reference Substitution

## Instructions

WHEN the TG encounters code that performs template substitution — specifically methods like `substituteTypeAccessReference` that replace or validate type references (e.g., `CtTypeReference`, `CtTypeAccess`) within a template's code elements — THEN the TG should:

1. **Test that substitution handles various types correctly**: Create tests that substitute type access references with both simple types (e.g., `String`) and complex/parameterized types (e.g., `List<String>`, `Map<Integer, String>`, or custom generic types). The bug may manifest when multiple different types are used in sequence.

2. **Verify the substituted type reference is correctly resolved**: After substitution, verify that the resulting code element has the correct type by checking the target type's qualified name or by asserting the code compiles/executes to the expected result.

3. **Test with different code contexts**: Verify that when substituting type references in different contexts (e.g., variable declarations, method return types, field declarations, cast expressions), the substitution works correctly and doesn't leave orphaned or incorrectly-linked type references.

4. **Expect the bug to manifest as an assertion error or incorrect type**: When running the test against the buggy version, the test should fail — typically because the substituted type reference doesn't resolve correctly (e.g., the target type's `getQualifiedName()` returns null or an unexpected value, or the compiled code doesn't match the expected output).

5. **Avoid testing only one type in isolation**: A common pitfall is to test substitution with a single type (e.g., only `String`). The bug may only surface when multiple different types are substituted in sequence or when a parameterized type (e.g., `List<String>`) is used as the target.

### Correct Example (what the test should do):
```java
// Substitute with multiple different types
CtTypeReference<String> stringRef = factory.Type().get(String.class);
template.substituteTypeAccessReference(stringRef);
// Assert the substitution worked correctly

CtTypeReference<List<String>> listRef = factory.Type().get(List.class)
    .getActualTypeArguments().add(factory.Type().get(String.class));
template.substituteTypeAccessReference(listRef);
// Assert the substitution worked correctly for parameterized types
```

### Incorrect Example (what to avoid):
```java
// Testing only with a single type — may miss the bug
CtTypeReference<String> stringRef = factory.Type().get(String.class);
template.substituteTypeAccessReference(stringRef);
// Only testing String type — insufficient
```

### Common Pitfalls:
- Testing only identical types (e.g., substituting `String` with another `String`) — the bug may only appear with *different* types
- Not testing parameterized types (generics) — these have different reference structures that may expose broken link logic
- Assuming the substitution is symmetric or idempotent — test the actual result, not just that no exception was thrown
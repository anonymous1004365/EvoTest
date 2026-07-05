---
name: template-parameter-type-validation
description: When validating proxy template parameters passed to a method, the TG should test that both target types (e.g., String.class) and CtTypeReference types are handled. The bug manifests when a type parameter of one kind (e.g., CtTypeReference) is stored/processed but only checked against another kind (e.g., String), causing a ClassCastException or logical failure.
code_tags: ['BOUNDARY_CHECK', 'VALIDATION', 'STATE_MUTATION']
test_pattern: PARAMETRIC_TEST
---

# template-parameter-type-validation

## Instructions

# Template Parameter Type Validation

## Instructions

WHEN the TG encounters a class that accepts "template parameters" or "proxy parameters" as a collection of Objects (e.g., `List<Object>`, `Object[]`, or varargs `Object...`), where those parameters can represent different kinds of type information (such as a plain `String` class name vs. a `CtTypeReference` wrapper object), THEN the TG should:

1. **Test with mixed types**: Write tests that pass BOTH `String` values (e.g., `"java.lang.String"`) AND `CtTypeReference` objects (or their equivalent typed wrappers) as parameters. Do NOT assume all type parameters are of the same concrete type.

2. **Verify the parameter is used correctly**: The TG should confirm that when a type parameter is stored/processed, the code uses the correct branch to extract the type info from each kind of object. On the buggy version, a `CtTypeReference` object may be incorrectly treated as a `String` (or vice versa), leading to a `ClassCastException`.

3. **Assert on behavior**: The test should verify that both types of parameters work without throwing an exception and yield the expected result (e.g., the type is correctly recognized). In the buggy version, a `ClassCastException` is expected when a `CtTypeReference` (or non-String type) is passed where only String was handled.

4. **Common pitfalls to avoid**:
   - **Testing only String type parameters**: The bug is that only String is handled; you MUST test with non-String type wrappers.
   - **Assuming `instanceof` checks cover all cases**: If the code has an `instanceof String` check but treats the else branch incorrectly (e.g., calling `.toString()` or casting without proper handling), the test should specifically probe that else branch.
   - **Forgetting the collection structure**: Some parameters may be nested inside a list or array; test both direct arguments and those wrapped in collections.

### Correct Example (what the TG should write):
```java
@Test
void testMixStringAndCtTypeReferenceParameters() {
    List<Object> params = new ArrayList<>();
    params.add("java.lang.String");       // String type
    params.add(mockCtTypeReference);      // CtTypeReference type (non-String)
    
    // On buggy version, this should throw ClassCastException
    // On fixed version, this should succeed
    assertDoesNotThrow(() -> target.method(params));
}
```

### Incorrect Example (what the TG should NOT do):
```java
// BAD: Only tests String parameters — will miss the bug
@Test
void testOnlyStringParameters() {
    List<Object> params = new ArrayList<>();
    params.add("java.lang.String");
    params.add("java.lang.Integer");
    
    // This passes even on buggy version, giving false confidence
    assertDoesNotThrow(() -> target.method(params));
}
```
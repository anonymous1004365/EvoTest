---
name: template-parameter-type-validation
description: WHEN testing CtNewClass (or CtConstructorCall) in no-classpath mode, THEN validate that all parameter types (both String and CtTypeReference) are correctly handled. This skill prevents missing type validation when template proxy parameters can be either String literals or typed references.
code_tags: ['VALIDATION', 'NULL_CHECK', 'TYPE_CONVERSION']
test_pattern: PARAMETRIC_TEST
---

# template-parameter-type-validation

## Instructions

# Template Parameter Type Validation

## Instructions

- WHEN the TG encounters a method that creates or processes `CtNewClass` / `CtConstructorCall` elements with template/proxy parameters that accept both `String` and `CtTypeReference` types (especially in a no-classpath context)
- THEN the TG should write a parametric test that:
  1. Creates a `CtNewClass` with a parameter whose value is a `CtTypeReference` (e.g., `factory.Type().get(String.class)`)
  2. Creates a `CtNewClass` with a parameter whose value is a plain `String` (e.g., `"java.lang.String"`)
  3. For each case, asserts that the resulting model element (e.g., the `CtNewClass` / `CtConstructorCall`) exists, has the expected number of arguments, and that each argument's type matches the expected type
  4. Runs both cases in no-classpath mode (e.g., by building the model with `Launcher` and `NoClasspath` enabled)
  5. Verifies that no `NullPointerException` or `ClassNotFoundException` is thrown, and that the type information is correctly resolved for both string and reference parameter types
- Common pitfalls to avoid:
  - Testing only with `String` type parameters and assuming `CtTypeReference` parameters will work the same way
  - Forgetting to enable no-classpath mode when the bug specifically manifests in that context
  - Assuming the number of arguments or their order is preserved correctly when parameter types vary
  - Not checking that the resulting model element (e.g., `CtNewClass`) actually has the expected number of arguments after building

### Correct Example (Java-like pseudocode)
```java
@Test
public void testMixedParameterTypes() {
    // Test with CtTypeReference parameter
    Launcher launcher = new Launcher();
    launcher.addInputResource("./src/test/resources/some-source");
    launcher.getEnvironment().setNoClasspath(true);
    CtModel model = launcher.buildModel();
    
    CtNewClass newClassWithRef = findNewClassWithParameterType(model, 
        factory.Type().get(String.class));
    assertNotNull(newClassWithRef);
    assertEquals(1, newClassWithRef.getArguments().size());
    
    // Test with String parameter
    CtNewClass newClassWithString = findNewClassWithParameterType(model, 
        "java.lang.String");
    assertNotNull(newClassWithString);
    assertEquals(1, newClassWithString.getArguments().size());
}
```

### Incorrect Example (pitfall to avoid)
```java
@Test
public void testOnlyStringParameters() {
    // ONLY testing String parameters — misses the bug
    Launcher launcher = new Launcher();
    launcher.addInputResource("./src/test/resources/some-source");
    launcher.getEnvironment().setNoClasspath(true);
    CtModel model = launcher.buildModel();
    
    CtNewClass nc = findNewClassWithStringParam(model, "java.lang.String");
    assertNotNull(nc); // passes even though CtTypeReference params would crash
}
```
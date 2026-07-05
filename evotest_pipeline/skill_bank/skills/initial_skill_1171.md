---
name: proxy-template-parameter-type-validation
description: When a method accepts proxy template parameters via a raw Types map,
  the TG must test that values of different types (e.g., String and CtTypeReference)
  are properly handled. Apply this skill when parsing, validating, or processing heterogeneous
  template parameter values.
code_tags:
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# proxy-template-parameter-type-validation

## Instructions

# Proxy Template Parameter Type Validation

## Instructions

- WHEN the TG encounters a method that reads values from a `Types` map (e.g., `Map<String, Object>` or `Map<String, Object[]>`) where keys represent proxy template parameter names (e.g., `"rawFullyQualifiedClassName"`), and the values can be either `String` or a type reference object (e.g., `CtTypeReference`)
- THEN the TG must write a parametric test that:
  1. Creates a `Types` map containing at least **two entries** with different **value types** for the same logical parameter family:
     - One entry with a **String value** (e.g., key `"rawFullyQualifiedClassName"`, value `"java.util.List"`)
     - One entry with a **CtTypeReference value** (e.g., key `"rawFullyQualifiedClassName"`, value `aCtTypeRef`)
  2. Passes this mixed-type `Types` map into the method under test
  3. Verifies that the method processes **both entries correctly** without throwing a `ClassCastException`, `NullPointerException`, or producing incorrect output due to type erasure assumptions
  4. Checks the **final state** or **return value** to ensure both parameters contributed correctly to the result (e.g., both were added to a collection that the method populates)
- Common pitfalls:
  - Testing with **only String-typed values** in the Types map — this hides bugs where the code fails on non-String types like CtTypeReference
  - Testing with **only CtTypeReference-typed values** — this hides the reverse direction
  - **Not verifying the "all values present" invariant** — the bug manifests not just as a crash, but as silently dropping one of the parameter values
  - Assuming the bug would manifest as a hard crash — test for **logical completeness** (both values present in result), not just absence of exceptions

### Example (Correct)

```java
// Correct: Tests with both String and CtTypeReference values
@Test
public void testDecodeWithMixedParameterTypes() {
    // Create a CtTypeReference value
    CtTypeReference<?> typeRef = new CtTypeReference<>() {
        @Override
        public String getQualifiedName() { return "java.util.List"; }
    };
    
    Types types = new Types();
    types.put("rawFullyQualifiedClassName", new Object[] {
        "java.util.List",          // String value
        typeRef                    // CtTypeReference value
    });
    
    List<String> result = methodUnderTest.decode(types);
    assertEquals(2, result.size());       // Both should be present
    assertTrue(result.contains("java.util.List"));
}
```

### Example (Incorrect)

```java
// Incorrect: Only tests String values — misses the bug
@Test
public void testDecode() {
    Types types = new Types();
    types.put("rawFullyQualifiedClassName", new Object[] {
        "java.util.List",          // Only String values
        "java.util.ArrayList"
    });
    
    List<String> result = methodUnderTest.decode(types);
    // Passes on buggy code because String path works, but CtTypeReference path is broken
}
```

### Example (Incorrect)

```java
// Incorrect: Only tests CtTypeReference values — misses the String path issue
@Test
public void testDecode() {
    CtTypeReference<?> typeRef1 = ...
    CtTypeReference<?> typeRef2 = ...
    
    Types types = new Types();
    types.put("rawFullyQualifiedClassName", new Object[] { typeRef1, typeRef2 });
    
    List<String> result = methodUnderTest.decode(types);
    // Fails on the String path but the test never checks String compatibility
}
```
---
name: annotation-value-type-compatibility
description: WHEN adding or modifying annotation values through an annotation API,
  THEN test with values of different types (String, CtTypeReference, etc.) to ensure
  the API correctly handles type-specific logic. This prevents state corruption from
  type-unsafe value addition.
code_tags:
- ANNOTATION_PRESENCE_CHECK
- TYPE_CONVERSION
- STATE_MUTATION
test_pattern: STATE_TEST
---

# annotation-value-type-compatibility

## Instructions

# Annotation Value Type Compatibility Testing

## Instructions

### WHEN the TG encounters code that adds or modifies values on an annotation element (e.g., through methods like `addValue`, `setValue`, `putValue`, or direct assignment into annotation value collections)
- **THEN** the TG should test with at least two distinct value types (e.g., `String` and `CtTypeReference`) to verify that the annotation stores and retrieves each type correctly without unintended type coercion or state corruption.

### WHEN the annotation API has overloaded or type-dispatching methods for adding values (e.g., `addValue(String key, Object value)` where the implementation branches on `value instanceof String` vs. `value instanceof CtTypeReference` vs. `value instanceof CtAnnotation`)
- **THEN** the TG should create separate test cases that pass each distinct type and verify that:
  1. The value is stored in the correct internal field/collection.
  2. The value can be retrieved later with the correct type intact.
  3. Adding a value of one type does not corrupt previously added values of another type.

### WHEN an annotation element can hold multiple values (e.g., a `Map<Object, Object>` or list of `Object`)
- **THEN** the TG should test interleaved addition of different types (e.g., add a `String` value, then add a `CtTypeReference` value, then add another `String`) to verify that each value is stored independently and that the annotation's internal state remains consistent.

### Common pitfalls to avoid:
- **Testing only one value type** — If the bug manifests only when mixing types (e.g., adding a `CtTypeReference` after a `String` corrupts the `String`), testing only `String` values will miss the bug.
- **Assuming annotation values are homogeneous** — Many annotation models allow heterogeneous value types even when the spec suggests otherwise; always test with at least two different concrete types.
- **Not verifying retrieval** — Storing a value is not enough; the test must call the getter/retrieval method and assert the returned value has the expected type and content.
- **Testing with only simple types** — Buggy code may handle `String` and primitive types correctly but fail on `CtTypeReference`, `CtAnnotation`, or other AST/reflect types.

### Correct example pattern:
```java
@Test
public void testAnnotationAddValueWithDifferentTypes() {
    CtAnnotation<?> annotation = factory.createAnnotation();
    // Add a String value
    annotation.addValue("key1", "stringValue");
    // Add a CtTypeReference value
    CtTypeReference<String> typeRef = factory.createTypeReference(String.class);
    annotation.addValue("key2", typeRef);
    // Verify both values are stored correctly
    assertEquals("stringValue", annotation.getValue("key1"));
    assertSame(typeRef, annotation.getValue("key2"));
}
```

### Incorrect example pattern (what would miss the bug):
```java
@Test
public void testAnnotationAddValue() {
    CtAnnotation<?> annotation = factory.createAnnotation();
    annotation.addValue("key", "value");
    // Only testing String type — misses bug where CtTypeReference values corrupt state
    assertEquals("value", annotation.getValue("key"));
}
```
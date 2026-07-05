---
name: annotation-on-parameter-reflection
description: When retrieving annotations from method parameters using reflection-like
  access (annotationType on parameter), the implementation may accidentally check
  annotations on the wrong element (e.g., method vs. parameter). Test with at least
  two different annotation types on a parameter to catch this bug.
code_tags:
- ANNOTATION_PRESENCE_CHECK
- TYPE_CONVERSION
- STATE_MUTATION
test_pattern: STATE_TEST
---

# annotation-on-parameter-reflection

## Instructions

# Annotation on Parameter Reflection Bug

## Instructions

- WHEN the TG encounters code that retrieves annotations from method parameters (e.g., `getAnnotation(annotationType)` on a parameter object, or iterating `getParameterAnnotations()`)
- THEN the TG should write a test that:
  1. Declares a method with **at least two different annotations** on the **same parameter** (e.g., `@Deprecated` and a custom annotation like `@SuppressWarnings`)
  2. Uses reflection to retrieve each annotation individually by calling `getAnnotation(Class)` on the `Parameter` object
  3. Asserts that each annotation is present and has the expected values
  4. **Critically**: Tests that calling `getAnnotation` with an annotation type that is **NOT** on the parameter but IS on a sibling parameter or on the method itself returns `null`
- Common pitfalls: 
  - Testing only a single annotation type on a single parameter — this misses bugs where the annotation lookup accidentally returns annotations from the wrong element (e.g., the method instead of the parameter)
  - Using only `getDeclaredAnnotations()` or `getParameterAnnotations()` without individual `getAnnotation(Class)` calls — the bug may only manifest in the per-type retrieval
  - Not testing with multiple annotation types on the same parameter — the bug may involve a type-based lookup that confuses annotation types between parameters or between method and parameter

### Correct example test pattern:
```java
// Declare a method with multiple annotations on parameters
void myMethod(@Deprecated @CustomAnnotation("value") String param1, @SuppressWarnings("unchecked") String param2) {}

// Test: retrieve each annotation by type from the correct parameter
Parameter param = method.getParameters()[0];
assertNotNull(param.getAnnotation(Deprecated.class));
assertNotNull(param.getAnnotation(CustomAnnotation.class));
assertEquals("value", param.getAnnotation(CustomAnnotation.class).value());

// Test: annotation NOT on this parameter returns null
assertNull(param.getAnnotation(SuppressWarnings.class)); // SuppressWarnings is on param2, not param1
```

### Incorrect (misses the bug) test pattern:
```java
// Only tests one annotation on one parameter
void myMethod(@Deprecated String param) {}
Parameter param = method.getParameters()[0];
assertNotNull(param.getAnnotation(Deprecated.class));
// Missing: testing with multiple annotation types reveals the bug
```
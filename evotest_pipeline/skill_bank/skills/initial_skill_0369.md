---
name: annotation-value-reflection-testing
description: When a framework/API provides annotation values via reflection, the TG
  should verify that different annotation parameter types (Class<?>, enum, String,
  nested annotation, arrays) are correctly resolved and accessible at runtime. This
  skill ensures the test exercises the reflection path that retrieves annotation element
  values.
code_tags:
- VALIDATION
- STATE_MUTATION
test_pattern: PARAMETRIC_TEST
---

# annotation-value-reflection-testing

## Instructions

# Annotation Value Reflection Testing

## Instructions

- WHEN the TG encounters code that reads annotation element values via reflection (e.g., `Method.getAnnotation()`, `annotationType().getMethod()`, or `AnnotationInvocationHandler`-style proxies to retrieve values from annotation elements)
- THEN the TG should write a PARAMETRIC test that:
  1. Creates an annotation usage with **multiple element types** including:
     - A `Class<?>` type element (e.g., `@MyAnnotation(type = SomeClass.class)`)
     - An `enum` type element (e.g., `@MyAnnotation(mode = MyEnum.VALUE)`)
     - A nested annotation type element (e.g., `@MyAnnotation(nested = @NestedAnnotation(...))`)
     - An array type element (e.g., `@MyAnnotation(values = {"a", "b"})`)
  2. Reads back the annotation via `getAnnotation()` on the annotated element
  3. Calls `annotation.elementName()` for each element type and verifies the returned value matches the expected value
  4. Verifies that the annotation is **not null** before accessing its elements

- WHEN testing annotation values that use `Class<?>` type elements retrieved via reflection/annotation proxy
- THEN verify that the returned object is the **exact expected `Class` object**. Common pitfalls include:
  - Testing only with simple `String` or `int` elements and assuming all types work
  - Forgetting that `Class<?>` values come back as `TypeType` or `CtTypeReference` wrapper objects rather than raw `Class<?>` objects in frameworks like Spoon
  - Not using `assertEquals(expectedClass, actualClass)` for class-typed annotation elements
  - Assuming `Class` values will be equal via `.equals()` without checking the actual runtime type

- WHEN validating the annotation retrieval path in Spoon (or similar code analysis frameworks)
- THEN the test MUST:
  1. Use `Factory.createClass()` or equivalent to create a class with the annotation
  2. Call `getAnnotation()` to retrieve the annotation from the class
  3. Call `getClass()` or equivalent on the annotation to access its actual type
  4. Verify the type using `assertEquals(actualAnnotationType, "expected.class.Name")`
  5. Verify the values match the expected annotation parameters
  6. Failing to call both `getAnnotation()` AND the value retrieval methods means the reflection path is not exercised

- Common pitfalls to avoid:
  - Testing only that the annotation **exists** without verifying the values are retrievable
  - Assuming that if the annotation compiles, it will reflect correctly — the bug is often in the runtime resolution, not compilation
  - Not testing with `Class<?>` parameters at all — these are the most likely to fail in reflection-based annotation retrieval
  - Using a simple `String.valueOf()` or `toString()` comparison instead of direct type comparison

## Examples

### Correct test (catches the bug):

```java
@Test
public void testAnnotationValueReflection() {
    // Arrange
    SpoonAPI spoon = new Launcher();
    spoon.addInputResource("./src/test/resources/annotations");
    spoon.buildModel();
    
    CtClass<?> ctClass = spoon.getFactory().Class().get("test.TestClass");
    
    // Act
    SomeAnnotation annotation = ctClass.getAnnotation(SomeAnnotation.class);
    
    // Assert
    assertNotNull("Annotation should be present", annotation);
    assertEquals("Expected string value", annotation.stringValue());
    assertEquals(Integer.class, annotation.classValue());  // THIS LINE is critical!
    assertEquals(Mode.ENUM_VALUE, annotation.enumValue());
}
```

### Incorrect test (would NOT catch the bug):

```java
@Test
public void testAnnotationExists() {
    // Only checks annotation presence, not value resolution
    SpoonAPI spoon = new Launcher();
    spoon.addInputResource("./src/test/resources/annotations");
    spoon.buildModel();
    
    CtClass<?> ctClass = spoon.getFactory().Class().get("test.TestClass");
    assertTrue("Annotation should be present", 
        ctClass.hasAnnotation(SomeAnnotation.class));
    // Missing: actually retrieving and asserting annotation values!
}
```
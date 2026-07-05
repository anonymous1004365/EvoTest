---
name: class-dollar-sign-traversal-validation
description: When traversing class names containing dollar signs for nested classes,
  the traversal logic can silently skip or return null if it encounters segments without
  corresponding real types. The TG should test that dollar-separated class name segments
  are each resolved as distinct type references and that the method returns a non-null,
  properly typed result.
code_tags:
- VALIDATION
- TYPE_CONVERSION
test_pattern: PARAMETRIC_TEST
---

# class-dollar-sign-traversal-validation

## Instructions

# Class Name Dollar Sign Traversal Validation

## Instructions

- WHEN the TG encounters a method that resolves a class by name — especially one that traverses segments separated by dots (`.`) — and the class name may contain dollar signs (`$`) denoting nested classes
- THEN the TG should write a test that:
  1. Passes a class name that includes both dots and dollar signs (e.g., `"com.example.OuterClass$InnerClass"` or similar nested class paths with `$`)
  2. Asserts that the resolved `CtTypeReference` or `CtClass` object is **not null**
  3. Asserts that the resolved type's **simple name** equals the expected simple name (the last segment after the last `$`)
  4. Optionally, asserts that the resolved type's **qualified name** matches the input exactly
- Common pitfalls to avoid:
  - **Testing only with dot-separated names** — the bug specifically involves `$` being mishandled during traversal, so test both with and without `$`
  - **Using only one level of nesting** — if the bug truncates after one `$`, test multi-level nested class names (e.g., `"A$B$C"`)
  - **Not checking the fully qualified name** — the returned type may be non-null but point to the wrong (outer) class

### Correct Example (catches the bug)

```java
@Test
public void testGetClassWithDollarAndNestedClass() {
    // Assuming factory/helper that resolves class names to CtTypeReference
    String qualifiedName = "some.pack.age.OuterClass$NestedClass";
    CtTypeReference<?> ref = typeFactory.get(qualifiedName);
    
    assertNotNull("Should resolve nested class with $", ref);
    assertEquals("NestedClass", ref.getSimpleName());
    assertEquals(qualifiedName, ref.getQualifiedName());
}
```

### Incorrect Example (fails to catch the bug)

```java
@Test
public void testGetClassSimple() {
    // Only tests dot-separated package names — no $, so the bug is not triggered
    String qualifiedName = "some.pack.age.SimpleClass";
    CtTypeReference<?> ref = typeFactory.get(qualifiedName);
    
    assertNotNull(ref);
    assertEquals("SimpleClass", ref.getSimpleName());
}
```
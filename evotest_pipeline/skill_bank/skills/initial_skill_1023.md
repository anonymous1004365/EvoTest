---
name: null-check-annotation-filter-path
description: When a method extracts a value from an annotation (like @WebFilter.value)
  and uses it as a filter path, the TG should test that the code handles a null annotation
  gracefully, expecting a NullPointerException on the buggy version due to missing
  null checks.
code_tags:
- NULL_CHECK
- VALIDATION
test_pattern: EXCEPTION_TEST
---

# null-check-annotation-filter-path

## Instructions

# Null Check for Filter Path From Annotation

## Instructions

- WHEN the TG encounters a `getFilterPathFromAnnotation` or similar method that reads a value from a servlet annotation (e.g., `@WebFilter`, `@WebServlet`) and converts it to a filter path, AND the method does not check whether the annotation or its value is null
  - THEN the TG should write a test that creates a filter class with a `@WebFilter` annotation that has a **null** `value` attribute, and verify that the code handles this gracefully or throws an appropriate exception
  - Specifically, the TG should:
    1. Create an annotated filter class (e.g., `@WebFilter(value = "/web/*")`) and ensure the annotation is present
    2. Test with a filter class that has **no** `@WebFilter` annotation at all (i.e., the annotation is null)
    3. Expect a `NullPointerException` on the buggy version when the annotation is null, because the code calls `annotation.value()` without a null check
    4. The test should use `WicketFilter.getFilterPath()` with a null annotation, or simulate the scenario by passing a filter class without the annotation
  - Common pitfalls to avoid:
    - Testing only the happy path where the annotation exists and has a valid value
    - Forgetting to test with a filter class that has absolutely no annotation (which triggers the null pointer)
    - Testing only with different `value` patterns but not with the annotation missing entirely
    - Assuming the annotation will always be present in production code

**Example (Incorrect, misses the null case):**
```java
@Test
public void testGetFilterPathFromAnnotation() {
    // Only tests the happy path with annotation present
    String path = filter.getFilterPathFromAnnotation(false);
    // This passes even on buggy version because annotation is not null
}
```

**Example (Correct, catches the bug):**
```java
@Test(expected = NullPointerException.class)
public void testGetFilterPathFromAnnotationWithoutAnnotation() {
    // Use a class without @WebFilter annotation
    String path = filter.getFilterPathFromAnnotation(false);
    // On buggy version, this throws NullPointerException because
    // the code calls annotation.value() without null check
}
```
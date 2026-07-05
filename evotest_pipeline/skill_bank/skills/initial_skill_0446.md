---
name: annotation-inheritance-support-validation
description: When a test base class validates field annotations and a subclass introduces
  a different annotation type, the TG should ensure tests cover the subclass's annotation
  as well. This skill helps catch bugs where the annotation check logic directly references
  annotation objects by class without considering that subclasses may override supported
  annotations.
code_tags:
- ANNOTATION_PRESENCE_CHECK
- NULL_CHECK
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# annotation-inheritance-support-validation

## Instructions

# Annotation Inheritance Support Validation

## Instructions

- WHEN the TG encounters a test class that extends a base test class, and the base test class has a `supportsField(Field)` method checking for specific annotations (e.g., `@Resource`, `@Inject`, `@SpringBean`):
  - THEN the TG should create a PARAMETRIC test that verifies each annotation type is properly supported by the subclass.
  - Include test cases for ALL annotation types that the subclass's `supportsField` implementation should handle, not just those tested by the base class.
  - Specifically test the annotation type that the subclass is named after (e.g., if the subclass is `JavaxInjectAnnotProxyFieldValueFactoryTest`, test with `javax.inject.Inject`).

- WHEN the `supportsField(Field)` method in the production code checks for annotation presence using `field.getAnnotation(...)` or `field.isAnnotationPresent(...)`:
  - THEN the TG should test with fields annotated with EACH annotation type the factory claims to support.
  - Verify that `supportsField` returns `true` for the relevant annotation and `false` for unrelated annotations.

- WHEN the base test class has a test that sets up mocked or proxied fields (e.g., `ParameterizedField` with specific annotations) and checks behavior like `getFieldValue`:
  - THEN the TG should override that test in the subclass if the subclass uses a different annotation type, or create a new test that uses the subclass's annotation.
  - Verify that `getFieldValue` works correctly (returns a non-null proxy/bean) and that `supportsField` returns the expected boolean.

- WHEN a `@Parameterized` test class uses `@Parameters` to provide `CtTypeReference` and `String` types for annotation class lookup:
  - THEN the TG should include both a `CtTypeReference` type parameter and a `String` type parameter in the parameterized data, testing that the annotation lookup logic handles both type representations.
  - Common pitfall: Only testing with `String` type and not `CtTypeReference`, which can miss bugs in the type-aware annotation resolution logic.

- **Mistakes to avoid**:
  - Do NOT assume that if the base class tests work, the subclass tests automatically pass — the subclass may have different annotation support logic or additional annotations.
  - Do NOT test only one annotation type when the factory supports multiple annotations across different subclasses.
  - Do NOT forget to verify that the triggering test method (e.g., `required()`) correctly reports the field annotation name (e.g., `@Inject`) in error messages when the field is missing.
  - Do NOT assume that the annotation check is symmetrical — just because `@Resource` is supported doesn't mean `@Inject` is, and vice versa.

### Example (correct approach)

```java
// Given a base test class that tests @Resource annotations, 
// and a subclass JavaxInjectAnnotProxyFieldValueFactoryTest that supports @Inject:
// The test should:
@Test
public void supportsField_withInjectAnnotation_returnsTrue() throws Exception {
    Field field = SomeClass.class.getDeclaredField("injectField");
    assertTrue(factory.supportsField(field));
}

@Test
public void supportsField_withoutAnnotation_returnsFalse() throws Exception {
    Field field = SomeClass.class.getDeclaredField("plainField");
    assertFalse(factory.supportsField(field));
}

// Given the buggy behavior (NPE when field is missing @Inject but factory requires it):
@Test(expected = IllegalStateException.class)
public void required_injectFieldMissing_throwsException() {
    // factory tries to get value for @Inject-annotated field
    // but the field has no injection target, should throw IllegalStateException
    factory.getFieldValue(missingInjectField);
}
```

### Example (incorrect approach)

```java
// WRONG: Only tests @Resource, missing @Inject scenario
@Test
public void supportsField_withResourceAnnotation_returnsTrue() throws Exception {
    Field field = SomeClass.class.getDeclaredField("resourceField");
    assertTrue(factory.supportsField(field));
    // Missing: test @Inject annotation for the subclass
}

// WRONG: Doesn't test the missing-annotation error case
@Test
public void required_fieldPresent_returnsProxy() {
    // Only tests the happy path, missing the error case
}
```
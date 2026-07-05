---
name: pojo-serializer-subclass-copy
description: WHEN testing PojoSerializer.copy() for POJO types with registered subclass
  hierarchies, THEN include test data instances of actual subclass types to verify
  that copy() correctly handles non-registered subclasses via the subclass serializer
  cache. This catches NullPointerException bugs when copy() tries to create a target
  instance of an abstract superclass type instead of the actual runtime subclass type.
code_tags:
- NULL_CHECK
- VALIDATION
- ARGUMENT_VALIDATION
- SERIALIZER_COPY
- TYPE_HIERARCHY_DESERIALIZATION
test_pattern: PARAMETRIC_TEST
---

# pojo-serializer-subclass-copy

## Instructions

# PojoSerializer Subclass Copy Verification

## Instructions

- WHEN the test generator (TG) encounters a `PojoSerializer` for a POJO type (e.g., `TestUserClass`) that has concrete subclass types (e.g., `SubTestUserClassA`, `SubTestUserClassB`), and the serializer test base's `testCopy()` method iterates over `getTestData()` calling `serializer.copy(datum)`:

  - THEN the TG MUST include instances of concrete subclass types (not just the base type) in the `getTestData()` array returned by the test class.
  - The test data array should contain at least one instance of each concrete subclass to exercise the `copy()` method's subclass handling path.
  - This is necessary because `PojoSerializer.copy()` uses `from.getClass().newInstance()` to create the copy target — if the runtime type is a subclass but the serializer only tests with base-type instances, the subclass copy path (which looks up a serializer via `getSubclassSerializer()` and uses it to copy fields) may not be exercised.
  - Verify that `serializer.copy(subclassInstance)` returns a non-null, deeply-equal copy of the original subclass instance. If the buggy code fails to handle the subclass correctly (e.g., returns null or throws a NullPointerException due to attempting `getClass().newInstance()` on a class without a public no-arg constructor or some other flaw), the test should fail with an exception.
  - Example fix pattern: In `PojoSerializer.copy()`, when `actualType != clazz`, the code should call `getSubclassSerializer(actualType).copy(from)` instead of `actualType.newInstance()`.

- Common pitfalls:
  - Testing only base-type instances in `getTestData()` and not including subclass instances that exercise the subclass serializer cache code path.
  - Assuming that because the base class has a no-arg constructor, all subclasses automatically work with `newInstance()` — this is not always the case, and the `getSubclassSerializer()` path should be used instead.
  - Not verifying that the copied object preserves subclass-specific field values.

### Correct Example

```java
@Override
protected TestUserClass[] getTestData() {
    return new TestUserClass[]{
        // Base type instances
        new TestUserClass(...),
        // Subclass instances that exercise the subclass copy path
        new SubTestUserClassA(),
        new SubTestUserClassB()
    };
}
```

### Incorrect Example (only base type instances)

```java
@Override
protected TestUserClass[] getTestData() {
    return new TestUserClass[]{
        new TestUserClass(...),
        new TestUserClass(...)
        // Missing: SubTestUserClassA and SubTestUserClassB instances
    };
}
```
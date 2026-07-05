---
name: reference-value-identifier-validation
description: Teach the TG to test that REFERENCE and WEAKREFERENCE value creation
  correctly validates the identifier string, catching cases where invalid (non-UUID)
  strings are silently accepted instead of throwing RepositoryException.
code_tags:
- VALIDATION
- STATE_MUTATION
- BOUNDARY_CHECK
- REFERENCE_WEAKREFERENCE_VALIDATION
- EXCEPTION_HANDLING
test_pattern: EXCEPTION_TEST
---

# reference-value-identifier-validation

## Instructions

# Reference Value Identifier Validation

## Instructions

WHEN the TG encounters a method that creates a JCR Value of type REFERENCE or WEAKREFERENCE (e.g., `createValue(String value, int type)` where `type` is `PropertyType.REFERENCE` or `PropertyType.WEAKREFERENCE`), THEN it should test that the method validates the identifier string against a valid UUID format.

- The test MUST verify that passing a non-UUID string (e.g., `"invalid"`, `"123"`, `"not-a-uuid"`, or an empty string `""`) with type REFERENCE or WEAKREFERENCE throws a `RepositoryException` with a message indicating the value is invalid (e.g., containing "Invalid value" or "not a valid reference").
- The test MUST also verify that a valid UUID string (e.g., `"01234567-9abc-def0-1234-56789abcdef0"`) with type REFERENCE or WEAKREFERENCE is accepted without throwing an exception.
- Use `org.apache.jackrabbit.commons.JcrUtils` or `org.apache.jackrabbit.oak.commons.UUIDUtils` or `java.util.UUID.fromString()` to validate the UUID format — the key is that the implementation must validate that the string is a proper UUID.

Common pitfalls to avoid:
- Testing only `createValue(String)` (which creates a STRING type) but not testing `createValue(String, int)` with REFERENCE/WEAKREFERENCE types.
- Testing with valid UUID values only and not testing with invalid values.
- Testing only one invalid value — test with multiple invalid formats (non-UUID string, empty string, malformed UUID).
- Forgetting that the validation should throw `RepositoryException`, not `IllegalArgumentException` or other exceptions.
- Not considering that the fix might be in a helper/utility method called by the value factory (e.g., a validation utility in a different class).

### Example Correct Test Pattern

```java
@Test(expected = RepositoryException.class)
public void testCreateReferenceValueWithInvalidString() throws Exception {
    ValueFactory valueFactory = ...;
    valueFactory.createValue("invalid", PropertyType.REFERENCE);
}

@Test(expected = RepositoryException.class)
public void testCreateWeakReferenceValueWithInvalidString() throws Exception {
    ValueFactory valueFactory = ...;
    valueFactory.createValue("not-a-uuid", PropertyType.WEAKREFERENCE);
}

@Test
public void testCreateReferenceValueWithValidString() throws Exception {
    ValueFactory valueFactory = ...;
    Value value = valueFactory.createValue(
        "01234567-9abc-def0-1234-56789abcdef0", PropertyType.REFERENCE);
    assertNotNull(value);
    assertEquals(PropertyType.REFERENCE, value.getType());
}
```

### Example Incorrect Test Pattern (Would NOT Catch the Bug)

```java
// BAD: Only tests the default createValue(String) which creates STRING type
@Test
public void testCreateValue() throws Exception {
    ValueFactory valueFactory = ...;
    Value value = valueFactory.createValue("invalid");
    assertNotNull(value);
}

// BAD: Only tests with valid UUID, never tests invalid input
@Test
public void testCreateReferenceValue() throws Exception {
    ValueFactory valueFactory = ...;
    Value value = valueFactory.createValue(
        "01234567-9abc-def0-1234-56789abcdef0", PropertyType.REFERENCE);
    assertNotNull(value);
    // Missing negative test with invalid string
}
```
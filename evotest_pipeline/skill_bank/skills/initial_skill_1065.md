---
name: object-name-validation-with-underscore
description: When validating resource object names (e.g., cloud storage bucket names,
  blob names), validate that names with underscores are correctly accepted or rejected
  per the specification. This skill helps detect cases where underscore-containing
  names are incorrectly rejected.
code_tags:
- VALIDATION
test_pattern: EXCEPTION_TEST
---

# object-name-validation-with-underscore

## Instructions

# Object Name Validation with Underscore

## Instructions

- WHEN the TG encounters validation logic that checks resource object names (e.g., cloud storage bucket names, blob names, file names) against a pattern or character set
- THEN it should test with names containing underscores (`_`) to verify they are correctly handled according to the specification
  - If the specification states underscores are valid, verify the name passes validation without throwing an exception
  - If the specification states underscores are invalid, verify the name correctly throws an appropriate exception (e.g., `IllegalArgumentException`)
- Include test cases for:
  - Names containing only underscores (e.g., `"_object"`, `"object_name"`, `"name_with_multiple_parts"`)
  - Names with mixed valid characters and underscores (e.g., `"my_valid_object_name"`)
  - Edge cases like names starting with underscore, ending with underscore, or consecutive underscores
- Specifically test that underscore-containing names are NOT rejected when the specification allows them — a common bug is to incorrectly reject these names
- Common pitfalls:
  - Testing only alphanumeric or hyphenated names while ignoring underscores
  - Using a validation regex pattern that is too restrictive (e.g., `[a-zA-Z0-9-]+` instead of `[a-zA-Z0-9_-]+`)
  - Assuming underscore is invalid without checking the actual specification requirements
  - Not testing with a variety of underscore positions (start, middle, end)

### Example (correct approach)

```java
@Test
public void testValidObjectWithUnderscore() {
    // This test should PASS on the fixed version and FAIL on the buggy version
    // because underscore is a valid character in object names
    String objectName = "my_valid_object_name";
    assertDoesNotThrow(() -> storage.create(objectName, new byte[0]));
    
    // Also test names starting and ending with underscore
    assertDoesNotThrow(() -> storage.create("_leading", new byte[0]));
    assertDoesNotThrow(() -> storage.create("trailing_", new byte[0]));
}
```

### Example (incorrect approach — will miss the bug)

```java
@Test
public void testValidObject() {
    // ❌ WRONG: Only tests alphanumeric names, misses the underscore bug
    String objectName = "myvalidobjectname";
    assertDoesNotThrow(() -> storage.create(objectName, new byte[0]));
}
```
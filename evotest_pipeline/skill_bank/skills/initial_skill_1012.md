---
{}
---

---
name: enum-value-of-with-custom-factory-method
description: When testing Logger Level or similar enum-like classes with a static factory method (e.g. toLevel), the TG should test that invalid string names that don't match the Java enum constant name throw an appropriate exception. The bug was that Level.forName("Information") returned an enum that later caused java.lang.IllegalArgumentException: No enum constant when calling Level.valueOf("Information") since "Information" is not a real enum constant name.
code_tags: ['ENUM_VALIDATION', 'TYPE_CONVERSION']
test_pattern: EXCEPTION_TEST
---

# enum-value-of-with-custom-factory-method

## Instructions

# Testing Enum-Like Classes with Static Factory Methods

## Instructions

- WHEN the TG encounters a class that acts like an enum but has static factory methods such as `toLevel(String)`, `forName(String, int)`, or `valueOf(String)` that create or retrieve custom enum instances that may not correspond to the actual Java enum constant names
- THEN the TG should test that passing a string that is NOT a valid Java enum constant name (e.g. "Information" when only "INFO" exists) to `Level.valueOf(String)` throws `java.lang.IllegalArgumentException` with message containing "No enum constant"
- The TG should verify that calling the static factory method (e.g. `Level.forName("Information", 350)`) succeeds (returns a Level object), but that subsequently calling `Level.valueOf("Information")` on the returned object's name fails with `IllegalArgumentException`
- Common pitfalls:
  - Only testing the factory method in isolation without testing `valueOf` round-trip
  - Assuming that `Level.forName("Information", 350).name()` will work with `Level.valueOf()` — it won't because `valueOf` only matches Java enum constant names exactly
  - Testing only with valid enum constant names that match the Java identifiers (like "INFO", "DEBUG")
  - Not testing the exact failure message "No enum constant" to distinguish from other exceptions

### Correct example (catches the bug):
```java
@Test
public void testCustomLevelNameNotInEnum() {
    Level custom = Level.forName("Information", 350);
    assertEquals("Information", custom.name());
    assertThrows(IllegalArgumentException.class, () -> Level.valueOf("Information"), 
        "Should throw because 'Information' is not a canonical enum constant name");
}
```

### Incorrect example (misses the bug):
```java
@Test
public void testCustomLevelName() {
    Level custom = Level.forName("Information", 350);
    assertEquals("Information", custom.name());
    // Missing: verifying that Level.valueOf("Information") throws IllegalArgumentException
}
```
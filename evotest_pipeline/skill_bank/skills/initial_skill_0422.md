---
name: optional-conversion-empty-string-returns-null
description: When a class provides toOptionalXxx() conversion methods that may receive
  empty strings as input, the test should verify that an empty string (not null) returns
  null for all optional-type conversions. This skill covers testing toOptionalBoolean(),
  toOptionalCharacter(), toOptionalDouble(), toOptionalDuration(), toOptionalInteger(),
  toOptionalLong(), toOptionalString(), toOptionalTime() and similar methods.
code_tags:
- EMPTY_STRING_HANDLING
- TYPE_CONVERSION
- OPTIONAL_VALUE_HANDLING
test_pattern: STATE_TEST
---

# optional-conversion-empty-string-returns-null

## Instructions

# Optional Conversion Empty String Returns Null

## Instructions

### WHEN the test generator encounters a class that has `toOptionalXxx()` conversion methods (e.g., `toOptionalBoolean()`, `toOptionalCharacter()`, `toOptionalDouble()`, `toOptionalInteger()`, `toOptionalLong()`, `toOptionalDuration()`, `toOptionalTime()`, `toOptionalString()`)

- **THEN** it should create a `StringValue` object with an empty string `""` (not null) and assert that **all** `toOptionalXxx()` methods return `null`, except `toOptionalString()` which should return `""`.
- **THEN** it should create a separate test with a `null` string value and assert that **all** `toOptionalXxx()` methods return `null`, including `toOptionalString()`.
- **THEN** it should verify each conversion method individually, not just a subset — missing any optional conversion method means the bug goes undetected.
- **THEN** for the `toOptional(Class<T> type)` generic method, it should also verify that calling it with `String.class` or `String[].class` on an empty string returns `null`.

### Common pitfalls to avoid:

- **DO NOT** test only with `null` input. Testing with `null` is necessary but insufficient — an empty string `""` is a distinct input value that the buggy version may fail to handle. The bug in this case is that `toOptionalXxx()` methods throw `StringValueConversionException` for empty strings instead of returning `null`.
- **DO NOT** test only one or two optional conversion methods. The bug may affect multiple or all `toOptionalXxx()` methods in the class. The test must cover every `toOptionalXxx()` method available.
- **DO NOT** forget that `toOptionalString()` for an empty string is a special case — it should return `""` (not null), while for null it should return `null`.
- **DO NOT** test only the happy path (valid strings). Empty and null inputs are boundary cases that deserve their own dedicated test method.

### Correct example (Java):

```java
@Test
public void toOptionalXyzWithEmptyString()
{
    StringValue sv = new StringValue("");
    assertNull(sv.toOptionalBoolean());
    assertNull(sv.toOptionalCharacter());
    assertNull(sv.toOptionalDouble());
    assertNull(sv.toOptionalDuration());
    assertNull(sv.toOptionalInteger());
    assertNull(sv.toOptionalLong());
    assertEquals("", sv.toOptionalString());
    assertNull(sv.toOptionalTime());
    // also test toOptional(Class) with empty string
    assertNull(sv.toOptional(String.class));
}

@Test
public void toOptionalXyzWithNull()
{
    StringValue sv = new StringValue(null);
    assertNull(sv.toOptionalBoolean());
    assertNull(sv.toOptionalCharacter());
    assertNull(sv.toOptionalDouble());
    assertNull(sv.toOptionalDuration());
    assertNull(sv.toOptionalInteger());
    assertNull(sv.toOptionalLong());
    assertNull(sv.toOptionalString());
    assertNull(sv.toOptionalTime());
    // also test toOptional(Class) with null
    assertNull(sv.toOptional(String.class));
}
```

### Incorrect example (Java):

```java
// BAD: Only tests null, not empty string
@Test
public void toOptionalXyzWithNull()
{
    StringValue sv = new StringValue(null);
    assertNull(sv.toOptionalBoolean());
    assertNull(sv.toOptionalCharacter());
    // ...
}

// BAD: Only tests a subset of methods - toOptionalDuration() and toOptionalTime() not tested
@Test
public void toOptionalBooleanAndIntegerOnly()
{
    StringValue sv = new StringValue("");
    assertNull(sv.toOptionalBoolean());
    assertNull(sv.toOptionalInteger());
    // Missing: toOptionalCharacter(), toOptionalDouble(), toOptionalDuration(),
    //          toOptionalLong(), toOptionalString(), toOptionalTime()
}
```
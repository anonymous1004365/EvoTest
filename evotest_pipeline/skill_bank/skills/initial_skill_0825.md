---
name: enum-converter-null-handling
description: When converting String values to enum types via reflection (valueOf),
  a null input value causes NullPointerException when calling value.toUpperCase()
  or similar String methods before the null check. This skill teaches how to test
  that null values are gracefully handled in custom PropertyConverter implementations.
code_tags:
- NULL_CHECK
- VALIDATION
- ARGUMENT_VALIDATION
test_pattern: EXCEPTION_TEST
---

# enum-converter-null-handling

## Instructions

# Null Value Handling in Enum Property Converters

## Instructions

- WHEN the TG encounters a `PropertyConverter` that converts a `String` value to an enum type using reflection (e.g., `Method.invoke(null, value.toUpperCase(Locale.ENGLISH))`), AND the `convert(String, ConversionContext)` method does not perform an explicit null check on the `value` parameter before calling `String.toUpperCase()` or any other `String` instance method
- THEN the TG should write a test that passes `null` as the `value` argument to the `convert` method and verify that it gracefully handles the null (returns `null`, returns a default, or throws a meaningful exception), WITHOUT throwing a `NullPointerException` on `value.toUpperCase(Locale.ENGLISH)` or `value.toUpperCase()`
- Concrete example from the actual bug: In `EnumConverter.convert()`, the second try-block calls `value.toUpperCase(Locale.ENGLISH)` without first checking if `value` is null. The fix adds `if (value != null) { return (T) factory.invoke(null, value.toUpperCase(Locale.ENGLISH)); }` — the test must pass `null` to trigger the NPE on the buggy version
- Common pitfalls: 
  - Testing only valid enum string values (e.g., "HELLO", "WORLD") — the bug is specific to the null case in the fallback uppercase conversion path
  - Forgetting that the first try-block may already catch the NPE from `factory.invoke(null, value)` with `null` value — the NPE actually occurs in the SECOND try-block where `value.toUpperCase(...)` is called without null check
  - Not importing the correct `ConversionContext` class needed to construct the test (typically you need a mock or simple implementation)
- Correct test pattern:

```java
@Test
public void testConvert_Nulls() {
    PropertyConverter<MyEnum> converter = new EnumConverter<>(MyEnum.class);
    ConversionContext ctx = new ConversionContext.Builder(MyEnum.class, "test").build();
    
    // This should NOT throw NullPointerException
    Object result = converter.convert(null, ctx);
    
    // On the buggy version, this throws NPE at value.toUpperCase()
    // On the fixed version, it returns null (or gracefully handles)
    assertNull(result);
}
```

- Incorrect test pattern (would NOT catch this bug):

```java
@Test
public void testConvert_ValidValue() {
    PropertyConverter<MyEnum> converter = new EnumConverter<>(MyEnum.class);
    ConversionContext ctx = new ConversionContext.Builder(MyEnum.class, "test").build();
    
    // This path works fine on both buggy and fixed versions
    assertEquals(MyEnum.VALUE, converter.convert("VALUE", ctx));
}
```
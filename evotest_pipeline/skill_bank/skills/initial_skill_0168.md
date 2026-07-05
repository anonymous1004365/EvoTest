---
name: header-as-type-validation
description: When testing simple language expressions with headerAs(key, className),
  the type class name must be validated to ensure it resolves to a real class. Without
  validation, invalid types silently return null instead of throwing an exception,
  masking configuration errors.
code_tags:
- VALIDATION
- TYPE_CONVERSION
- EXCEPTION_HANDLING
- HEADER_AS_VALIDATION
test_pattern: EXCEPTION_TEST
---

# header-as-type-validation

## Instructions

# headerAs Type Class Name Validation

## Instructions

- WHEN the TG encounters a simple language expression that uses the `headerAs(key, className)` function (e.g., `${headerAs(foo, SomeType)}` where `SomeType` is a class name string)
- THEN the TG should write a test that verifies an exception is thrown when the class name argument does not correspond to a real, loadable Java class (e.g., `headerAs(foo, BarType)` where `BarType` is not a valid class). The test should:
  - Set a header with key that matches the first argument (e.g., `"foo"` with any value)
  - Evaluate the simple expression using `SimpleLanguage.simple("${headerAs(foo, InvalidType)}").evaluate(exchange, Object.class)`
  - Expect an `ExpressionIllegalSyntaxException` (or similar syntax/validation exception) rather than silently returning `null`
- Common pitfalls:
  - Testing only the happy path where valid class names (like `String`, `Integer`, `Long`) are used — this misses the bug entirely
  - Assuming that returning `null` is correct behavior for invalid class names; the correct behavior is to throw an exception
  - Not setting the required header value in the exchange before evaluating the expression, which would cause a different (null header) code path

### Correct Example

```java
public void testHeaderAsInvalidType() throws Exception {
    exchange.getIn().setHeader("foo", "123");
    try {
        SimpleLanguage.simple("${headerAs(foo, BarType)}").evaluate(exchange, Object.class);
        fail("Should have thrown an exception");
    } catch (ExpressionIllegalSyntaxException e) {
        // expected
    }
}
```

### Incorrect Example (would miss the bug)

```java
public void testHeaderAsInvalidType() throws Exception {
    exchange.getIn().setHeader("foo", "123");
    Object result = SimpleLanguage.simple("${headerAs(foo, BarType)}").evaluate(exchange, Object.class);
    assertNull(result);  // WRONG: the buggy version returns null silently, the fixed version should throw
}
```
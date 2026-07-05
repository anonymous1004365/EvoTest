---
name: field-default-expression-validation
description: When testing getDefaultExpression on a field with an initializer, verify
  the returned expression is not null and has the correct type. Also test that fields
  without an initializer return null.
code_tags:
- VALIDATION
- NULL_CHECK
- STATE_MUTATION
test_pattern: STATE_TEST
---

# field-default-expression-validation

## Instructions

# Field Default Expression Validation

## Instructions

- WHEN the TG encounters a method like `getDefaultExpression()` on a field (`CtField`) that returns the field's default/initialization expression
- THEN it should test that:
  1. A field declared WITH an initializer (e.g., `int x = 5`) returns a non-null expression from `getDefaultExpression()`
  2. The returned expression's type matches the initializer value's type (e.g., for `int x = 5`, the expression should be a literal with integer value 5)
  3. A field declared WITHOUT an initializer (e.g., `int x;`) returns `null` from `getDefaultExpression()`

- Include tests for both primitive types (e.g., `int`, `String`) and reference types with initializers
- Verify the expression type using `CtLiteral` or `CtExpression` type checks
- Common pitfall: Only testing that `getDefaultExpression()` returns a non-null value without verifying the value is correct when it should be null for fields without initializers
- Common pitfall: Not testing the null case — fields without initializers must return null, not an empty or default expression

### Correct Example
```java
// Field: int x = 5;
CtField<?> field = type.getField("x");
CtExpression<?> expr = field.getDefaultExpression();
assertNotNull("Field with initializer should have non-null expression", expr);
assertTrue("Expression should be a literal", expr instanceof CtLiteral);
assertEquals(5, ((CtLiteral<?>) expr).getValue());

// Field: int y; (no initializer)
CtField<?> field2 = type.getField("y");
assertNull("Field without initializer should return null", field2.getDefaultExpression());
```

### Incorrect Example
```java
// BUG: Only checks non-null case, misses that fields without initializers should return null
CtField<?> field = type.getField("x");
assertNotNull(field.getDefaultExpression());

// ERROR: Assumes all fields have default expressions
CtField<?> field2 = type.getField("y");
assertNotNull(field2.getDefaultExpression()); // FAILS when y has no initializer!
```
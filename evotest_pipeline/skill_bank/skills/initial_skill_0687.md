---
name: primitive-overload-ambiguity-testing
description: When a method has overloaded variants taking primitive vs wrapper types
  (e.g., long vs Long, int vs Integer), test with both types to verify correct overload
  resolution. This skill helps catch bugs where the method treats overloaded parameters
  inconsistently, leading to runtime failures.
code_tags:
- ARGUMENT_VALIDATION
- NULL_CHECK
- STATE_MUTATION
- TYPE_CONVERSION
- VALIDATION
- PRIMITIVE_OVERLOAD_CONFUSION
test_pattern: PARAMETRIC_TEST
---

# primitive-overload-ambiguity-testing

## Instructions

# Primitive Overload Ambiguity Testing

## Instructions

- WHEN a class has overloaded methods or constructors that accept both a primitive type and its wrapper type (e.g., `long` and `Long`, `int` and `Integer`, `boolean` and `Boolean`)
- THEN write a test that invokes each overload explicitly and verifies correct behavior for both, including at least:
  1. A test passing a primitive literal (e.g., `3L`, `true`, `42`)
  2. A test passing a boxed wrapper value (e.g., `Long.valueOf(3L)`, `Boolean.valueOf(true)`, `Integer.valueOf(42)`)
  3. A test passing `null` for the wrapper variant (where applicable)
- Verify that the operations are symmetric — e.g., converting a value to its primitive and back yields the same result, or passing primitive vs wrapper produces the same object state
- Expect that on the buggy version, one of these overloads may fail with an exception such as `NullPointerException`, `IllegalArgumentException`, or a type mismatch error like `com.fasterxml.jackson.databind.exc.InvalidDefinitionException`
- COMMON PITFALL: Testing only with the wrapper type (`Long`, `Integer`, `Boolean`) and assuming the primitive overload will behave identically
- COMMON PITFALL: Not testing the `null` case for wrapper parameters, which may reveal missing null handling
- COMMON PITFALL: Assuming that auto-boxing/unboxing will always make primitives and wrappers interchangeable — the buggy code may use overload resolution or reflection that treats them differently

### Example (Good Test — catches the bug)

```java
@Test public void canUsePrimitiveOverloads() {
  // Test with primitive long (literal '3L')
  Span spanWithPrimitive = Span.newBuilder().timestamp(3L).build();
  assertThat(spanWithPrimitive.timestamp()).isEqualTo(3L);
  
  // Test with boxed Long
  Span spanWithBoxed = Span.newBuilder().timestamp(Long.valueOf(3L)).build();
  assertThat(spanWithBoxed.timestamp()).isEqualTo(3L);
  
  // Test with null Long (should produce null/default)
  Span spanWithNull = Span.newBuilder().timestamp((Long) null).build();
  assertThat(spanWithNull.timestamp()).isNull();
}
```

### Example (Bad Test — misses the bug)

```java
@Test public void testTimestamp() {
  // Only tests with primitive literal — does NOT exercise the Long wrapper overload
  Span span = Span.newBuilder().timestamp(3L).build();
  assertThat(span.timestamp()).isEqualTo(3L);
  // Bug: the Long overload may fail with an exception or produce wrong result
}
```
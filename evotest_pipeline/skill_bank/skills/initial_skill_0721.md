---
name: value-converter-source-null-check
description: When implementing a ConditionalConverter for value types (e.g., io.vavr.Value),
  the convert() method must guard against null source or null context to avoid NullPointerException.
  Test with null mapping context and null source values.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
- BOUNDARY_CHECK
- CONTEXT_SOURCE_NULL_CHECK
test_pattern: EXCEPTION_TEST
---

# value-converter-source-null-check

## Instructions

# Value Converter Source Null Check

## Instructions

- WHEN the TG encounters a `ConditionalConverter` implementation whose `convert(MappingContext)` method calls `context.getSource()` without a null check on either `context` or `context.getSource()`:
  - THEN the TG should write a test that passes `null` as the source value in the mapping context, and verify the converter returns `null` gracefully instead of throwing a `NullPointerException`.
  - Additionally, test with a `null` mapping context itself (if the method signature allows it), verifying that the method returns `null` rather than throwing `NullPointerException`.

- WHEN a value converter (e.g., implementing `ConditionalConverter<Value, Value>`) delegates to `context.create(src, destinationType)` and `context.getMappingEngine().map(ctx)`, and the source can be a collection-like value that is empty or contains null elements:
  - THEN the TG should test with a source collection containing null elements AND with an empty source collection, verifying that the converter does not throw internal exceptions.
  - Also verify that the converter can return `null` for a null source input without crashing.

- Common pitfalls to avoid:
  - Testing only with non-null source values and missing the null-source edge case.
  - Assuming that `context.getSource()` can never be null in real usage (e.g., when mapping a null object from one type to another).
  - Writing tests that only verify the normal happy path (non-null source matching and conversion) without testing the defensive null return path.
  - Forgetting that the `match()` method returns `MatchResult.FULL` for all `Value` subclass types, which means the converter is expected to handle all those types including cases where the source might be null.

### Correct test example (Java/JUnit 5)

```java
@Test
void testConvertWithNullSource() {
    // Given: a mapping context with null source
    MappingContext<Value, Value> context = mock(MappingContext.class);
    when(context.getSource()).thenReturn(null);
    
    ValueConverter converter = new ValueConverter();
    
    // When: converting with null source
    Value result = converter.convert(context);
    
    // Then: should return null gracefully, not throw NullPointerException
    assertNull(result);
}
```

### Incorrect test example (missing null source edge case)

```java
@Test
void testConvertNormal() {
    // Incorrect: only tests happy path, no null-source test
    List<String> sourceList = List.of("a", "b");
    MappingContext<Value, Value> context = mock(MappingContext.class);
    when(context.getSource()).thenReturn(sourceList);
    
    ValueConverter converter = new ValueConverter();
    Value result = converter.convert(context);
    
    assertNotNull(result);
    // Missing test for null source scenario
}
```
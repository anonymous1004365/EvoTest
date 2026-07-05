---
name: collection-type-narrowing-in-proxy-conversion
description: When a utility class collects multiple proxy wrapper types (like Vavr
  Option, JDK Optional) in a shared registry and applies narrowing conversions for
  compatibility, forgetting to handle new types in the conversion logic causes ClassCastException.
  Use this skill when TG sees a collection of wrapper types being iterated for conversion.
code_tags:
- JSON_PARSING_SYNTAX_CHECK
- NULL_CHECK
- BOOLEAN_LOGIC
- COLLECTION_OPERATIONS
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# collection-type-narrowing-in-proxy-conversion

## Instructions

# Collection Type Narrowing in Proxy Conversion

## Instructions

- WHEN the TG encounters code that iterates over a collection (e.g., `List`, `Set`) of proxy wrapper types (e.g., `Option`, `Optional`, `VavrOption`, `JdkOptional`) and applies a narrowing conversion from a broader type (e.g., `Object`) to a specific wrapper type, with a mechanism to skip or handle "others" (unknown types)
- THEN the TG should write a **parametric test** that registers a **new proxy wrapper type** (not yet handled by the conversion logic) and verifies that converting values using that new type either:
  - succeeds without `ClassCastException` (if the fix adds handling), **OR**
  - fails gracefully (e.g., returns `null`, skips, or throws a meaningful exception) — the TG must verify the expected behavior matches the fix
- Include **concrete types** from the actual code (e.g., `io.vavr.control.Option`, `java.util.Optional`, custom `QueryExecutionConverters` wrapper types)
- Verify that the **conversion method** (e.g., `potentiallyConvertValueToVavrOption`, `potentiallyConvertToWrapper`) handles **all** registered types, not just a hardcoded subset
- **Common pitfall**: Testing only the known types (e.g., only `Option` and `Optional`) and missing the bug where a newly added third type (e.g., `VavrOption`) is registered in the collection but its conversion logic is forgotten. Always test with a type that was added to the registry last.

### Example (Correct)

```java
// Correct: parametric test verifies all registered wrapper types
@ParameterizedTest
@MethodSource("wrapperTypes")
void convertsAllRegisteredWrapperTypes(Class<?> wrapperType, Object testValue) {
    Object result = queryExecutionConverters.potentiallyConvert(toOptionalValue(), wrapperType);
    assertThat(result).isInstanceOf(wrapperType);
}

static Stream<Arguments> wrapperTypes() {
    return Stream.of(
        Arguments.of(Option.class, Option.of("test")),
        Arguments.of(java.util.Optional.class, java.util.Optional.of("test")),
        Arguments.of(VavrOption.class, VavrOption.of("test"))  // VavrOption was the missing type
    );
}
```

### Example (Incorrect)

```java
// Incorrect: only tests one type, misses the newly added VavrOption
@Test
void convertsToVavrOption() {
    // Only tests the most common type
    Object result = queryExecutionConverters.potentiallyConvert(toOptionalValue(), Option.class);
    assertThat(result).isInstanceOf(Option.class);
}
```

### Failure Expectation

When the bug is present, the test for the newly added type (e.g., `VavrOption`) should fail with a `ClassCastException` because the conversion code attempts to cast `Option` to `VavrOption` without proper narrowing logic.
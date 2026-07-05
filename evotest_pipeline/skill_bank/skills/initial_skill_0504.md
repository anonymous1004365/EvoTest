---
name: type-info-parser-basic-types-validation
description: When parsing type information strings (e.g., "Integer", "String") using
  TypeInfoParser.parse(), test that both primitive wrapper types (Integer, Long, Double,
  Float, Boolean, Byte, Short, Character) and String types are correctly parsed into
  their corresponding TypeInformation. This skill helps detect parsing failures that
  manifest as IllegalArgumentException without proper error messages.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- NULL_CHECK
- TYPE_CONVERSION
- ERROR_HANDLING
test_pattern: PARAMETRIC_TEST
---

# type-info-parser-basic-types-validation

## Instructions

# TypeInfoParser Basic Type Parsing Validation

## Instructions

- WHEN the TG encounters code that calls `TypeInfoParser.parse(...)` to parse type information from string representations (e.g., "Integer", "String", "Long", "Double")
- THEN the TG should write a parametric test that iterates over ALL the following basic types and verifies that each one parses successfully without throwing an exception:
  - "Integer", "String", "Long", "Double", "Float", "Boolean", "Byte", "Short", "Character"
  - Expected behavior: `TypeInfoParser.parse(typeName)` should return a non-null `TypeInformation<?>` object for each of these strings
  - The test should use a `@ParameterizedTest` or equivalent looping mechanism, not separate individual test methods
- Common pitfalls to avoid:
  - Testing only a subset of basic types (e.g., only "Integer" and "String") — this misses failures in types like "Long" or "Double"
  - Using hardcoded individual test methods for each type instead of a single parametric test
  - Assuming that if one basic type works, all basic types work — each type has its own parsing path
  - Not catching `Throwable` — the parser may throw `IllegalArgumentException` or other runtime exceptions on failure

### Correct Example (parametric test):
```java
@ParameterizedTest
@ValueSource(strings = {"Integer", "String", "Long", "Double", "Float", "Boolean", "Byte", "Short", "Character"})
public void testBasicTypes(String typeName) {
    TypeInformation<?> typeInfo = TypeInfoParser.parse(typeName);
    assertNotNull("Failed to parse type: " + typeName, typeInfo);
}
```

### Incorrect Example (only testing two types):
```java
@Test
public void testBasicTypes() {
    TypeInformation<?> intType = TypeInfoParser.parse("Integer");
    assertNotNull(intType);
    TypeInformation<?> stringType = TypeInfoParser.parse("String");
    assertNotNull(stringType);
    // Missing: Long, Double, Float, Boolean, Byte, Short, Character
}
```
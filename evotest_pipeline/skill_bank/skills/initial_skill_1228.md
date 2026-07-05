---
name: creator-property-type-validation
description: When deserializing beans with constructor-based or factory-method-based
  creators, the TG should write tests that verify all property types (including primitives
  like int, long, String) are correctly bound via their @JsonProperty annotations,
  not just a subset. This catches bugs where type-specific handling in CreatorCollector
  fails for certain types like primitives.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
- STATE_MUTATION
- VALIDATION
- TYPE_CONVERSION
test_pattern: PARAMETRIC_TEST
---

# creator-property-type-validation

## Instructions

# Creator Property Type Validation

## Instructions

- WHEN the TG encounters a bean class that uses a constructor or static factory method with `@JsonProperty` annotations to define creator properties, and that bean has properties of **different types** (e.g., a primitive `int` field and a `String` field, or a primitive `long` and a `String`)
- THEN the TG should write a **parametric test** that deserializes JSON containing **all** property types simultaneously, and assert that each property is correctly deserialized. Do NOT test only one property type in isolation.
- Concrete example: For a bean `SimplePojo` with `int intField` and `String stringField`, the test should deserialize `{"intField": 1, "stringField": "foo"}` and verify both `getIntField() == 1` and `getStringField().equals("foo")`. On the buggy version, this should produce an exception `JsonMappingException` with a message containing "Could not find creator property with name 'intField'".
- Common pitfalls to avoid:
  - Testing only `String`-typed properties while ignoring primitive (`int`, `long`, etc.) properties
  - Testing only a single property in isolation instead of all properties together in one deserialization call
  - Assuming that if one property type works, all property types work (the bug specifically causes primitive properties to fail while String properties succeed)
  - Not checking the specific error message "Could not find creator property with name" on the buggy version
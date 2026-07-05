---
name: json-ignore-fields-property-resolver-type
description: When filtering JSON properties using @JsonIgnoreProperties or related
  annotations that accept property names, the TG should test that both String property
  names and CtTypeReference type-based keys are properly resolved and returned, as
  bugs occur when internal maps mix types.
code_tags:
- EXCEPTION_HANDLING
- TYPE_CONVERSION
test_pattern: STATE_TEST
---

# json-ignore-fields-property-resolver-type

## Instructions

# JsonIgnoreFields PropertyResolver Type Handling

## Instructions

- WHEN the TG encounters a JSON serialization/deserialization class that implements a `PropertyResolver` or contains internal maps (like `HashMap<String, ...>`) storing property names from annotations such as `@JsonIgnoreProperties`, `@JsonIgnoreType`, or similar
  - THEN the TG should test that the `findPropertiesFor()` (or equivalent property resolution method) correctly handles both `String`-typed property names AND `CtTypeReference`-typed keys when they are passed as arguments
  - Specifically, create a test that:
    1. Sets up the serializer/deserializer context with ignored property names (Strings)
    2. Sets up the same context with class-based type references (e.g., `CtTypeReference<SomeClass>`)
    3. Calls the property resolution method (e.g., `findPropertiesFor(String.class)`)
    4. Verifies that both types of properties are returned and that no `ClassCastException` or missing-property error occurs
  - Common pitfalls to avoid:
    - Testing only with `String` type property names and assuming all internal maps use `String` keys
    - Not testing with `CtTypeReference` or other class-based type objects that may be stored alongside `String` keys
    - Assuming `HashMap<Object, Object>` or raw maps are not used internally
    - Not covering the case where properties are filtered during constructor-based deserialization (e.g., `testConstructorMap` scenario)

- Example correct test (pseudocode):
```java
// Given a PropertyResolver with both String and CtTypeReference entries
PropertyResolver resolver = new SomePropertyResolver();
resolver.addIgnored("propertyName"); // String key
resolver.addIgnored(new CtTypeReference<MyClass>()); // CtTypeReference key

// When finding properties for a type
Map<String, Property> result = resolver.findPropertiesFor(String.class);

// Then both ignored entries should be handled without ClassCastException
assertNotNull(result);
// Verify string-based property is filtered
assertFalse(result.containsKey("propertyName"));
```

- Example incorrect test (common pitfall):
```java
// ❌ BAD: Only tests String-based property names
PropertyResolver resolver = new SomePropertyResolver();
resolver.addIgnored("propertyName");
Map<String, Property> result = resolver.findPropertiesFor(String.class);
// This would miss the bug where CtTypeReference keys cause ClassCastException
```
---
name: json-to-xml-type-handling
description: When converting JSON values to XML, different types (String, Number,
  Boolean) must be handled separately. Tests should verify that type information is
  preserved correctly during serialization, especially for mixed-type values like
  dates versus strings.
code_tags:
- VALIDATION
- TYPE_CONVERSION
- STATE_MUTATION
test_pattern: PARAMETRIC_TEST
---

# json-to-xml-type-handling

## Instructions

# JSON-to-XML Type Handling

## Instructions

- WHEN the TG encounters a JSON-to-XML conversion method that handles multiple value types (String, Number, Boolean, Array, Object)
- THEN it should write parametric tests that:
  1. For each JSON value type (String, Number, Boolean), verify the XML output preserves the correct representation
  2. Test with String values that could be misinterpreted (e.g., "2023-01-15", "true", "123") to ensure they remain strings in the XML output
  3. Test with Number values (integers, decimals) to verify they are not converted to strings
  4. Test with Boolean values to verify they become XML text content, not wrapped in quotes
  5. Compare the actual XML output against expected XML strings using exact string matching
  6. When testing with objects/arrays that contain mixed types, verify each nested value is correctly typed in the XML output

- Common pitfalls to avoid:
  - Testing only with String values and assuming other types work the same way
  - Assuming JSON primitives like numbers and booleans are converted to their XML representation correctly without explicit verification
  - Testing only with simple flat objects instead of nested structures with mixed types
  - Not testing boundary values like empty strings, zero, or negative numbers

- Correct example (testing type differentiation):
```java
// For String values like date strings
String jsonStr = "{\"date\":\"2023-01-15\"}";
String expectedXml = "<root><date>2023-01-15</date></root>";
assertEquals(expectedXml, converter.toXml(jsonStr));

// For numeric values
String jsonNum = "{\"count\":123}";
String expectedNumXml = "<root><count>123</count></root>";
assertEquals(expectedNumXml, converter.toXml(jsonNum));
```

- Incorrect example (pitfall):
```java
// WRONG: Only testing with simple string values, assuming all types work identically
String json = "{\"name\":\"test\"}";
String result = converter.toXml(json);
assertTrue(result.contains("<name>test</name>"));
// Missing: test with numbers, booleans, mixed nested types
```
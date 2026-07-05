---
name: number-string-validation-in-swagger-yaml
description: When generating Swagger YAML from Java models, numeric fields (int, long,
  float, double) declared as String type in the model must be serialized as quoted
  strings in YAML output. Failing to quote them causes YAML parsers to interpret them
  as numeric types instead of strings.
code_tags:
- NULL_CHECK
- VALIDATION
- TYPE_CONVERSION
test_pattern: PARAMETRIC_TEST
---

# number-string-validation-in-swagger-yaml

## Instructions

# Number-as-String Validation in Swagger YAML Generation

## Instructions

- WHEN the TG encounters a test class named `SwaggerYamlGeneratorTest` (or any Swagger YAML generation test) and the focal method involves generating a YAML representation of model properties,
  - THEN the TG should verify that numeric-looking string values (e.g., `"123"`, `"3.14"`) are correctly serialized as quoted YAML strings, not as numeric YAML scalars.
  - Write a test that creates a model object with a field typed as `String` but assigned a numeric value (e.g., `"123"` or `"-0.5"`), generates the YAML output from the model, and asserts that the output contains the value wrapped in quotes (e.g., `"123"` not just `123`).
  - Also test edge cases: `"0"`, `"-0"`, `"Infinity"`, and empty string `""` — these should all remain quoted strings.
  - Include the case of a field named `numberAsString` with value `"123"` in the model.
  - Common pitfall: The TG might test only non-numeric strings (e.g., `"foo"`) and miss that numeric-looking strings are the ones that get unquoted by the buggy YAML generator. Always include at least one numeric string value.

- WHEN the TG sees a code path that constructs a YAML property value from a Java model field's value (where the field type is `String`),
  - THEN the TG should verify that the resulting YAML renders the value in quotation marks `"..."` regardless of whether the string content is numeric.
  - The test should call the YAML generation method (e.g., `toYaml()` or `generate()` or similar) on the model object and check the resulting YAML string for quoted output.

### Correct test example (conceptual):
```java
@Test
public void testNumberAsStrings() {
    Model model = new Model();
    model.setNumberAsString("123");  // numeric string
    String yaml = SwaggerYamlGenerator.generate(model);
    assertTrue("Numeric string should be quoted in YAML", yaml.contains("\"123\""));
    assertFalse("Numeric string should NOT appear unquoted", yaml.contains("123"));  // careful: partial match
}
```

### Incorrect test (would not catch the bug):
```java
@Test
public void testNumberAsStrings() {
    Model model = new Model();
    model.setNumberAsString("foo");  // non-numeric — works in both buggy and fixed
    String yaml = SwaggerYamlGenerator.generate(model);
    assertTrue(yaml.contains("\"foo\""));
}
```

### Common pitfalls:
1. **Testing only non-numeric strings** — Alpha-only strings are always quoted; the bug is that numeric-looking strings lose their quotes.
2. **Using `contains` on a partial numeric match** — If the YAML contains `"1234"` and you check for `contains("123")`, it may match incorrectly. Test for the exact quoted string: `"\"123\""`.
3. **Forgetting edge cases** — Test `"0"`, `"-1.5"`, `"Infinity"`, and empty string `""`.
4. **Assuming all YAML generators quote all strings** — Some YAML serializers may unquote numeric strings for compactness; this bug is specifically about a Swagger YAML generator that should NOT do that for model fields typed as String.
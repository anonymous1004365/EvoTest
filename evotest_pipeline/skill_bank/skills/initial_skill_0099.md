---
name: final-field-interpolation-skipping
description: When code uses reflection to iterate over fields and skips final fields,
  the test generator should verify that non-final fields ARE interpolated and final
  fields are NOT, by testing with models containing both field types.
code_tags:
- FINAL_FIELD_INTERPOLATION
- REFLECTIVE_FIELD_PROCESSING
test_pattern: STATE_TEST
---

# final-field-interpolation-skipping

## Instructions

# Final Field Interpolation Skipping

## Instructions

- WHEN the TG encounters code that uses `Modifier.isFinal()` or similar logic to conditionally process object fields during interpolation/transformation (e.g., `if ( !Modifier.isFinal( currentField.getModifiers() ) )`)
- THEN the TG should write a test that:
  1. Creates a model object with BOTH a `final` field and a regular (non-final) field that contain interpolation placeholder values (e.g., `${some.value}`)
  2. Calls the interpolation method on that model
  3. Asserts that the non-final field's placeholder was replaced (interpolated) while the `final` field's placeholder remains unchanged (not interpolated)
- Use concrete field names and values from the actual model class under test
- The test should specifically check that the final field retains its exact original placeholder string after interpolation, while non-final fields get resolved
- Common pitfalls to avoid:
  - Testing only with non-final fields and assuming final fields are handled correctly
  - Asserting that final fields are cleared or set to null (verify the original value is preserved, not removed)
  - Forgetting to set up the model with actual interpolation placeholders in both field types
  - Not testing the specific `final` modifier behavior — testing only one field type is insufficient
  
### Correct example:
```java
@Test
public void testFinalFieldsExcludedFromInterpolation() {
    Model model = new Model();
    model.setArtifactId("test");
    // property value that could be used
    // Set a final field (like parent version) and non-final field  
    Parent parent = new Parent();
    parent.setVersion("${parentVersion}");
    model.setParent(parent);
    
    model.setVersion("${projectVersion}");
    
    StringSearchModelInterpolator interpolator = new StringSearchModelInterpolator();
    // ... interpolate with properties containing parentVersion=1.0, projectVersion=2.0
    
    // Final field (parent.version) should remain untouched
    assertEquals("${parentVersion}", model.getParent().getVersion());
    // Non-final field (model.version) should be interpolated
    assertEquals("2.0", model.getVersion());
}
```

### Incorrect example (missing final field check):
```java
@Test
public void testInterpolation() {
    Model model = new Model();
    model.setVersion("${projectVersion}");
    
    interpolator.interpolateModel(model, ...);
    
    assertEquals("2.0", model.getVersion());
    // WRONG: This test doesn't verify that final fields like parent.version
    // remain un-interpolated. The bug is that IF final fields WERE interpolated,
    // this test would still pass.
}
```
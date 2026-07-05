---
name: interfaceOnly-property-cleanup
description: When a boolean property like interfaceOnly is set to false, the test
  should verify it is properly removed/cleaned from additional properties to prevent
  stale state that could affect subsequent operations like template generation.
code_tags:
- VALIDATION
- STATE_MUTATION
test_pattern: STATE_TEST
---

# interfaceOnly-property-cleanup

## Instructions

# InterfaceOnly Property Cleanup Test

## Instructions

**WHEN** the TG encounters a code generator class that has a boolean property `interfaceOnly` (or similar boolean configuration flags) which, when set to `false`, should cause that property to be removed from an `additionalProperties` map or similar configuration state:

- **THEN** the TG should write a test that:
  1. First sets the property (e.g., `interfaceOnly`) to `true`
  2. Then sets the same property back to `false`
  3. Then verifies the property is no longer present in the additional properties map passed to templates (e.g., `additionalProperties()` does NOT contain the key `"interfaceOnly"`)
  4. Specifically test that `additionalProperties.containsKey("interfaceOnly")` returns `false` after setting the property to `false`

**WHEN** the property `interfaceOnly` is set to `true`:
- **THEN** the test should verify the property IS present in additional properties (as a positive control)

**Common pitfalls to avoid:**
- ❌ Testing only the "set to true" path without verifying cleanup when set back to false
- ❌ Testing the property value but not verifying its presence/absence in the additional properties map
- ❌ Assuming the default value of a boolean property doesn't affect the presence of the key in additional properties
- ❌ Not testing the state transition (true→false) to catch stale state bugs

**Correct example:**
```java
@Test
public void verify_that_interfaceOnly_is_removed_from_additional_properties_if_false() {
    // Given
    JavaJAXRSSpecServerCodegen codegen = new JavaJAXRSSpecServerCodegen();
    
    // When - set to true
    codegen.setInterfaceOnly(true);
    
    // Then - should be present
    assertTrue(codegen.additionalProperties().containsKey("interfaceOnly"));
    
    // When - set back to false
    codegen.setInterfaceOnly(false);
    
    // Then - should be removed
    assertFalse(codegen.additionalProperties().containsKey("interfaceOnly"));
}
```

**Incorrect example:**
```java
// BAD - Only tests that true adds to properties, but never tests false removes them
@Test
public void testInterfaceOnly() {
    JavaJAXRSSpecServerCodegen codegen = new JavaJAXRSSpecServerCodegen();
    codegen.setInterfaceOnly(true);
    assertTrue(codegen.additionalProperties().containsKey("interfaceOnly"));
}
```
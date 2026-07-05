---
name: callback-parameter-type-iteration
description: Teaches TG to test that when constructing JavaScript callback functions
  from mixed-type parameter arrays (e.g., Object[] containing both String and CtTypeReference
  values), each parameter is properly converted to its JavaScript string representation.
  Use this when behavior iterates over a template parameter array to build output.
code_tags:
- NULL_CHECK
- VALIDATION
- BOUNDARY_CHECK
- STRING_BUILDING
- ARRAY_ITERATION
test_pattern: PARAMETRIC_TEST
---

# callback-parameter-type-iteration

## Instructions

# Callback Parameter Type Iteration

## Instructions

- WHEN the TG encounters code that constructs a JavaScript callback function string by iterating over a `CallbackParameter` array (typically `Object[] params`) where each element can be either a `String` or a `CtTypeReference` (or similar type-representing object that must be stringified differently)
- THEN the TG should write a parameterized test that passes a heterogeneous array containing BOTH:
  - A `String` parameter (e.g., `"{foo}"`)
  - A typed parameter (e.g., `CallbackParameter.converted("bar", someTypeReference)`) that gets converted to a string like `"bar"`
  - Verify the final JavaScript callback string includes BOTH values correctly formatted (e.g., `"function(){...}"`)
  - If only `String` parameters are tested, the test may pass on buggy code even though `CtTypeReference` typed parameters produce malformed output, so test with at least one of each type

- Common pitfalls:
  - Testing only `String` type parameters, which would not expose the bug where `CtTypeReference` values are not properly stringified
  - Assuming all parameters in the array are of the same type
  - Forgetting to verify that the final callback output is syntactically valid JavaScript (e.g., contains `function()`, proper quoting, no stray characters)

- Example of a correct test:
  ```java
  @Test
  public void testCallbackFunctionWithMixedParameterTypes() {
      // Given
      CallbackParameter stringParam = CallbackParameter.explicit("{foo}");
      CallbackParameter convertedParam = CallbackParameter.converted("bar", SomeTypeReference.get());
      AbstractDefaultAjaxBehavior behavior = new AbstractDefaultAjaxBehavior() {
          @Override
          protected void respond(AjaxRequestTarget target) {}
      };
      behavior.setCallbackParameters(stringParam, convertedParam);
      
      // When
      String callback = behavior.getCallbackFunction().toString();
      
      // Then
      assertTrue("Callback should contain the string parameter value", callback.contains("{foo}"));
      assertTrue("Callback should contain the converted parameter value", callback.contains("bar"));
      // The string should be valid JavaScript
      assertTrue("Callback should be a valid JavaScript function", callback.startsWith("function("));
  }
  ```

- Example of an INCORRECT test (would miss the bug):
  ```java
  @Test
  public void testCallbackFunctionWithOnlyStringParams() {
      // Only tests String parameters — won't catch the bug!
      CallbackParameter param = CallbackParameter.explicit("{foo}");
      // ... test passes but doesn't verify typed parameter rendering
  }
  ```
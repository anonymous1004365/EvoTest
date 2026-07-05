---
name: template-parameter-type-validation
description: When handling proxy template parameters with mixed types (String and CtTypeReference), validate all parameter types uniformly to prevent ClassCastException. Use this skill when a method processes template/index parameters that can be either String or a specific type reference.
code_tags: ['EXCEPTION_HANDLING', 'VALIDATION', 'NULL_CHECK']
test_pattern: EXCEPTION_TEST
---

# template-parameter-type-validation

## Instructions

# Template Parameter Type Validation

## Instructions

- WHEN the TG encounters a method that accepts template parameters or index arguments that can be either a `String` or a `CtTypeReference` (or similar type reference classes) AND the method casts or processes these parameters assuming a single type
  - THEN the TG should write a test that passes BOTH types of arguments to the method and verifies no `ClassCastException` is thrown
  - Include a test where the parameter is a `String` type AND a test where the parameter is a `CtTypeReference` type (or the alternative type reference class)
  - Verify that the method handles both types correctly by checking the returned/processed value
  - If the method is expected to throw an exception for unsupported types, verify the correct exception type (not `ClassCastException`)

- WHEN a method uses `instanceof` checks or type casting (`(String) param`) without exhaustively covering all possible input types
  - THEN the TG should identify all concrete types that can be passed to the method and add test cases for each type
  - Common pitfalls: testing only one type (e.g., only `String`) and missing the alternative type (e.g., `CtTypeReference`), which would cause a `ClassCastException` at runtime

- EXAMPLES:
  - Correct test pattern:
    ```java
    @Test
    public void testMixedParameterTypes() {
        ProxyTemplate proxy = createProxyWithTemplate();
        // Test with String parameter
        proxy.addNamedTemplateParameter("key", "value");
        assertEquals("value", proxy.getTemplateParameter("key"));
        
        // Test with CtTypeReference parameter  
        CtTypeReference<String> typeRef = factory.Type().createReference(String.class);
        proxy.addNamedTemplateParameter("key2", typeRef);
        assertEquals(typeRef, proxy.getTemplateParameter("key2"));
    }
    ```

  - Incorrect test pattern (only tests String, misses ClassCastException):
    ```java
    @Test
    public void testOnlyStringParameters() {
        ProxyTemplate proxy = createProxyWithTemplate();
        proxy.addNamedTemplateParameter("key", "value");
        // Missing: CtTypeReference parameter test
        // Bug: when CtTypeReference is passed, ClassCastException occurs
    }
    ```

- WHEN writing assertions for template parameter validation tests
  - THEN assert both that no exception is thrown AND that the returned object matches the expected type/value
  - For negative tests, explicitly catch `ClassCastException` and fail the test with a descriptive message
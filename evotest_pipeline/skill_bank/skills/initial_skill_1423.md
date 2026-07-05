---
name: template-parameter-type-validation
description: When a method validates parameters before processing typed values (like
  URI template arguments), teach the TG to test with all accepted types to ensure
  no parameter type causes a state-mutating skip. This skill prevents tests that miss
  type-related validation branches.
code_tags:
- STATE_MUTATION
- VALIDATION
test_pattern: STATE_TEST
---

# template-parameter-type-validation

## Instructions

# Template Parameter Type Validation

## Instructions

- WHEN the TG encounters a method that iterates over URI template parameters (e.g., replacing `{param}` placeholders) and the method body explicitly checks the type of each parameter value (e.g., `if (value instanceof String)` or similar type-specific branching)
- THEN the TG should write a test that supplies at least one parameter of **each type** that the method is expected to handle (e.g., a `String` value AND an alternative type like an object of `CtTypeReference` or a custom wrapper), verifying that the state mutation (e.g., clearing a stored value) still occurs correctly for **each type**
- Specifically, the TG should simulate a scenario where a URI template contains the same `{param}` placeholder twice. The test should call the method to process the template, then assert that after processing, the internal state (such as a stored template or a "value cleared" flag) is correctly updated regardless of the parameter type. Expect that a buggy version might skip the state mutation for non-`String` types, leaving stale data.
- Common pitfalls to avoid:
  - **Testing only `String` type parameters**: The bug may only manifest when parameters are of a non-`String` type (e.g., `CtTypeReference`). The TG must test with at least two different parameter types, not just one.
  - **Not verifying the resulting state**: The TG should not just check the output of the method but also inspect an internal state variable that tracks whether the value was cleared or updated.
  - **Assuming all branches are covered with one test case**: Write separate test cases or parameterized tests to cover each type explicitly.

### Example (Correct)

Assume the following class under test:

```java
public class TemplateProcessor {
    // A set of placeholder names whose values have been "cleared"
    private Set<String> clearedParams = new HashSet<>();

    public String processTemplate(String template, Map<String, Object> params) {
        for (Map.Entry<String, Object> entry : params.entrySet()) {
            String paramName = entry.getKey();
            Object paramValue = entry.getValue();
            if (template.contains("{" + paramName + "}")) {
                // BUGGY: only clears if value is String
                // if (paramValue instanceof String) { clearedParams.add(paramName); }
                // FIXED: always clears
                clearedParams.add(paramName);
                template = template.replace("{" + paramName + "}", paramValue.toString());
            }
        }
        return template;
    }

    public boolean isParamCleared(String paramName) {
        return clearedParams.contains(paramName);
    }
}
```

A correct test for this scenario would be:

```java
@Test
public void testProcessTemplateWithNonStringParam() {
    // Given a template with a placeholder and a non-String parameter value
    String template = "Hello {name}!";
    Map<String, Object> params = new HashMap<>();
    params.put("name", new CtTypeReference<>()); // non-String type
    
    TemplateProcessor processor = new TemplateProcessor();
    
    // When processing the template
    processor.processTemplate(template, params);
    
    // Then the param should be marked as cleared
    assertTrue("Should mark param as cleared for non-String types", 
               processor.isParamCleared("name"));
}
```

### Example (Incorrect)

```java
@Test
public void testProcessTemplateWithStringParam() {
    // This test only covers String types and would not catch the bug
    String template = "Hello {name}!";
    Map<String, Object> params = new HashMap<>();
    params.put("name", "World");
    
    TemplateProcessor processor = new TemplateProcessor();
    processor.processTemplate(template, params);
    
    assertTrue("Should mark param as cleared for String types", 
               processor.isParamCleared("name"));
}
```
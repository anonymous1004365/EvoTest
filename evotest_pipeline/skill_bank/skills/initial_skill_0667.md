---
name: properties-concatenation-default-value
description: When testing properties component concatenation with default values,
  ensure the test sets system properties only for the required prefix and verifies
  that concatenated properties resolve their default placeholders correctly, not just
  the first token.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- NULL_CHECK
- STATE_MUTATION
- ORDER_DEPENDENCY
test_pattern: PARAMETRIC_TEST
---

# properties-concatenation-default-value

## Instructions

# Properties Concatenation with Default Values

## Instructions

- WHEN the TG encounters a `PropertiesComponent` that uses concatenation syntax (e.g., `{{prefix.key}}` combined with `{{key.suffix}}`) and the test involves setting system properties as overrides
- THEN the TG should ensure that:
  1. System properties are set ONLY for the specific prefix being tested (e.g., `concat.another=foo`) — NOT for the full concatenated key
  2. The test verifies that the concatenated property resolves ALL of its constituent tokens, including default values (e.g., `{{concat.value1}}other{{concat.value2}}` should resolve to `someotherthing`)
  3. The test uses `context.addComponent("properties", new PropertiesComponent("classpath:concatenation.properties"))` and creates a route that uses the property placeholder in an endpoint URI
  4. The test checks the final endpoint URI using `getMockEndpoint("mock:{{...}}")` or by inspecting the route context after creation

- WHEN the TG tests property concatenation with default values for tokens that are NOT set as system properties
- THEN the test must set the *individual token prefix* as a system property (e.g., `System.setProperty("concat.another", "foo")`) rather than the full compound key, and verify that the route endpoint is correctly resolved with the concatenation including defaults

- Common pitfalls to avoid:
  - Setting system properties for the full compound key instead of individual tokens
  - Testing only the first token and ignoring second/third tokens in concatenation
  - Not verifying that default values from the properties file are properly resolved alongside system property overrides
  - Testing with `PropertiesResolver` directly (low-level) instead of using the DSL route builder + `context.addComponent`

### Correct Example (catches the bug):
```java
@Test
public void testConcatPropertiesComponentDefault() throws Exception {
    System.setProperty("concat.another", "foo");
    context.addComponent("properties", new PropertiesComponent("classpath:concatenation.properties"));
    context.addRoutes(new RouteBuilder() {
        @Override
        public void configure() throws Exception {
            from("direct:start").to("{{concat.value1}}other{{concat.value2}}");
        }
    });
    context.start();
    // Verify the route resolves correctly
    getMockEndpoint("mock:someotherthing").expectedMessageCount(1);
    template.sendBody("direct:start", "Hello World");
    assertMockEndpointsSatisfied();
}
```

### Incorrect Example (misses the bug):
```java
@Test
public void testIncorrect() throws Exception {
    // BUG: Only tests first token, or sets system property for the full key
    System.setProperty("concat.value1", "some");
    // Missing: System.setProperty("concat.another", "foo") for the second token
    // or: sets System.setProperty("concat.value1other{{concat.value2}}", "wrong") 
    // The concatenated property with default {{concat.value2}} won't resolve correctly
}
```
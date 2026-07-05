---
name: route-property-placeholder-transacted-interaction
description: When property placeholders (e.g., {{key}}) are used in routes that also
  have transacted policies or interceptors, placeholders may remain unresolved (e.g.,
  {{cool.name}} instead of "Camel"). Tests should verify placeholder resolution in
  combination with other route configurations like policy(), interceptFrom(), or transacted().
code_tags:
- NULL_CHECK
- STATE_MUTATION
- VALIDATION
test_pattern: INTERACTION_TEST
---

# route-property-placeholder-transacted-interaction

## Instructions

# Route Property Placeholder Transacted Interaction

## Instructions

- WHEN the TG encounters a route definition that uses property placeholders (e.g., `{{cool.name}}`) in combination with transacted policies (`policy(new MyPolicy())`), interceptors (`interceptFrom()`), or other route configuration that might interfere with property placeholder resolution
- THEN it should write a test that sends a message through the route and verifies that the placeholder has been resolved correctly in the output (e.g., the body of the final message is `"Camel"` not `"{{cool.name}}"`)
- The test should:
  1. Set up a CamelContext with a `PropertiesComponent` pointing to a `.properties` file that defines the placeholder key (e.g., `cool.name=Camel`)
  2. Configure the route with a transacted policy and/or interceptors that use the placeholder
  3. Send a message to the route's input endpoint
  4. Assert that the mock endpoint receives the resolved value (e.g., `mock:result` expects body `"Camel"`)
  5. Expect the failure: on the **buggy** version, the placeholder remains unresolved (body is `{{cool.name}}` instead of the expected value)
- Common pitfalls to avoid:
  - **Testing placeholders without transacted/interceptor configuration**: The bug only manifests when property placeholders interact with transacted policies and interceptors. Testing just `{{cool.name}}` in a simple route may pass on both buggy and fixed versions.
  - **Using only String type for mock expectations**: Use `expectedBodiesReceived()` with the exact resolved string value, not regex patterns or contains matchers.
  - **Forgetting to add properties file to the test resources**: The `.properties` file must exist in the classpath (e.g., `src/test/resources/org/apache/camel/component/properties/myproperties.properties`) and the `PropertiesComponent` must be configured with the correct location.

### Correct test pattern (simplified):

```java
// Setup CamelContext with PropertiesComponent
context.addComponent("properties", new PropertiesComponent("classpath:org/apache/camel/component/properties/myproperties.properties"));

// Route definition with transacted policy + interceptor using placeholder
context.addRoutes(new RouteBuilder() {
    public void configure() throws Exception {
        interceptFrom().to("mock:intercepted");
        from("direct:start")
            .policy(new MyPolicy())
            .to("{{cool.name}}")
            .to("mock:result");
    }
});

// Send message and verify
template.sendBody("direct:start", "test");
mockResult.expectedBodiesReceived("Camel");  // NOT "{{cool.name}}"
mockResult.assertIsSatisfied();
```

### Incorrect test pattern (weak verification):

```java
// ❌ Testing placeholder in isolation without transacted policy
context.addRoutes(new RouteBuilder() {
    public void configure() throws Exception {
        from("direct:start")
            .to("mock:result");
    }
});
// This would pass on both buggy and fixed versions, missing the bug entirely
```
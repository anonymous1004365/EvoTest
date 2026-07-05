---
name: intercept-from-multiple-uri-registration
description: When registering multiple interceptFrom definitions with different URIs,
  the second definition's URI gets corrupted or merged. This skill teaches how to
  test that each interceptFrom URI is independently registered and managed via JMX
  without state leaking between registrations.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- NULL_CHECK
- STATE_MUTATION
test_pattern: STATE_TEST
---

# intercept-from-multiple-uri-registration

## Instructions

# InterceptFrom URI State Leakage on Multiple Registration

## Instructions

- WHEN the code creates multiple `interceptFrom` definitions with different URI values (e.g., "direct:start" and "direct:foo") and registers them in a `CamelContext` that supports JMX management
- THEN the test MUST verify that each interceptFrom definition preserves its own URI independently. Specifically, the test should:
  1. Create a route with at least two different `interceptFrom(...)` definitions, each with a distinct URI (e.g., `interceptFrom("direct:start")` and `interceptFrom("direct:foo")`)
  2. Use `ManagedCamelContext` MBean to retrieve the `InterceptFromDefinition` objects via JMX (e.g., using `context.getManagementStrategy()` or `managedCamelContext.getObjectName("*:type=intercepts,*")`)
  3. Assert that each `InterceptFromDefinition` returned from management has the **correct, distinct URI** that matches what was originally defined
  4. Assert that the number of interceptFrom definitions returned matches the number that was defined (e.g., expect 2, not 1)
- The bug occurs because the state of the second interceptFrom definition **overwrites** the first when both are registered for management, due to incorrect state sharing or a missing copy/clone during registration
- Common pitfalls:
  - Testing only a single interceptFrom definition — this does NOT catch the bug
  - Testing interceptFrom with the same URI twice — the bug only manifests with **different** URIs
  - Forgetting to check the **actual URI value** in the managed object, not just the count
  - Assuming that `context.getInterceptFromDefinitions()` returns independent copies rather than shared references
  - Relying on `toString()` or `getLabel()` of the definition instead of the explicit `getUri()` method

### Correct Example (catches the bug):
```java
// In ManagedInterceptFromTest
@Test
public void testManageWithInterceptFrom() throws Exception {
    context.addRoutes(new RouteBuilder() {
        @Override
        public void configure() throws Exception {
            interceptFrom("direct:start").to("mock:intercepted");
            interceptFrom("direct:foo").to("mock:intercepted");
            from("direct:start").to("mock:result");
        }
    });
    context.start();

    // Get managed interceptFrom definitions via MBeanServer
    ObjectName on = new ObjectName("org.apache.camel:type=intercepts,*");
    Set<ObjectName> names = getMBeanServer().queryNames(on, null);
    assertEquals("Expected 2 interceptFrom definitions", 2, names.size());

    for (ObjectName name : names) {
        String uri = (String) getMBeanServer().getAttribute(name, "Uri");
        assertNotNull("URI should not be null", uri);
        assertTrue("URI should be one of the defined URIs",
            uri.equals("direct://start") || uri.equals("direct://foo"));
    }
}
```

### Incorrect Example (misses the bug):
```java
// BAD: only tests one interceptFrom, doesn't catch inter-URI state corruption
@Test
public void testManageWithInterceptFrom() throws Exception {
    context.addRoutes(new RouteBuilder() {
        @Override
        public void configure() throws Exception {
            interceptFrom("direct:start").to("mock:intercepted");
            from("direct:start").to("mock:result");
        }
    });
    context.start();

    ObjectName on = new ObjectName("org.apache.camel:type=intercepts,*");
    Set<ObjectName> names = getMBeanServer().queryNames(on, null);
    assertEquals("Expected 1 interceptFrom definition", 1, names.size());
}
```
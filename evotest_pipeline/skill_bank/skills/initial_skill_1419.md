---
name: update-route-from-xml-marshalling-failure
description: When testing JMX operations that update routes from XML, the XML may
  reference classes not on the classpath, causing JAXBException wrapped as a route
  update failure. This skill teaches how to test that such marshalling failures are
  properly translated to meaningful exceptions (e.g., IllegalArgumentException) rather
  than raw JAXBException.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- NULL_CHECK
- MARSHALLING_UNMARSHALLING_ERROR
test_pattern: EXCEPTION_TEST
---

# update-route-from-xml-marshalling-failure

## Instructions

# Managed Route XML Update Marshalling Failure Handling

## Instructions

- WHEN the TG encounters a JMX MBean operation that updates a route from XML (e.g., `updateRouteFromXml(String xml)` on a `ManagedRoute`), and the code executes an XML unmarshalling step internally
- THEN the TG should write a test that:
  1. Provides XML input containing route definitions that reference classes NOT on the classpath (e.g., a custom `RouteDefinition` extension that doesn't exist), OR XML with mismatched route IDs that cause validation to fail during the unmarshalling process
  2. Verifies that a specific, meaningful exception type is thrown (e.g., `java.lang.IllegalArgumentException`) rather than a low-level `javax.xml.bind.JAXBException`
  3. Checks the failure message contains context about the root cause (e.g., the route ID mismatch message)
- Include the following concrete steps:
  - **First, verify the JMX MBean operation signature**: confirm the method takes a `String xml` parameter and delegates to XML unmarshalling
  - **Then, prepare test XML** that either (a) references missing classes in `jaxb.index`, or (b) contains a route element with an `id` attribute that doesn't match the managed route's ID (e.g., `<route id="myRoute" xmlns="http://camel.apache.org/schema/spring">...`)
  - **Use JMX invocation** to call the operation via `mbeanServer.invoke(objectName, "updateRouteFromXml", new Object[]{xml}, new String[]{"java.lang.String"})`
  - **Expect an `IllegalArgumentException`** (or a subclass like `javax.management.MBeanException` wrapping it) — DO NOT expect a `JAXBException`
  - **Assert the exception message** contains a meaningful description of what went wrong (e.g., "route mismatch" or the specific validation error)
- **Common pitfalls to avoid**:
  - ❌ Testing only with valid XML that always succeeds — this misses the error-handling behavior entirely
  - ❌ Expecting `JAXBException` directly — the bug shows that the wrapping mechanism might fail to translate it properly
  - ❌ Using `@Test(expected = JAXBException.class)` — the buggy version leaks the marshalling exception instead of throwing a clean `IllegalArgumentException`
  - ❌ Not configuring the classloader for JAXB context initialization — ensure the test classpath doesn't have the referenced classes

### Correct Example (minimized):
```java
@Test
public void testUpdateRouteFromXmlMismatchRouteId() throws Exception {
    // Given: a managed route with a specific ID
    String routeId = context.getRoutes().iterator().next().getId();
    
    // When: XML with a DIFFERENT route ID is provided
    String xml = "<route id=\"" + routeId + "XXX\" xmlns=\"http://camel.apache.org/schema/spring\">"
        + "  <from uri=\"direct:start\"/>"
        + "  <to uri=\"mock:end\"/>"
        + "</route>";
    
    // Then: an IllegalArgumentException should be thrown, not a JAXBException
    try {
        mbeanServer.invoke(on, "updateRouteFromXml", new Object[]{xml}, new String[]{"java.lang.String"});
        fail("Should throw exception");
    } catch (Exception e) {
        assertTrue(e.getCause() instanceof IllegalArgumentException);
    }
}
```

### Incorrect Example (pitfall):
```java
@Test(expected = JAXBException.class)  // WRONG: expects the wrong exception type
public void testUpdateRouteFromXmlBadXml() throws Exception {
    String xml = "<invalid-xml>";
    mbeanServer.invoke(on, "updateRouteFromXml", new Object[]{xml}, new String[]{"java.lang.String"});
}
```
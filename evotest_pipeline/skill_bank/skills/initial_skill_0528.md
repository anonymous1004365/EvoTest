---
name: route-xml-update-id-validation
description: When updating a route from XML via JMX, the new route's ID must match
  the existing route's ID. Tests should verify that an IllegalArgumentException is
  thrown on ID mismatch, not that the route update silently fails or causes runtime
  exceptions like FailedToStartRouteException.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
- RESOURCE_MANAGEMENT
- VALIDATION
- EXCEPTION_HANDLING
- STATE_MUTATION
test_pattern: EXCEPTION_TEST
---

# route-xml-update-id-validation

## Instructions

# Route XML Update ID Mismatch Validation

## Instructions

- WHEN the TG encounters a method that updates a route from XML (e.g., `updateRouteFromXml(String xml)` on `ManagedRoute`), and the XML contains a route ID that does NOT match the current route's ID
- THEN the TG should write a test that:
  1. Starts a route with a specific route ID (e.g., `route1`)
  2. Invokes `updateRouteFromXml` with XML that defines a **different** route ID (e.g., `route2`)
  3. Asserts that an `IllegalArgumentException` is thrown (not `FailedToStartRouteException` or any other exception)
  4. The assertion should catch `IllegalArgumentException` specifically, not a generic `Exception`
  5. Verifies that `route1` remains stopped (or in its original state) after the failed update

- Common pitfalls to avoid:
  - ❌ Testing only the happy path where the route ID matches in the XML
  - ❌ Catching a generic `Exception` instead of the specific `IllegalArgumentException`
  - ❌ Assuming the route update will silently fail — the bug shows that without proper validation, a mismatched route ID leads to a `FailedToStartRouteException` (a runtime error), not the expected `IllegalArgumentException`
  - ❌ Not stopping the route before calling `updateRouteFromXml` — the update operation requires the route to be in a stopped state

- Correct example:
```java
// Stop the route first
mbeanServer.invoke(objectName, "stop", null, null);

// XML with MISMATCHED route ID
String xml = "<routes><route id=\"route2\">..."
    + "</route></routes>";

// Expect IllegalArgumentException on ID mismatch
try {
    mbeanServer.invoke(objectName, "updateRouteFromXml",
        new Object[]{xml}, new String[]{"java.lang.String"});
    fail("Should throw IllegalArgumentException");
} catch (Exception e) {
    assertIsInstanceOf(IllegalArgumentException.class, e.getCause());
}
```

- Incorrect example:
```java
// ❌ Wrong: not stopping the route first
// ❌ Wrong: not checking for the specific exception type
mbeanServer.invoke(objectName, "updateRouteFromXml",
    new Object[]{xml}, new String[]{"java.lang.String"});
// The test passes but no validation occurs — route gets into a broken state
```
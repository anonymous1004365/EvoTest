---
name: proxy-builder-skip-java-lang-object-methods
description: When testing proxy builders that create dynamic proxies for interfaces,
  verify that java.lang.Object methods (toString, hashCode, equals) are skipped during
  routing and not sent to the Camel endpoint. This skill teaches how to test that
  Object class methods on proxy interfaces are handled correctly.
code_tags:
- NULL_CHECK
- STATE_MUTATION
- INHERITANCE
test_pattern: INTERACTION_TEST
---

# proxy-builder-skip-java-lang-object-methods

## Instructions

# Testing Proxy Builder Skip Java Lang Object Methods

## Instructions

WHEN the TG encounters a `ProxyBuilder` or `ProxyHelper.createProxy()` that creates a dynamic proxy for an interface using Camel endpoints (`CamelContext` + `Endpoint`), THEN it should verify that invocations of `java.lang.Object` methods (specifically `toString()`, `hashCode()`, and `equals(Object)`) on the proxy instance do NOT trigger Camel message routing to the endpoint.

WHEN the proxy's `InvocationHandler` (e.g., `AbstractCamelInvocationHandler`) delegates method calls to a Camel endpoint, THEN the TG should test that:

1. **`toString()` on the proxy** returns a meaningful string representation (e.g., "Proxy[...]") instead of sending a message to the endpoint or throwing an exception.
2. **`hashCode()` on the proxy** returns an integer value (consistent with the proxy's identity) instead of sending a message to the endpoint.
3. **`equals(Object)` on the proxy** performs identity comparison (reference equality) instead of routing to the endpoint.

WHEN the interface being proxied declares its own `toString()`, `hashCode()`, or `equals(Object)` methods (these are the same signatures as `java.lang.Object` methods), THEN the TG should test that those methods ARE routed to the endpoint (since they are interface-declared overrides, not plain Object methods).

Common pitfalls:
- **Assuming all proxy method calls route to the endpoint**: `Object` methods like `toString()`, `hashCode()`, `equals(Object)` should NOT be routed; they are handled locally by the invocation handler.
- **Not testing edge cases**: Test both `toString()` (no args), `hashCode()` (no args), and `equals(Object)` (one arg) separately.
- **Forgetting to verify return types**: `toString()` must return a `String`, `hashCode()` must return an `int`, `equals(Object)` must return a `boolean`.
- **Not setting up a mock route/endpoint**: Use a `MockEndpoint` to assert that NO messages were received when calling Object methods, but that a real business method DOES send a message.

### Correct example (Java with Camel)

```java
public class ProxyBuilderSkipJavaLangObjectMethodsTest extends ContextTestSupport {

    public interface MyProxy {
        String sayFoo();
        String toString();
        int hashCode();
        boolean equals(Object obj);
    }

    public void testSayFoo() throws Exception {
        MockEndpoint mock = getMockEndpoint("mock:result");
        mock.expectedBodiesReceived("Hello World");

        MyProxy proxy = new ProxyBuilder(context)
            .endpoint("direct:foo")
            .build(MyProxy.class);

        // Business method should route
        String reply = proxy.sayFoo();
        assertEquals("Hello World", reply);
        mock.assertIsSatisfied();
    }

    public void testToString() throws Exception {
        MockEndpoint mock = getMockEndpoint("mock:result");
        mock.expectedMessageCount(0);

        MyProxy proxy = new ProxyBuilder(context)
            .endpoint("direct:foo")
            .build(MyProxy.class);

        // toString should NOT route to the endpoint
        String result = proxy.toString();
        assertNotNull(result);
        assertTrue(result.contains("Proxy"));
        mock.assertIsSatisfied();
    }

    public void testHashCode() throws Exception {
        MockEndpoint mock = getMockEndpoint("mock:result");
        mock.expectedMessageCount(0);

        MyProxy proxy = new ProxyBuilder(context)
            .endpoint("direct:foo")
            .build(MyProxy.class);

        // hashCode should NOT route to the endpoint
        int hash = proxy.hashCode();
        assertTrue(hash != 0);
        mock.assertIsSatisfied();
    }

    public void testEquals() throws Exception {
        MockEndpoint mock = getMockEndpoint("mock:result");
        mock.expectedMessageCount(0);

        MyProxy proxy = new ProxyBuilder(context)
            .endpoint("direct:foo")
            .build(MyProxy.class);

        // equals should NOT route to the endpoint
        boolean equal = proxy.equals(proxy);
        assertTrue(equal);
        mock.assertIsSatisfied();
    }
}
```

### Correct test structure (WHAT the TG should verify)

```java
// Set up the mock endpoint
MockEndpoint mock = getMockEndpoint("mock:result");
mock.expectedMessageCount(0);  // Expect NO messages

// Build the proxy
MyProxy proxy = new ProxyBuilder(context)
    .endpoint("direct:foo")
    .build(MyProxy.class);

// Invoke toString() - should NOT send to endpoint
String result = proxy.toString();
assertNotNull(result);

// Verify no messages were sent
mock.assertIsSatisfied();
```

### Incorrect approach (what the TG should NOT do)

```java
// WRONG: Setting up route but not verifying no messages for Object methods
MockEndpoint mock = getMockEndpoint("mock:result");

MyProxy proxy = new ProxyBuilder(context)
    .endpoint("direct:foo")
    .build(MyProxy.class);

// WRONG: Calling toString() but not checking that mock received 0 messages
String result = proxy.toString();

// WRONG: Only testing business methods, not Object methods
// Missing: toString(), hashCode(), equals() tests
```

### Key assertion points

- For `toString()`: assertNotNull, assertTrue(result.contains("Proxy")) - should return a descriptive string
- For `hashCode()`: assertTrue(hash != 0) - should return a non-zero hash code
- For `equals(Object)`: assertTrue(proxy.equals(proxy)) - should return true for self-comparison
- For `equals(null)`: assertFalse(proxy.equals(null)) - should return false for null
- For all: verify `mock.assertIsSatisfied()` with `expectedMessageCount(0)` to confirm NO routing occurred
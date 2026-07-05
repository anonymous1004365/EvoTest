---
name: namespace-mismatch-xpath-evaluation
description: WHEN validating that an XPath expression with namespace bindings correctly
  handles body elements that use a different namespace than the one declared in the
  route. THEN test with input XML whose namespace does NOT match the xpath namespace
  prefix binding, and verify that the XPath expression evaluates to null/no-match
  rather than incorrectly returning a value from a mismatched namespace.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- VALIDATION
- ARGUMENT_VALIDATION
test_pattern: STATE_TEST
---

# namespace-mismatch-xpath-evaluation

## Instructions

# Namespace Mismatch in XPath Evaluation

## Instructions

- WHEN the TG encounters code that sets an XPath-based expression (e.g., `.xpath("/c:number", Integer.class, ns)`) using a `Namespaces` object with a specific namespace URI and prefix binding, AND the route/processor applies this XPath to filter/extract data from the incoming message body
- THEN the TG SHOULD write a test where the incoming XML body uses a **different namespace** than the one declared in the XPath `Namespaces` binding. For example:
  - Declare `Namespaces ns = new Namespaces("c", "http://acme.com/cheese");`
  - Send a body with `<number xmlns="http://acme.com/cake">55</number>` (uses "cake", not "cheese")
  - Verify that the XPath evaluates correctly (returns null/no match for the header) and the body passes through unchanged
  - Specifically verify that `getIn().getHeader("foo")` is `null` (not set) when the namespaces do not match

- WHEN the TG writes such a test
- THEN it MUST:
  1. Create a `Namespaces` object with prefix `"c"` and URI `"http://acme.com/cheese"` (or similar)
  2. Use `.setHeader("foo").xpath("/c:number", Integer.class, ns)` in the route
  3. Send an XML body where the element uses a **different** namespace (e.g., `xmlns="http://acme.com/cake"`)
  4. Verify the body arrives unchanged at the mock endpoint
  5. Verify the header `"foo"` is NOT set (is `null`) — this is the key assertion
  6. Also test with a matching namespace to confirm the positive case still works

- Common pitfalls:
  - Testing only matching namespaces and never testing a mismatched namespace — this misses the bug
  - Assuming that when the XPath doesn't match, the header is still set to some default value — verify it's null
  - Not verifying both that the body passes through AND that the header is null — both are needed
  - Using the same namespace prefix (`"c"`) for both test cases but forgetting to change the actual XML namespace URI

**Correct test approach:**
```java
// Route sets up XPath with "c" -> "http://acme.com/cheese"
Namespaces ns = new Namespaces("c", "http://acme.com/cheese");
from("direct:in")
    .setHeader("foo").xpath("/c:number", Integer.class, ns)
    .to("mock:result");

// Test with DIFFERENT namespace (should NOT match)
MockEndpoint mock = getMockEndpoint("mock:result");
mock.expectedBodiesReceived("<number xmlns=\"http://acme.com/cake\">55</number>");
template.sendBody("direct:in", "<number xmlns=\"http://acme.com/cake\">55</number>");
mock.assertIsSatisfied();
assertNull(mock.getExchanges().get(0).getIn().getHeader("foo"));
```

**Incorrect approach:**
```java
// Only testing matching namespace — misses the bug entirely
Namespaces ns = new Namespaces("c", "http://acme.com/cheese");
mock.expectedBodiesReceived("<number xmlns=\"http://acme.com/cheese\">55</number>");
mock.expectedHeaderReceived("foo", 55);
template.sendBody("direct:in", "<number xmlns=\"http://acme.com/cheese\">55</number>");
// No test for namespace mismatch scenario!
```
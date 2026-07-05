---
name: raw-uri-parameter-parsing-trailing-characters
description: When testing URI parameters using RAW(value) syntax, test that special
  characters like ')' at the end of a RAW value are correctly preserved and not stripped.
  The parser must handle values ending with ')' that is part of the value vs the RAW()
  closing token.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- VALIDATION
- TYPE_CONVERSION
test_pattern: PARAMETRIC_TEST
---

# raw-uri-parameter-parsing-trailing-characters

## Instructions

# Testing RAW URI Parameter Value Boundaries

## Instructions

- WHEN the TG encounters code that parses URI query parameters with the `RAW(value)` syntax (where `RAW_TOKEN_START = "RAW("` and `RAW_TOKEN_END = ")"`)
- THEN it should test with a RAW parameter value that contains a closing parenthesis `)` as part of the actual value (e.g., `password=RAW(++%%w?rd))`)
  - The parser must distinguish between the `)` that ends the RAW token and the `)` that is part of the value
  - The expected resolved value should include the trailing `)` character (e.g., `++%%w?rd)` not `++%%w?rd`)
- The test should verify that the parameter value received by the endpoint is correctly stripped of the `RAW(...)` wrapper **while preserving** any `)` character that is part of the value itself
- Use a custom `DefaultComponent` subclass endpoint as the test target to simulate URI parameter parsing
- Common pitfalls to avoid:
  - Testing only with simple RAW values that don't contain `)` characters — this misses the boundary condition
  - Assuming that the `RAW(` token is always followed by a value without `)` characters
  - Testing only via the `URISupport.parseQuery()` method in isolation — the bug manifests through `DefaultComponent.createEndpoint()` which calls `URISupport.resolveRawParameterValues()`

### Correct Example (should detect the bug)
```java
// This test catches the bug: RAW(++%%w?rd)) with a trailing ) in the value
// The expected resolved value is "++%%w?rd)" (including the trailing parenthesis)
public void testRawUriParameter() throws Exception {
    getMockEndpoint("mock:result").expectedHeaderReceived("password", "++%%w?rd)");
    template.sendBody("direct:start", "Hello World");
    assertMockEndpointsSatisfied();
}
// Route: .to("mycomponent:foo?password=RAW(++%%w?rd))")
```

### Incorrect Example (misses the bug)
```java
// This test would pass even on the buggy version:
public void testRawUriParameter() throws Exception {
    getMockEndpoint("mock:result").expectedHeaderReceived("password", "++%%w?rd");
    template.sendBody("direct:start", "Hello World");
    assertMockEndpointsSatisfied();
}
// Route: .to("mycomponent:foo?password=RAW(++%%w?rd)")
```
The difference is subtle: the buggy version incorrectly strips the final `)` from `++%%w?rd)`, so testing with `++%%w?rd` (without the trailing `)`) would pass on both versions. The test must use a value ending with `)` to expose the bug.
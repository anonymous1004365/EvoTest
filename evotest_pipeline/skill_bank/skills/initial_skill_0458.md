---
name: endpoint-uri-normalization-mismatch
description: When an `interceptSendToEndpoint` pattern is matched against actual endpoint
  URIs, the pattern URI and runtime URI must be normalized identically before comparison.
  Use this skill when testing URI pattern matching logic where query parameters, schemes,
  or path components undergo normalization/encoding changes.
code_tags:
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# endpoint-uri-normalization-mismatch

## Instructions

# Endpoint URI Normalization Mismatch in Intercept Pattern Matching

## Instructions

**WHEN** the TG encounters code that matches an `interceptSendToEndpoint` URI pattern against runtime endpoint URIs — especially when the pattern URI contains characters that may be normalized differently (e.g., `+` in query parameter values, URL-encoded characters like `%2B`, trailing slashes, scheme case differences):

**THEN** the TG should write a test that demonstrates that the pattern matching works correctly with URIs that require normalization. Specifically:

1. **Test with a URI containing a `+` character in a query parameter value** (e.g., `mock:foo?myParam=Value+With+Plus`) as the pattern, and send a message to the same URI at runtime. Verify that the intercept fires (expect 1 message on the mock endpoint).

2. **Test with URL-encoded equivalents** (e.g., `mock:foo?myParam=Value%2BWith%2BPlus`) if the normalization should treat `+` and `%2B` equivalently.

3. **Verify that the match count is 1** — the bug is that the intercept silently fails to match (0 messages received) when the pattern URI contains characters that get normalized differently at runtime.

4. **Include both passing and failing scenarios** in parametric form when possible.

**Common pitfalls to avoid:**
- Testing only simple URI patterns (alphanumeric paths, no query params) — this misses the normalization bug
- Testing only the normalization method in isolation rather than the full `interceptSendToEndpoint` flow
- Assuming that `+` in query parameter values is preserved identically through URI normalization — it may be converted to `%2B` or handled differently
- Forgetting to call `skipSendToOriginalEndpoint()` to isolate the intercept behavior

### Correct Example (pseudocode)

```java
@Test
public void testInterceptWithPlusInQueryParam() throws Exception {
    // The pattern URI contains '+' which may be normalized
    context.getRouteDefinitions().get(0).adviceWith(context, new AdviceWithRouteBuilder() {
        @Override
        public void configure() {
            interceptSendToEndpoint("mock:foo?myParam=Value+With+Plus")
                .skipSendToOriginalEndpoint()
                .to("mock:intercept");
        }
    });

    getMockEndpoint("mock:intercept").expectedMessageCount(1);
    template.sendBody("direct:test", "test");
    assertMockEndpointsSatisfied();
}
```

### Incorrect Example (pitfall)

```java
// BAD: Only tests simple URI without query parameters
@Test
public void testInterceptSimple() throws Exception {
    // Simple path matching works, but doesn't catch normalization issues
    context.getRouteDefinitions().get(0).adviceWith(context, ...);
    // ... only tests "mock:simpleEndpoint"
    // This passes even on the buggy version, giving false confidence
}
```
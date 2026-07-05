---
name: mock-endpoint-uri-with-params
description: When writing tests that intercept and mock endpoints using adviceWith
  or mockEndpoints pattern, the URI match must include query parameters. Test that
  a mock endpoint pattern like "mock:foo?param=value" is matched as a full URI string,
  not decomposed into scheme:path + params parts.
code_tags:
- ADVICE_WITH_ROUTE_INTERCEPTION
- URI_MATCHING_INTERCEPTION
test_pattern: INTERACTION_TEST
---

# mock-endpoint-uri-with-params

## Instructions

# Mock Endpoint URI With Parameters Skill

## Instructions

- WHEN the TG encounters a test that uses `mockEndpoints(String pattern)` or `AdviceWithRouteBuilder` with `mockEndpoints()` API (e.g., `adviceWith(routeId, a -> a.mockEndpoints("mock:foo?param=value"))`)
- THEN it should verify that the _entire_ endpoint URI, including query parameters, is used for matching against the mock pattern — not just the scheme+path portion.
  - Specifically, when a route sends to `mock:foo?bar=123&cheese=yes`, and the mock pattern is `mock:foo?bar=123`, the test must ensure the mock URI `mock:foo?bar=123&cheese=yes` does NOT match `mock:foo?bar=123` because the full URIs differ.
  - Use `getMockEndpoint("mock:foo?bar=123")` to retrieve the mock and verify that messages sent to `mock:foo?bar=123&cheese=yes` are NOT received by that mock.
  - Conversely, verify that sending to `mock:foo?bar=123` DOES match `mock:foo?bar=123`.
- Include concrete assertions like `mock.assertIsSatisfied()` where expected message counts are set via `expectedMessageCount(1)`.
- Common pitfall: Assuming that `InterceptSendToMockEndpointStrategy` strips or ignores query parameters when matching URIs. Tests must demonstrate that the full URI, including all query parameters, is compared exactly.
- **Correct example** (what the test should do):
```java
// Route sends to mock:foo?bar=123&cheese=yes
// mock pattern is mock:foo?bar=123
MockEndpoint mock = getMockEndpoint("mock:foo?bar=123");
mock.expectedMessageCount(1); // expects the route to send to exact URI
// Send to mock:foo?bar=123 — this message is counted
template.sendBody("direct:start", "Hello World");
mock.assertIsSatisfied();
```
- **Incorrect example** (what the TG might do without this skill):
```java
// Wrong: assumes parameters are stripped
MockEndpoint mock = getMockEndpoint("mock:foo?bar=123");
mock.expectedMessageCount(1);
// Send to mock:foo?bar=123&cheese=yes — this would match if parameters were ignored
template.sendBody("direct:start", "Hello World");
mock.assertIsSatisfied(); // Fails: expected 1 but was 0 (or vice versa)
```
- **Test guidance**: Write a test that uses `adviceWith` to mock endpoints with a pattern that includes query parameters. Create a route that sends to a URI with additional parameters beyond the mock pattern. Verify that the mock only captures messages where the full URI matches exactly.
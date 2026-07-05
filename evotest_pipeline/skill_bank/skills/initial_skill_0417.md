---
name: on-completion-mode-switching
description: When a route defines an onCompletion block with mode-switching methods
  like onCompleteOnly() or onFailureOnly(), test that the correct branch executes
  for each outcome path (success vs. exception) and that the mode setting persists
  correctly under concurrent processing.
code_tags:
- FILE_UPLOAD_VALIDATION
- STATE_MUTATION
- ORDER_DEPENDENCY
test_pattern: STATE_TEST
---

# on-completion-mode-switching

## Instructions

# OnCompletion Mode Switching

## Instructions

- WHEN the TG encounters a `RouteBuilder` that calls `onCompletion()` followed by a mode-switching method (e.g., `.onCompleteOnly()` or `.onFailureOnly()`), possibly combined with `.parallelProcessing()`
- THEN it should write a test that verifies **both** the success path and the failure path produce the correct behavior:
  - Send a message that succeeds normally → verify that only the `onCompleteOnly` branch executes (not the `onFailureOnly` branch)
  - Send a message that throws an exception → verify that only the `onFailureOnly` branch executes, AND that the exception is correctly propagated (if `useOriginalMessage` is not set, the exception should still propagate to the caller)
  - Specifically, verify that the exchange body content, headers, and mock endpoint bodies have the expected values after each path
- Include concrete verification using `mock:endpoint` assertions:
  - `mock:complete.expectedMessageCount(1)` / `mock:complete.expectedBodiesReceived(...)` for the success branch
  - `mock:failure.expectedMessageCount(1)` / `mock:failure.expectedBodiesReceived(...)` for the failure branch
  - Also assert that the success mock receives **zero** messages when an exception occurs, and vice versa
- WHEN using `.parallelProcessing()`, verify that the mode-switching predicate is evaluated per-exchange (not cached before the exchange outcome is known), e.g., test that a message completing successfully does NOT trigger the failure-only branch and vice versa
- WHEN the bug is related to the `onCompletion` mode not being reevaluated per exchange, also verify that sending **two** messages — one success, one failure — results in the correct mock counts: `mock:stop.exchangeCount` equals the number of successes, `mock:except.exchangeCount` equals the number of failures
- Common pitfalls to avoid:
  - ❌ Testing only one path (only success or only failure) — this misses the mode-switching bug entirely
  - ❌ Assuming the mode-switching method works correctly under `.parallelProcessing()` without testing each path separately
  - ❌ Forgetting to assert that each mock receives the **exact expected count** (not just that it received some messages)
  - ❌ Not verifying the exception propagation when testing the failure path with `onFailureOnly()` — the exception should still be thrown to the caller (test with `assertMockEndpointsSatisfied()` + checking the exchange exception)

## Example

Correct test (two routes, two paths, assertions on both mocks):

```java
public void testOnCompletionIssue() throws Exception {
    final String body = "Body of message: 1";

    getMockEndpoint("mock:complete").expectedBodiesReceived(body);
    getMockEndpoint("mock:failure").expectedMessageCount(0);
    getMockEndpoint("mock:stop").expectedBodiesReceived(body);
    getMockEndpoint("mock:except").expectedMessageCount(0);

    template.sendBody("direct:start", body);

    assertMockEndpointsSatisfied();
}
```

Incorrect test (only verifies one path, no failure scenario):

```java
public void testOnCompletionSuccessOnly() throws Exception {
    getMockEndpoint("mock:complete").expectedMessageCount(1);
    getMockEndpoint("mock:stop").expectedMessageCount(1);

    template.sendBody("direct:start", "Hello");

    assertMockEndpointsSatisfied();
    // BUG: no failure path test, no mock:failure verification
}
```
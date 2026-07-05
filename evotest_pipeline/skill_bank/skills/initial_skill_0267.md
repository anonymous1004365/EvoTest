---
name: response-filter-ajax-application
description: When response filters implement IResponseFilter and need to process both
  Ajax and non-Ajax responses, tests must verify filters are applied to both code
  paths. Without this check, filters may silently be skipped for Ajax responses, causing
  inconsistent behavior.
code_tags:
- NULL_CHECK
- VALIDATION
- STATE_MUTATION
test_pattern: STATE_TEST
---

# response-filter-ajax-application

## Instructions

# Response Filter Application for Ajax Responses

## Instructions

WHEN the Test Generator encounters code that implements `IResponseFilter` and registers it via `getRequestCycleSettings().addResponseFilter(...)`:

- THEN the TG MUST verify that the response filter is applied to **both** Ajax and non-Ajax (normal) responses.
- Specifically, test the `IResponseFilter.filter(AppendingStringBuffer)` method and check that it is called on:
  1. A normal (non-Ajax) request/response cycle
  2. An Ajax request/response cycle (e.g., by simulating an Ajax request via `AbstractAjaxTimerBehavior` or similar)
- For each path, verify that the filter's `filter()` method actually receives and processes the response buffer. The easiest way is to use a `IResponseFilter` implementation that tracks whether it was invoked (e.g., a boolean flag `wasInvoked` set to `true` inside `filter()`).
- Assert that `wasInvoked` is `true` after both a normal request and an Ajax request. Only testing one path (usually the normal one) will NOT catch this bug.

Common pitfalls to avoid:
- **Testing only the normal (non-Ajax) request path** — the buggy code may apply filters only there, not in `AjaxRequestHandler`.
- **Testing only that the filter is registered** — registering does not guarantee invocation on all response paths.
- **Assuming Ajax responses bypass filter application** — they should not; the fix ensures Ajax responses also run through filters.

### Correct example

```java
@Test
public void normalRequest()
{
    final boolean[] invoked = { false };
    IResponseFilter filter = new IResponseFilter() {
        @Override
        public AppendingStringBuffer filter(AppendingStringBuffer responseBuffer) {
            invoked[0] = true;
            return responseBuffer;
        }
    };
    tester.getApplication().getRequestCycleSettings().addResponseFilter(filter);
    
    // Execute a normal request
    tester.startPage(TestPage.class);
    assertTrue("Response filter was not invoked for normal request", invoked[0]);
}

@Test
public void ajaxRequest()
{
    final boolean[] invoked = { false };
    IResponseFilter filter = new IResponseFilter() {
        @Override
        public AppendingStringBuffer filter(AppendingStringBuffer responseBuffer) {
            invoked[0] = true;
            return responseBuffer;
        }
    };
    tester.getApplication().getRequestCycleSettings().addResponseFilter(filter);
    
    // Execute an Ajax request (e.g., via an Ajax behavior)
    tester.executeAjaxEvent(tester.getComponent("ajaxButton"), "click");
    assertTrue("Response filter was not invoked for Ajax request", invoked[0]);
}
```

### Incorrect example (will NOT catch the bug)

```java
@Test
public void normalRequest()
{
    final boolean[] invoked = { false };
    IResponseFilter filter = new IResponseFilter() {
        @Override
        public AppendingStringBuffer filter(AppendingStringBuffer responseBuffer) {
            invoked[0] = true;
            return responseBuffer;
        }
    };
    tester.getApplication().getRequestCycleSettings().addResponseFilter(filter);
    
    tester.startPage(TestPage.class);
    assertTrue("Response filter was not invoked", invoked[0]);
    // Only checks normal requests — Ajax path remains untested
}
```
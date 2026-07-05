---
name: redirect-handler-branch-coverage
description: WHEN testing redirect request handlers with multiple status codes (301/302/303),
  THEN ensure all branch paths are covered — especially that status 303 (SC_SEE_OTHER)
  goes through the `setStatus`+`setHeader` path, not `sendRedirect`.
code_tags:
- REDIRECT_HANDLER_BRANCH_COVERAGE
- VALIDATION
- STATE_MUTATION
test_pattern: INTERACTION_TEST
---

# redirect-handler-branch-coverage

## Instructions

# Redirect Handler Branch Coverage

## Instructions

WHEN the TG encounters a request handler that dispatches different HTTP redirect status codes (301, 302, 303), THEN it should verify that the constructor validation AND the `respond()` method both handle status 303 (`SC_SEE_OTHER`, value=303) correctly.

Specifically:

1. **Constructor validation coverage**: The constructor allows status values 301 (`SC_MOVED_PERMANENTLY`), 302 (`SC_MOVED_TEMPORARILY`), and 303 (`SC_SEE_OTHER`). Any other status must throw `IllegalStateException` with message containing "Status must be either 301, 302 or 303". The TG should test all three valid values plus at least one invalid value (e.g., 304, 404, 0, -1).

2. **`respond()` method branch coverage**: The `respond(IRequestCycle)` method has a critical `if` branch: `if (status == HttpServletResponse.SC_MOVED_TEMPORARILY)` triggers `response.sendRedirect(location)`, while ALL other statuses (including 301 and 303) go to the `else` branch which calls `response.setStatus(status)` and `response.setHeader("Location", location)`. The TG MUST test that status 303 (SC_SEE_OTHER) correctly goes through the `else` branch, calling `setStatus(303)` and `setHeader("Location", ...)` — NOT `sendRedirect`.

3. **Mock-based verification**: Use Mockito to mock both `IRequestCycle` and `WebResponse`. Set up `Mockito.when(requestCycle.getResponse()).thenReturn(webResponse)`. Then verify the exact method calls and arguments using `Mockito.verify(webResponse)`.

4. **Common pitfalls to avoid**:
   - Do NOT assume status 303 behaves like 302 (temporary redirect). The hardcoded branch only sends `sendRedirect` for 302; 303 goes to the `else` branch with `setStatus`+`setHeader`.
   - Do NOT test only 301 and 302 in `respond()`. The bug was that 303 was not tested — the constructor allowed it, but the test suite only covered 301 and 302, leaving the 303 branch path untested.
   - Do NOT forget to verify both `setStatus` AND `setHeader` calls for the 303 variant. The `else` branch does both.
   - Do NOT forget to verify that `sendRedirect` is NOT called for 303 status.

### Correct example (for status 303):

```java
@Test
public void seeOtherShouldSetLocationHeader()
{
    RedirectRequestHandler handler = new RedirectRequestHandler(REDIRECT_URL,
            HttpServletResponse.SC_SEE_OTHER);

    IRequestCycle requestCycle = Mockito.mock(IRequestCycle.class);
    WebResponse webResponse = Mockito.mock(WebResponse.class);

    Mockito.when(requestCycle.getResponse()).thenReturn(webResponse);

    handler.respond(requestCycle);

    Mockito.verify(webResponse).setStatus(HttpServletResponse.SC_SEE_OTHER);
    Mockito.verify(webResponse).setHeader("Location", REDIRECT_URL);
}
```

### Common mistake — only testing 301 and 302 (incomplete coverage):

```java
// INCOMPLETE: this only covers 301 branch of respond() 
@Test
public void permenanentlyMovedShouldSetLocationHeader() {
    RedirectRequestHandler handler = new RedirectRequestHandler(REDIRECT_URL,
            HttpServletResponse.SC_MOVED_PERMANENTLY);
    // ... verify setStatus(301) and setHeader(...)
}

// INCOMPLETE: this only covers 302 branch of respond()
@Test
public void tempMovedShouldRedirect() {
    RedirectRequestHandler handler = new RedirectRequestHandler(REDIRECT_URL,
            HttpServletResponse.SC_MOVED_TEMPORARILY);
    // ... verify sendRedirect(...)
}

// MISSING: No test for status 303 (SC_SEE_OTHER), which also goes through the else branch
```
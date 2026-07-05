---
name: expired-page-ajax-behavior-recreation
description: When testing request handling for expired pages with Ajax behaviors,
  the TG should verify that a new page instance is properly recreated and the behavior
  lookup does not fail with an InvalidBehaviorIdException. This applies when a listener
  interface is invoked on a component with a behavior after the page session has expired.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- NULL_CHECK
- STATE_MUTATION
- COMPONENT_TREE_NAVIGATION
- CHILD_REMOVAL
test_pattern: STATE_TEST
---

# expired-page-ajax-behavior-recreation

## Instructions

# Expired Page Ajax Behavior Recreation

## Instructions

- WHEN the TG encounters code that handles Ajax listener requests on pages that may expire (e.g., `ListenerRequestHandler.respond()` with an `AjaxLink` containing an `AjaxEventBehavior` or similar behavior of type `AjaxLink`)
- THEN the TG should write a test that:
  1. Mounts a test page (e.g., using `tester.getApplication().mountPage("path", TestPage.class)`)
  2. Starts the page and captures the initial page ID (e.g., `tester.startPage(TestPage.class)`)
  3. Gets the URL for the Ajax link/component (e.g., `tester.urlFor(page.link)`)
  4. Clears the session (e.g., `tester.getSession().clear()`) to simulate page expiry
  5. Fires an Ajax request to the URL with the `Wicket-Ajax-BaseURL` and `Wicket-Ajax` headers set as well as the request URL
  6. Asserts that the last rendered page has a page ID greater than the initial page ID (e.g., `assertTrue("A new page must be created", lastRenderedPageId > initialPageId)`)
- The test page must use an AjaxLink (or similar component that adds a behavior) and must NOT override `getStatelessHint()` to return `false` — when the behavior doesn't explicitly set `getStatelessHint()`, the default returns `true`, which means the behavior's ID may not be persisted, causing an `InvalidBehaviorIdException` on an expired page. Verify this by checking that `InvalidBehaviorIdException.getMessage()` contains "Perhaps the behavior did not properly implement getStatelessHint()".
- Common pitfalls to avoid:
  - Do NOT test only with fresh (non-expired) pages — the bug manifests specifically on expired pages where the behavior ID was never assigned because `getStatelessHint()` returned `true`
  - Do NOT manually assign behavior IDs in the test — the bug relies on the default behavior ID assignment mechanism
  - Do NOT forget to set the `Wicket-Ajax-BaseURL` request header on the simulated Ajax request, as it is required for proper page reconstruction
  - Do NOT forget to set `Wicket-Ajax` header to `"true"` to mark the request as Ajax
  - Do NOT test only by calling `respond()` directly without simulating the full request cycle — the page recreation logic depends on the request cycle processing

### Correct Example (simulating expired page Ajax request):
```java
tester.getApplication().mountPage("ajaxLink", AjaxLinkExpirePage.class);
AjaxLinkExpirePage page = tester.startPage(AjaxLinkExpirePage.class);
int initialPageId = page.getPageId();
Url urlToAjaxLink = tester.urlFor(page.link);
tester.getSession().clear();
// Execute the Ajax request
tester.getRequest().setUrl(urlToAjaxLink);
tester.getRequest().addHeader("Wicket-Ajax-BaseURL",
    tester.getWicketAjaxBaseUrlEncodedInLastResponse());
tester.getRequest().addHeader("Wicket-Ajax", "true");
tester.processRequest();
Page lastRenderedPage = tester.getLastRenderedPage();
assertTrue("A new page must be created",
    lastRenderedPage.getPageId() > initialPageId);
```

### Incorrect Example (only tests fresh page, no session expiry):
```java
// BAD: This does not test the expired page scenario
tester.startPage(MyPage.class);
tester.clickLink("link");
// No session.clear() → never triggers the page recreation path
```
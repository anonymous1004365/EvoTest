---
name: redirect-absolute-url-status-code
description: When testing redirect responses via WicketTester, the TG should verify
  that redirects to absolute URLs (starting with http:// or https://) result in HTTP
  302 status codes, as WicketTester's internal redirect processing may incorrectly
  return 200 by treating absolute URLs as relative.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
- STATE_MUTATION
test_pattern: STATE_TEST
---

# redirect-absolute-url-status-code

## Instructions

# Redirect to Absolute URL Status Code Validation

## Instructions

- WHEN the TG encounters code that tests a redirect response (e.g., via `WicketTester` calling `assertRedirectUrl()` or checking response status), and the redirect target is an absolute URL (starting with `http://`, `https://`, or another scheme),
- THEN the TG MUST test that the response status code is `302` (HttpServletResponse.SC_MOVED_TEMPORARILY). The bug is that `WicketTester` internally calls `assertRedirectUrl()` and may incorrectly treat absolute URLs as relative, processing them through the test application and returning status `200` instead of `302`. To write a test that catches this bug, the TG should simulate a redirect to an absolute URL (e.g., `http://example.com/test`), call `processRequest()` or the relevant request method, and then verify `tester.getLastResponse().getStatus() == 302`.

- **Concrete approach**: Create a page/component that, in its lifecycle (e.g., `onBeforeRender`, `onClick` of a link, or `onSubmit` of a form), calls `throw new RedirectToUrlException("http://example.com/destination");` or executes `((Page) component.getPage()).redirectToUrl("http://example.com/destination");`. Then use `WicketTester` to execute the request and assert that the status code is `302`. Do NOT assume `assertRedirectUrl()` alone is sufficient — the bug is in how `WicketTester` processes the redirect internally.

- **Common pitfall**: Testing only relative URL redirects (e.g., `./some-page` or `/relative/path`), which work correctly with `assertRedirectUrl()`. The bug is specific to absolute URLs. Also, DO NOT just call `assertRedirectUrl()` and skip the status check — the status code assertion is what catches the bug.

- **Mistakes to avoid**:
  - Testing only relative redirect URLs — these pass even on the buggy version.
  - Relying solely on `assertRedirectUrl()` without checking the response status code.
  - Assuming `WicketTester.executeRedirect()` or similar internal methods are invoked correctly — the test must use an end-to-end request (e.g., render a page that triggers a redirect) to expose the bug.

- **Example of correct test** (catches the bug):
  ```java
  // Create a page that redirects to an absolute URL
  public class RedirectPage extends WebPage {
      public RedirectPage() {
          throw new RedirectToUrlException("http://example.com/redirect");
      }
  }
  // Test
  WicketTester tester = new WicketTester();
  tester.startPage(RedirectPage.class);
  int status = tester.getLastResponse().getStatus();
  assertEquals("Expected 302 for absolute URL redirect", 302, status);
  ```

- **Example of incorrect test** (misses the bug):
  ```java
  // Only tests relative redirect — works on both buggy and fixed versions
  WicketTester tester = new WicketTester();
  tester.startPage(RelativeRedirectPage.class); // redirects to "./some-other-page"
  tester.assertRedirectUrl("./some-other-page");
  // status may be 200 or 302 — not checked!
  ```
---
name: ajax-parameter-cleaning-in-pageparameters
description: When constructing a UrlInfo object or any object that wraps PageParameters,
  internal Ajax-related parameters (PARAM_AJAX, PARAM_AJAX_BASE_URL, PARAM_AJAX_REQUEST_ANTI_CACHE)
  must be removed from the parameters so they are not propagated to subsequent requests.
  The test should verify that getPageParameters() returns null when only these internal
  parameters are present.
code_tags:
- NULL_CHECK
- VALIDATION
- STATE_MUTATION
test_pattern: STATE_TEST
---

# ajax-parameter-cleaning-in-pageparameters

## Instructions

# Ajax Parameter Cleaning in PageParameters

## Instructions

WHEN the TG encounters a class that constructs `PageParameters` from raw request parameters (e.g. `AbstractBookmarkableMapper.UrlInfo`) and those parameters may contain Wicket-internal Ajax-related keys such as `WebRequest.PARAM_AJAX`, `WebRequest.PARAM_AJAX_BASE_URL`, and `WebRequest.PARAM_AJAX_REQUEST_ANTI_CACHE`,

THEN the TG should test that the constructor/method correctly strips these internal parameters from the resulting `PageParameters` instance. Specifically:
- Create a `PageParameters` object and add the three Ajax-related parameters with arbitrary values (e.g., `"true"`, `"base/url"`, `"12345.6879"`).
- Pass these parameters to the relevant constructor (e.g., `new UrlInfo(null, MockPage.class, parameters)`).
- Call `getPageParameters()` on the constructed object — it must return `null` when *only* Ajax parameters were present.
- If non-Ajax parameters are mixed in, verify that those other parameters are retained while the Ajax-specific ones are removed.

Common pitfalls to avoid:
- Testing only with a single Ajax parameter (e.g., only `PARAM_AJAX`) instead of all three: `PARAM_AJAX`, `PARAM_AJAX_BASE_URL`, `PARAM_AJAX_REQUEST_ANTI_CACHE`.
- Testing only that construction succeeds without verifying the resulting `PageParameters` has been cleaned.
- Testing with `null` input `PageParameters` — the skill is about *cleaning*, not null-handling.
- Forgetting that when all parameters are removed, `getPageParameters()` should return `null` (not an empty `PageParameters`).

Example of a correct test:
```java
@Test
public void wicket4038()
{
    PageParameters parameters = new PageParameters();
    parameters.add(WebRequest.PARAM_AJAX, "true");
    parameters.add(WebRequest.PARAM_AJAX_BASE_URL, "base/url");
    parameters.add(WebRequest.PARAM_AJAX_REQUEST_ANTI_CACHE, "12345.6879");

    AbstractBookmarkableMapper.UrlInfo info = new UrlInfo(null, MockPage.class, parameters);
    assertNull(info.getPageParameters());
}
```

Example of an incorrect/incomplete test:
```java
@Test
public void badTest()
{
    // BAD: Only tests one Ajax parameter, not all three
    PageParameters parameters = new PageParameters();
    parameters.add(WebRequest.PARAM_AJAX, "true");

    AbstractBookmarkableMapper.UrlInfo info = new UrlInfo(null, MockPage.class, parameters);
    assertNull(info.getPageParameters()); // FAILS on buggy code because only PARAM_AJAX is removed
}
```
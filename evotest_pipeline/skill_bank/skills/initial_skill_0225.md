---
name: request-mapper-scheme-handling-bug
description: When testing HttpsMapper, mock the HttpServletRequest to set scheme to
  lowercase "https" and verify url.setProtocol is called with "https". Also test with
  "http" scheme to ensure port and protocol reset. Finally, test with mock IRequestHandler
  (non-IPageClassRequestHandler) to verify Scheme.ANY returns sameInstance handler.
code_tags:
- ARGUMENT_VALIDATION
- NULL_CHECK
- BOUNDARY_CHECK
test_pattern: INTERACTION_TEST
---

# request-mapper-scheme-handling-bug

## Instructions

# Request Mapper Scheme Handling Bug

## Instructions

- WHEN the TG encounters code that calls `mapHandler(IRequestHandler handler, Request request)` in `HttpsMapper`, specifically the `Url.setProtocol()` and `Url.setPort()` interaction with the scheme check
- THEN it should verify that when the request scheme is `"http"` and the desired scheme for the handler is `HTTPS`:
  - The returned url has protocol set to `"https"`
  - The returned url has port set to `443` (for default HttpsConfig)
  - Use `assertThat(url.getProtocol(), is("https"))` and `assertThat(url.getPort(), is(443))`
- THEN it should verify that when the request scheme is `"http"` and the desired scheme for the handler is `HTTP` (InsecurePage):
  - The returned url has protocol set to `nullValue()` (since no redirect needed)
  - Use `assertThat(url.getProtocol(), is(nullValue()))`
- THEN it should verify that when the request scheme is `"https"` and the desired scheme for the handler is `HTTP` (InsecurePage):
  - The returned url has protocol set to `"http"`
  - The returned url has port set to `80` (for default HttpsConfig)
  - Use `assertThat(url.getProtocol(), is("http"))` and `assertThat(url.getPort(), is(80))`
- THEN it should verify that the `HttpServletRequest.getScheme()` mock returns lowercase `"http"` / `"https"` (not mixed case) for the mapHandler test to avoid the bug
- Mistakes to avoid:
  - Testing only the positive case (HTTP -> HTTPS) and missing the reverse case (HTTPS -> HTTP)
  - Forgetting to mock `HttpServletRequest.getScheme()` with lowercase strings
  - Not using `renderPageRequestHandler` with proper page classes (SecurePage, InsecurePage) that have @RequireHttps annotation
  - Not resetting the delegate mock between test scenarios (the delegate mock's mapHandler must return a fresh Url with each call)
  - Not verifying that `url.getProtocol()` returns `nullValue()` when the current scheme is compatible with the desired scheme

### Correct Example

```java
// rendering url to https page on http, set protocol
IRequestHandler handler = new RenderPageRequestHandler(new PageProvider(SecurePage.class));
Url url = new Url();
when(delegate.mapHandler(handler)).thenReturn(url);
when(req.getScheme()).thenReturn("http");
mapper.mapHandler(handler, request);
assertThat(url.getProtocol(), is("https"));
assertThat(url.getPort(), is(443));

// render url to http page on https, set protocol
handler = new RenderPageRequestHandler(new PageProvider(InsecurePage.class));
url = new Url();
reset(delegate);
when(delegate.mapHandler(handler)).thenReturn(url);
when(req.getScheme()).thenReturn("https");
mapper.mapHandler(handler, request);
assertThat(url.getProtocol(), is("http"));
assertThat(url.getPort(), is(80));

// render url to http page on http, ignore protocol  
handler = new RenderPageRequestHandler(new PageProvider(InsecurePage.class));
url = new Url();
reset(delegate);
when(delegate.mapHandler(handler)).thenReturn(url);
when(req.getScheme()).thenReturn("http");
mapper.mapHandler(handler, request);
assertThat(url.getProtocol(), is(nullValue()));
```

### Incorrect Example

```java
// BUG: Only tests one direction, forgets to reset delegate, uses upper case "HTTP"
IRequestHandler handler = new RenderPageRequestHandler(new PageProvider(SecurePage.class));
Url url = new Url();
when(delegate.mapHandler(handler)).thenReturn(url);
when(req.getScheme()).thenReturn("HTTP");  // BUG: should be lowercase "http"
mapper.mapHandler(handler, request);
assertThat(url.getProtocol(), is("https"));
// Missing: test for HTTPS->HTTP, missing assert on port, missing null protocol case
```
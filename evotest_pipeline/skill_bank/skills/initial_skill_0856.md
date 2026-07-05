---
name: lazy-isPageStateless-redirect-to-buffer
description: When testing page statelessness detection with lazy-initialization and
  redirect-to-buffer rendering, verify that isPageStateless() is called BEFORE the
  page is rendered to buffer. If the page is only rendered lazily, the test must ensure
  the stateless check happens before rendering, otherwise it will incorrectly return
  false.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- VALIDATION
- STATE_MUTATION
test_pattern: STATE_TEST
---

# lazy-isPageStateless-redirect-to-buffer

## Instructions

# Lazy isPageStateless with Redirect-to-Buffer Rendering

## Instructions

- WHEN the TG encounters a test that checks `isPageStateless()` on a page that uses a redirect-to-buffer render strategy (e.g. `WebPageRenderer`), AND the page's stateless status depends on its component hierarchy being fully initialized
- THEN the TG should ensure that `isPageStateless()` is tested BEFORE any page rendering occurs. Specifically:
  - The page must be created and its `isPageStateless()` method called BEFORE `tester.startPage()` or any render-to-buffer operation
  - When using `WebPage.renderPage()` or similar, the stateless check must happen on the page object directly, not after the page has been processed by a buffered renderer
  - Verify that the test simulates the correct ordering: create page → check stateless → render page
  - Expected behavior on the buggy version: `isPageStateless()` returns `true` when called before rendering, but incorrectly returns `false` when called lazily after/during a redirect-to-buffer render cycle

- Common pitfalls:
  - Calling `tester.startPage()` first and then checking `isPageStateless()` on the rendered page — this will trigger the lazy/buffered path and produce the wrong result
  - Not separating the page creation from the render cycle, causing the stateless check to occur after the page's state has been mutated by rendering
  - Assuming that `isPageStateless()` returns the same value regardless of when it is called during the page lifecycle

- Correct example:
```java
// Create the page manually
MyStatelessPage page = new MyStatelessPage();

// Check stateless BEFORE rendering
assertTrue("Page should be stateless before rendering", page.isPageStateless());

// Now render
tester.startPage(page);
```

- Incorrect example:
```java
// This will cause isPageStateless to be called lazily/after rendering
tester.startPage(MyStatelessPage.class);

// This may fail on buggy version because stateless check happens too late
// Page rendered=false when it should be true
WicketTesterLazyIsPageStatelessRedirectToBufferTest
```
---
name: bookmarkable-mapper-relative-page-decoding
description: When testing URL mappers that generate relative URLs for page instances,
  verify that the mapper can also decode (resolve) those relative URLs back to a valid
  request handler. Tests should cover both String-based and page class-based mount
  paths in the same mapping configuration.
code_tags:
- VALIDATION
test_pattern: INTERACTION_TEST
---

# bookmarkable-mapper-relative-page-decoding

## Instructions

# Bookmarkable Mapper Relative URL Decoding

## Instructions

- WHEN the Test Generator (TG) encounters a `BookmarkableMapper` or any `AbstractBookmarkableMapper` subclass that mounts page classes using both `mountPage(String mountPath, Class<? extends Page> pageClass)` and string-based paths (e.g., `/page` or empty string `""` for root-level mount), THEN it should write an interaction test that verifies the **decoding** (resolution) of a relative URL produced by the mapper's **encoding** of a page instance.

- Specifically, the TG should:
  1. Mount a bookmarkable page class at the root-level mount path (e.g., an empty string `""`) — this means the page is accessible directly via its class, without any additional path prefix.
  2. **Encode** a page instance using `mapper.mapRequestHandler(...)` to get the `RequestHandler` and then obtain the URL via `urlFor(requestHandler, ...)` — this produces the relative URL for that page.
  3. **Decode** that same relative URL back using `mapper.mapRequest(url, ...)` and assert that the result is **not null** (a valid `RequestHandler` is resolved).
  4. The test must assert `assertNotNull("A handler should be resolved for relative url to a bookmarkable page!", handler)` on the decoded result.

- **Common pitfall**: The TG might test only the encoding direction (i.e., producing a URL from a request handler) without verifying that the same URL can be decoded back into a handler. This is critical because the mapper must be **bidirectional** — encoding and decoding must be symmetric. Without testing both directions, the bug (where the mapper fails to decode a URL that it itself produced) can go undetected.

- **Correct example**:
```java
// Mount a page at the root mount path (empty string)
mapper.mountPage("", MockPage.class);

// Encode a page instance request handler to get a URL
RequestHandler requestHandler = new RenderPageRequestHandler(new PageProvider(MockPage.class));
Url url = mapper.mapHandler(requestHandler);

// Decode the relative URL back
IRequestHandler[] handler = mapper.mapRequest(url, requestParameters);
assertNotNull("A handler should be resolved for relative url to a bookmarkable page!", handler);
```

- **Common mistake to avoid**: Testing only the encoding with `mountPage("/somePath", MockPage.class)` but not verifying that the produced relative URL can be decoded back when the page is mounted at the root path (`""`). The bug is triggered specifically when the mount path is empty — the mapper produces a correct URL during encoding but fails to recognize it during decoding.

- **Another mistake**: Using absolute URLs instead of relative ones. The encoding produces relative URLs (e.g., `wicket/bookmarkable/...`), and the test must use these relative URLs for decoding, not absolute ones with a base context path.
---
name: indexed-url-parameter-trailing-slash
description: WHEN testing IndexedParamUrlCodingStrategy URL generation, THEN verify
  that URL fragments containing interface parameters (or pagemap) after indexed parameters
  do NOT have an extra trailing slash that breaks subsequent URL path appending. This
  skill catches cases where an encoded URL is reused as a prefix for resource listener
  URLs.
code_tags:
- URL_ENCODING
- STRING_MANIPULATION
- STATE_MUTATION
test_pattern: STATE_TEST
---

# indexed-url-parameter-trailing-slash

## Instructions

# Indexed URL Parameter Trailing Slash Bug

## Instructions

WHEN the TG encounters code that uses `IndexedParamUrlCodingStrategy.appendParameters()` to build a URL, and the appended parameters include an INTERFACE_PARAMETER_NAME ("interface") or PAGEMAP parameter AFTER indexed integer parameters (e.g., parameters "0", "1", then "interface"), THEN the TG should test that the generated URL does NOT end with a trailing slash (`/`) that would break subsequent URL path appending.

Specifically:

- WHEN a page is mounted with `IndexedParamUrlCodingStrategy` and contains a component that calls `urlFor(IResourceListener.INTERFACE)` (which triggers URL encoding through the strategy),
- THEN verify that the generated URL for the page contains `src="...interface..."` WITHOUT a trailing slash before the `::` in the interface path,
- AND verify the URL follows the pattern: `/mount-path/paramValue0/paramValue1/wicket:interface:componentId::IResourceListener::` (NOT `/mount-path/paramValue0/paramValue1/wicket:interface:componentId::IResourceListener::/`).

The bug: In the buggy `appendParameters()` method, after appending the last special parameter (pagemap or interface), an extra `url.append("/")` at end adds a trailing slash. The fix removes this final trailing slash so that `decodeParameters()` (which strips trailing slashes) correctly decomposes the URL, and so the URL can be correctly used as a prefix for resource listener URLs.

How to write the test:

1. Mount a page using `IndexedParamUrlCodingStrategy` with a mount path (e.g., `"/test"`).
2. Create a page instance that has a component implementing `IResourceListener` that builds a URL via `urlFor(IResourceListener.INTERFACE)` (e.g., an iframe with `src` attribute set to `urlFor(IResourceListener.INTERFACE)`).
3. Pass `PageParameters` with indexed integer keys and at least one special parameter (e.g., `new PageParameters("0=foo,1=bar")` — just integer keys is enough since the page+interface triggers internal URL construction).
4. Start the page via `tester.startPage(page)`.
5. Assert the rendered HTML `assertContains("src=\"...")` where the URL in `src` contains the correct interface path WITHOUT a double slash or trailing slash artifact.

Common pitfalls:
- Testing only simple URL encoding without the presence of a component that triggers resource listener URL generation (the bug manifests when the URL is further processed by the framework, not just in `appendParameters` alone).
- Forgetting to mount the page with `IndexedParamUrlCodingStrategy` (using `BookmarkablePageRequestTargetUrlCodingStrategy` instead would not trigger this bug).
- Asserting the URL ends with a trailing slash — the FIXED version does NOT have this trailing slash.

### Correct test example:
```java
tester.getApplication().mount(
    new IndexedParamUrlCodingStrategy("/test", TestPageWithIFrame.class));
TestPageWithIFrame test = new TestPageWithIFrame(new PageParameters("0=foo,1=bar"));
tester.startPage(test);
tester.assertRenderedPage(TestPageWithIFrame.class);
tester.assertNoErrorMessage();
tester.assertContains("src=\"test/wicket:interface/:0:frame::IResourceListener::\"");
```

### Incorrect test example (missing trailing slash check):
```java
// This only verifies the page renders but doesn't check the URL format
tester.getApplication().mount(
    new IndexedParamUrlCodingStrategy("/test", TestPageWithIFrame.class));
tester.startPage(new TestPageWithIFrame(new PageParameters("0=foo,1=bar")));
tester.assertRenderedPage(TestPageWithIFrame.class);
// Missing: assertContains check on the specific URL format!
```
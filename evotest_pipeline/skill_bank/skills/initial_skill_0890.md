---
name: stateless-link-mark-children-immutable
description: When a component is marked as stateless (setStatelessHint(true)), its
  children's render preparation state may be cleared. Test that components with dynamic
  links can still render properly after being marked stateless.
code_tags:
- NULL_CHECK
- STATE_MUTATION
- VALIDATION
- COMPONENT_RENDER_PREPARATION
test_pattern: STATE_TEST
---

# stateless-link-mark-children-immutable

## Instructions

# Stateless Link Mark Children Immutable

## Instructions

- WHEN the TG encounters code that modifies a component's stateless hint via `setStatelessHint(boolean)` or adds `IStatelessComponent` markers, and the component contains dynamic links (e.g., `BookmarkablePageLink`, `Link`, or other link components added in `onInitialize()` or a constructor),
- THEN the TG should write a test that:
  1. Creates a page with dynamic links added in its constructor or `onInitialize()` method
  2. Mounts the page at a URL path using `tester.getApplication().mountPage("/path", PageClass.class)`
  3. Renders the page with `tester.startPage(PageClass.class)` or `tester.executeUrl("/path")`
  4. Asserts that the rendered response contains the expected link markup (e.g., `assertContains("href=\"...\"")` or checks the link target is present)
  5. The test should **fail on the buggy version** because the component's `beforeRender()` was skipped (the "WICKET-5460 no longer prepared for render" comment indicates the bug: a stateless component's children may not be prepared for rendering, causing dynamic links to not appear or have incorrect URLs)
  
- The test must verify that dynamic link components (those added programmatically, not in markup) render their URLs correctly even when the page is stateless. The test should use `tester.assertContains()` or `tester.assertModelValue()` to verify link content.

- Common pitfalls to avoid:
  - **Testing only static links**: The bug only manifests with programmatically added dynamic links (e.g., links added in `add(new BookmarkablePageLink<>("id", PageClass.class))`).
  - **Not mounting the page**: If the page is not mounted, the URL generation may differ and the bug may not trigger.
  - **Only testing the page class directly**: The bug is about rendering — use `tester.startPage()` or `tester.executeUrl()` to actually render the page and capture the response.
  - **Forgetting that `IStatelessComponent` interfaces or `setStatelessHint(true)` cause the issue**: The bug occurs when a component/page is marked stateless; test with a stateless page.
  
- Correct example approach:
```java
// Mount the page
tester.getApplication().mountPage("/stateless", StatelessPageWithDynamicLinks.class);

// Execute the URL to render
tester.executeUrl("/stateless");

// Verify the dynamic link appears in the rendered output
tester.assertContains("SomeLinkLabel");
// Or check the specific link URL contains expected parameters
```

- Incorrect example approach:
```java
// WRONG: Just creating the page without rendering doesn't catch the bug
StatelessPageWithDynamicLinks page = new StatelessPageWithDynamicLinks(new PageParameters());
assertNotNull(page.get("link"));

// WRONG: Not mounting, or checking directly without going through URL execution
tester.startPage(StatelessPageWithDynamicLinks.class);
// This might work differently than executing the mounted URL
```
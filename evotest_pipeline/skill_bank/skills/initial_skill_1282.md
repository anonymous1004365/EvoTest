---
name: redirect-to-buffer-stateful-page-null-check
description: When testing page rendering with REDIRECT_TO_BUFFER strategy and lazy
  page statelessness checks, ensure the test verifies that stateful pages (those with
  stateful listener interfaces) are not null after rendering. The bug caused stateful
  pages to return null after requesting buffered response before page statelessness
  was fully determined.
code_tags:
- NULL_CHECK
- STATE_MUTATION
- VALIDATION
- ORDER_DEPENDENCY
test_pattern: STATE_TEST
---

# redirect-to-buffer-stateful-page-null-check

## Instructions

# Page Rendering With REDIRECT_TO_BUFFER Strategy and Stateful Listener Interfaces

## Instructions

- WHEN the TG encounters a test that sets `RequestCycleSettings.RenderStrategy.REDIRECT_TO_BUFFER` and tests page statelessness via `isPageStateless()` or `setStatelessHint(false)` on a component with a stateless listener interface (e.g., `IStatelessListener`)
- THEN the TG should write a test that:
  1. Creates a page with a component that returns `false` from `setStatelessHint(false)` and implements a stateless listener interface (e.g., `IStatelessListener` or any interface from `org.apache.wicket.behavior.IStatelessListener`)
  2. Sets the render strategy to `REDIRECT_TO_BUFFER` via `tester.getRequestCycleSettings().setRenderStrategy(RenderStrategy.REDIRECT_TO_BUFFER)`
  3. Starts the test with `tester.startPage(page)`
  4. Verifies `tester.getLastRenderedPage()` is NOT null — this catches the bug where page ends up null
  5. Also verifies the page's component is present in the response (e.g., `tester.assertComponent(...)`)
- The test should expect a `NullPointerException` to be thrown (or at least `tester.getLastRenderedPage()` to be null) on the buggy version when the page is stateful but components return `false` from `setStatelessHint(false)` while implementing a stateless listener interface

- Common pitfalls to avoid:
  - **Do NOT** test only with stateless pages — the bug only manifests with stateful pages that have components implementing stateless listener interfaces
  - **Do NOT** forget to set the render strategy — without `REDIRECT_TO_BUFFER`, the bug does not reproduce
  - **Do NOT** assume that calling `tester.startPage(page)` followed by `tester.getLastRenderedPage()` is sufficient — the bug specifically requires the page to be fully rendered and the buffered response to be processed before page statelessness is determined
  - **Do NOT** test with pages that have no components returning false from setStatelessHint — the bug requires that statefulness is determined lazily during rendering

### Correct Example (Fixed Version Behavior):
```java
@Test
public void statelessListenerInterfaceInvoked() {
    // Set up
    RequestCycleSettings settings = tester.getRequestCycleSettings();
    settings.setRenderStrategy(RenderStrategy.REDIRECT_TO_BUFFER);
    
    // Create a page with a component that is stateful (setStatelessHint(false))
    // but which also implements a stateless listener interface
    LazyIsPageStatelessTestPage page = new LazyIsPageStatelessTestPage();
    page.add(new LazyIsPageStatelessTestPanel("panel"));
    
    // Execute
    tester.startPage(page);
    
    // Verify — page must not be null
    assertNotNull("The rendered page should not be null", tester.getLastRenderedPage());
    
    // Verify component is still present
    tester.assertComponent("panel", LazyIsPageStatelessTestPanel.class);
}
```

### Incorrect Example (Would Miss the Bug):
```java
@Test
public void statelessPageRendering() {
    // WRONG: Only tests stateless pages, not stateful ones with listener interfaces
    tester.getRequestCycleSettings().setRenderStrategy(RenderStrategy.REDIRECT_TO_BUFFER);
    
    // This is a stateless page — no components with setStatelessHint(false)
    StatelessPage page = new StatelessPage();
    tester.startPage(page);
    
    // This test would pass even with the bug
    assertNotNull(tester.getLastRenderedPage());
}

@Test
public void statefulPageWithoutListener() {
    // WRONG: Uses ONE_PASS_RENDER strategy instead of REDIRECT_TO_BUFFER
    tester.getRequestCycleSettings().setRenderStrategy(RenderStrategy.ONE_PASS_RENDER);
    
    StatefulPage page = new StatefulPage();
    tester.startPage(page);
    
    // The bug only manifests with REDIRECT_TO_BUFFER
    assertNotNull(tester.getLastRenderedPage());
}
```
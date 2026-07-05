---
name: ajax-timer-behavior-parent-resolution
description: When an AbstractAjaxTimerBehavior is attached to a component, it calls
  getComponent().findParent(Page.class) during onComponentTag. If the behavior's component
  is not yet attached to a Page (e.g., added after the page has been rendered), findParent
  returns null, causing the timer to not be rendered. Test for this by checking that
  timer-related JavaScript ("Wicket.Timer.set") is rendered only when the behavior
  is added before page render or when explicitly attached to a Page.
code_tags:
- AJAX_TIMER_BEHAVIOR_ATTACHMENT
- COMPONENT_PARENT_NAVIGATION
test_pattern: STATE_TEST
---

# ajax-timer-behavior-parent-resolution

## Instructions

# Ajax Timer Behavior Parent Resolution

## Instructions

- WHEN the TG encounters an `AbstractAjaxTimerBehavior` (or its subclass `AjaxSelfUpdatingTimerBehavior`) being added to a component via `component.add(behavior)`, and the behavior's lifecycle methods (`onComponentTag`, `onAdded`, `onRemove`, `onDetach`) use `getComponent().findParent(Page.class)` to resolve the parent page:

  - THEN the TG should write a test that verifies the timer behavior's JavaScript output ("Wicket.Timer.set" / "Wicket.Timer.clear") is correctly generated based on when the behavior is attached to the component tree.
  
  - Specifically, the TG should write a test that adds the timer behavior to a component **after** the page has been rendered (e.g., via an Ajax request), and verify that the expected timer JavaScript is rendered. The bug manifests when `findParent(Page.class)` returns `null` because the component is not yet attached to a Page at the time `onComponentTag` is called. This causes the timer to silently not output its JavaScript.

  - Use `tester.executeAjaxEvent(...)` to trigger an Ajax request that adds the timer behavior, then use `tester.assertContains("Wicket.Timer.set", ...)` or a custom `assertMatches` helper to verify the expected JavaScript appears in the response.

  - **_Common pitfall_**: Only testing timer behavior by adding it to the page **before** render (in `onInitialize()` or constructor). This misses the bug entirely because `findParent(Page.class)` works fine during initial page rendering. The bug only manifests when the behavior is added **dynamically during an Ajax request**.

  - **_Common pitfall_**: Assuming that because the behavior's `onAdded()` or `onComponentTag()` methods don't throw exceptions, the timer JavaScript is correctly rendered. In this bug, `findParent` silently returns `null`, so no exception is thrown — the timer simply doesn't appear in the JavaScript output.

  - **_Example (correct test)_**: Add the timer behavior inside an Ajax event handler, then check the Ajax response for "Wicket.Timer.set":
    ```java
    @Test
    public void addedInAjaxSetsTimout()
    {
        // Set up a page with a component that can be Ajax-updated
        MockPageWithLinkAndComponent page = new MockPageWithLinkAndComponent();
        page.add(new Link<Void>(MockPageWithLinkAndComponent.LINK_ID) {
            @Override
            public void onClick() {
            // add timer behavior via Ajax
            }
        });
        // ... execute Ajax event that adds the behavior ...
        // assertEquals(1, assertMatches("Wicket.Timer.set", 1));
    }
    ```

  - **_Example (incorrect test)_**: Only testing timer behavior added during page construction:
    ```java
    @Test
    public void timerWorksOnPageLoad() {
        // This test passes on both buggy and fixed versions — it never catches the bug
        MockPageWithLinkAndComponent page = new MockPageWithLinkAndComponent();
        AbstractAjaxTimerBehavior timer = new AbstractAjaxTimerBehavior(Duration.seconds(1)) {};
        component.add(timer);
        tester.startPage(page);
        tester.assertContains("Wicket.Timer.set");
    }
    ```

  - Verify that the count of `Wicket.Timer.set` calls in the Ajax response matches the expected number (e.g., 1), not 0.
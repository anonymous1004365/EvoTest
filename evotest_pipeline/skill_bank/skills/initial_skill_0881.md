---
name: ajax-timer-behavior-script-rendering
description: When testing Ajax timer behaviors, verify that the behavior correctly
  contributes its JavaScript to the Ajax response during an Ajax update. This skill
  helps detect bugs where a behavior's lifecycle events (onComponentTag, onAdded,
  etc.) fail to register the necessary JavaScript for proper Ajax rendering.
code_tags:
- ARGUMENT_VALIDATION
- STATE_MUTATION
- BEHAVIOR_LISTENER_INDEX_SHIFT
- AJAX_TIMER_BEHAVIOR_ATTACHMENT
- AJAX_BEHAVIOR_SETUP
test_pattern: STATE_TEST
---

# ajax-timer-behavior-script-rendering

## Instructions

# Ajax Timer Behavior Script Rendering

## Instructions

- WHEN testing an Ajax timer behavior (e.g., `AbstractAjaxTimerBehavior` or `AjaxSelfUpdatingTimerBehavior`) that is added/initialized in `onComponentTag` or similar setup methods
- THEN the test MUST simulate an Ajax request (e.g., using `WicketTester.executeAjaxEvent()` or a custom `AjaxRequestTarget`) and verify that the contributed JavaScript is present in the response
- Specifically, test the state where a behavior is added to a component during `onComponentTag`, and then an Ajax update is triggered via `target.add(component)`. Verify that `1` script header/footer contribution is included for the behavior — NOT `0`
- Include a test that calls `tester.executeAjaxEvent(component, "click")` or similar after the component's markup has been rendered, and then asserts on the number of `<script>` elements or encoded JavaScript contributions for the timer behavior
- Common pitfalls to avoid:
  - Testing only static/non-Ajax rendering (e.g., just calling `tester.startComponentInPage()` and checking markup without triggering an Ajax update)
  - Forgetting to call `target.add(component)` inside the behavior's event handler to re-render the component on Ajax
  - Assuming that the behavior's `renderHead()` or `getScript()` logic is correctly invoked — you must assert on the **Ajax response** content, not just page rendering
  - Failing to account for the fact that behavior attachment order or index in the component's behavior list can affect whether the script is included
- Correct example:

```java
// GOOD: Verifies the timer behavior contributes exactly 1 script to Ajax response
WicketTester tester = new WicketTester();
TestPage page = new TestPage();
tester.startPage(page);
// Trigger an Ajax event on the component
tester.executeAjaxEvent(page.getComponent(), "click");
// Assert on the last Ajax response
String response = tester.getLastResponse().getDocument();
// Expect exactly 1 script contribution from the timer behavior
assertThat("There should be 1 and only 1 script in the markup for this behavior, but 0 were found",
    countScripts(response), is(1));
```

- Incorrect example:

```java
// BAD: Only checks page render, not Ajax response
WicketTester tester = new WicketTester();
TestPage page = new TestPage();
tester.startPage(page);
// This passes even if the behavior's Ajax script contribution is broken
assertNotNull(page.getComponent().getBehaviorByClass(AjaxSelfUpdatingTimerBehavior.class));
```
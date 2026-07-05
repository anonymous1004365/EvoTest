---
name: ajax-behavior-rendering-output-validation
description: When testing AJAX behavior rendering output, compare the rendered HTML/JavaScript
  output against an expected baseline file to catch missing or malformed event handler
  registrations, especially for onChange and similar DOM event behaviors.
code_tags:
- AJAX_BEHAVIOR_SETUP
- STATE_MUTATION
test_pattern: STATE_TEST
---

# ajax-behavior-rendering-output-validation

## Instructions

# AJAX Behavior Rendering Output Validation

## Instructions

- WHEN the TG encounters a class that extends `AbstractDefaultAjaxBehavior` or implements an AJAX behavior that registers DOM event handlers (e.g., `onchange`, `inputchange`, `click`)
- THEN the TG should write a test that renders the component/page to an HTML string using a `WicketTester` (or similar test harness) and compares the output against a known expected HTML file (a "golden file" or baseline), verifying that the JavaScript callback code contains the correct event name binding — for example, `"e":"inputchange change"` (note the space between event names) must be present in the rendered AJAX callback payload for an `onchange` behavior attached to an `<input>` element.

- **Concrete verification**: Call `executeTest(TestPageClass.class, "TestPageClass_expected.html")` or equivalent, where the expected file contains the precise JavaScript/Ajax channel registration string including the bound event name. On the buggy version, the test should FAIL because the expected event name format (e.g., `"inputchange change"`) differs from the buggy output (e.g., `"inputchange"` or `"inputchange change"` — the key is to check the exact space-separated list of events in the callback descriptor JSON).

- **Common pitfalls**:
  - Testing only that the behavior is attached (component-level) without testing the rendered JavaScript output — the bug may only appear in the serialized callback descriptor.
  - Assuming that a single event name is sufficient when multiple event names should be space-separated in the callback JSON (e.g., `"e":"inputchange change"` not `"e":"inputchange"`).
  - Not using a golden file comparison — inline string assertions can miss subtle whitespace/formatting differences in the rendered output.
  - Forgetting that the event handler registration format may differ between the HTML `onchange` attribute and the Wicket Ajax channel descriptor, requiring separate verification of both.

- **Correct example**:
```java
@Test
public void rendering()
{
    tester.executeTest(OnChangeAjaxBehaviorTestPage.class, 
        "OnChangeAjaxBehaviorTestPage_expected.html");
}
```
Where `OnChangeAjaxBehaviorTestPage_expected.html` contains:
```
"e":"inputchange change"
```
This catches if the behavior outputs `"e":"inputchange"` (missing the ` change` space-separated suffix).

- **Incorrect example**:
```java
@Test
public void rendering()
{
    // Only checks component attachment, not rendered output
    assertNotNull(behavior);
    assertTrue(component.getBehaviors().contains(behavior));
}
```
This test passes on buggy code because the behavior is attached — it misses the rendering bug in the JS serialization output.
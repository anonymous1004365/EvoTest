---
name: onChangeAjaxBehavior-event-dispatch-testing
description: When testing Ajax behaviors that conditionally dispatch different JavaScript
  events based on component type (e.g., TextField/TextArea vs other FormComponents),
  verify the rendered markup contains the correct event name for each component type.
  Use WicketTester.executeTest() with expected HTML to catch regression.
code_tags:
- EVENT_TYPE_DISPATCH
- COMPONENT_TREE_NAVIGATION
- VALIDATION
- STATE_MUTATION
test_pattern: PARAMETRIC_TEST
---

# onChangeAjaxBehavior-event-dispatch-testing

## Instructions

# OnChangeAjaxBehavior Event Dispatch Testing

## Instructions

- WHEN the TG encounters a behavior that extends `AjaxFormComponentUpdatingBehavior` and overrides `updateAjaxAttributes()` to conditionally set different event names based on `component instanceof TextField || component instanceof TextArea` (e.g., setting `"inputchange change"` for text components and `"change"` for others)
- THEN the TG should write a parametric test that uses `WicketTestCase.executeTest()` with an expected HTML file to verify the rendered Ajax event handler for each component type:
  - For `TextField` / `TextArea` components: expect the `"e"` parameter in the Ajax call to be `"inputchange change"`
  - For `DropDownChoice` / non-text form components: expect the `"e"` parameter to be just `"change"`
  - The test page should include one instance of each component type (e.g., a `TextField<String>` and a `DropDownChoice<?>`)
  - The expected HTML file must be hand-crafted to contain both patterns

- WHEN constructing the expected HTML, the TG MUST include the `Wicket.Ajax.ajax(...)` calls verbatim as the production code generates them, not as a template. The expected file needs to match the exact output.

- Common pitfalls:
  - Testing only `TextField` components while ignoring `DropDownChoice` or other non-text form components — this would miss the bug where non-text components incorrectly receive `"inputchange change"` instead of `"change"`
  - Testing only the Java-side behavior (e.g., checking `AjaxRequestAttributes.getEventNames()`) without asserting the rendered markup — the bug manifests in the generated JavaScript, not in the Java model
  - Using `tester.startPage()` and `tester.assertContains()` instead of `executeTest()` with a full expected HTML file — this would be less precise and could miss subtle rendering differences

- Correct example: Create a `OnChangeAjaxBehaviorTestPage` with a `TextField` (bound to `"inputchange change"`) and a `DropDownChoice` (bound to `"change"`), then call `executeTest(OnChangeAjaxBehaviorTestPage.class, "OnChangeAjaxBehaviorTestPage_expected.html")`. The expected HTML must contain:
  ```
  Wicket.Ajax.ajax({"u":"...-form-field","m":"POST","c":"field1","e":"inputchange change"});;
  Wicket.Ajax.ajax({"u":"...-form-dropDown","m":"POST","c":"dropDown2","e":"change"});;
  ```

- Incorrect example: Only testing `TextField` with `"inputchange change"` without asserting that `DropDownChoice` gets `"change"`, or only checking attributes in `updateAjaxAttributes()` without verifying the rendered markup.
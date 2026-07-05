---
name: component-ajax-region-markup-id
description: When a component has setOutputMarkupPlaceholderTag(true) and a behavior
  (or the component itself) implements IAjaxRegionMarkupIdProvider, the placeholder
  tag's id attribute must use the provider's getAjaxRegionMarkupId() return value
  rather than the component's default markup id. Use this skill to test that the placeholder
  tag uses the custom ajax region markup id.
code_tags:
- ARGUMENT_VALIDATION
- BOUNDARY_CHECK
- EDGE_CASE_INPUT
- NULL_CHECK
- CONDITIONAL_BRANCH
- COMPONENT_TREE_NAVIGATION
test_pattern: PARAMETRIC_TEST
---

# component-ajax-region-markup-id

## Instructions

# Component Ajax Region Markup Id in Placeholder Tag

## Instructions

- WHEN the TG sees code that calls `setOutputMarkupPlaceholderTag(true)` on a component AND the component (or one of its behaviors) implements `IAjaxRegionMarkupIdProvider`
- THEN the TG should write a test that:
  1. Creates a component (e.g., a `Form`) that calls `setVisible(false)` and `setOutputMarkupPlaceholderTag(true)`
  2. Adds a behavior that implements `IAjaxRegionMarkupIdProvider` — the behavior's `getAjaxRegionMarkupId(Component)` method should return a distinct custom id string (e.g., `component.getMarkupId() + "_region"`)
  3. Starts the page with `tester.startPage(...)` 
  4. Verifies that the rendered HTML contains the custom region id in the placeholder tag, e.g., `tester.assertContains("<form id=\"..._region\" style=\"display:none\">")`
  5. Uses `tester.assertContains()` or `tester.assertContainsNot()` to check that the placeholder tag uses the custom region ID, NOT the component's default markup ID

- WHEN building such a test, the TG should:
  - Create a behavior class extending `Behavior` and implementing `IAjaxRegionMarkupIdProvider`
  - Override `getAjaxRegionMarkupId(Component)` to return a string that combines the component's `getMarkupId()` with a distinguishing suffix (e.g., `"_region"`)
  - Make the component invisible (`setVisible(false)`) so the placeholder tag is rendered
  - Add the behavior to the component

- Common pitfalls to avoid:
  - Testing only with `getAjaxRegionMarkupId()` on the component itself (when the component directly implements `IAjaxRegionMarkupIdProvider`) — also test with the provider on a **behavior**, as the bug was specifically about behaviors implementing `IAjaxRegionMarkupIdProvider` being ignored
  - Forgetting to call `setOutputMarkupPlaceholderTag(true)` — without it no placeholder tag is rendered
  - Forgetting to call `setVisible(false)` — the placeholder tag only renders when the component is invisible
  - Using the component's own default markup id in the assertion string — the test must verify the custom region ID from the provider

### Correct Example

```java
@Test public void placeholderTagUsesAjaxRegionMarkupIdFromBehavior()
{
    tester.startPage(new WebPage() {
        @Override protected void onInitialize() {
            super.onInitialize();
            Form<?> form = new Form<Void>("form");
            form.setVisible(false);
            form.setOutputMarkupPlaceholderTag(true);
            form.add(new Behavior() implements IAjaxRegionMarkupIdProvider {
                @Override
                public String getAjaxRegionMarkupId(Component component) {
                    return component.getMarkupId() + "_region";
                }
            });
            add(form);
        }
    });
    tester.assertContains("<form id=\"form_region\" style=\"display:none\">");
}
```

### Incorrect Example (what would pass on buggy code)

```java
@Test public void placeholderTagUsesDefaultMarkupId()
{
    // This test only checks the default markup id, missing the bug
    tester.startPage(testPage);
    tester.assertContains("<form id=\"form1\" style=\"display:none\">");
    // On the buggy version, this would pass even though the custom
    // region ID from the behavior was ignored
}
```
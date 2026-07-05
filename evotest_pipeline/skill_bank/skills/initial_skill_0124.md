---
name: enclosure-form-url-generation
description: Teaches testing for Wicket Enclosure components that wrap a Form, where
  the enclosure's visibility condition (determined by child components) affects the
  form's action URL generation — specifically, whether a bookmarkable URL or a page
  render URL is produced.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- NULL_CHECK
- ENCLOSURE_INTERACTION
- CONDITIONAL_BRANCH
test_pattern: PARAMETRIC_TEST
---

# enclosure-form-url-generation

## Instructions

# Enclosure-Form Interaction: Action URL Generation

## Instructions

- WHEN the TG encounters a Wicket `Enclosure` component that wraps a `Form` (or components inside a `Form`), where the Enclosure's visibility is controlled by child component conditions (e.g., `WebMarkupContainer.setVisible(boolean)` on a child of the Enclosure)
- THEN the TG should write a **parametric test** that:
    1. Creates a page with an `Enclosure` whose `visible` condition depends on a child component's state (e.g., a child `WebMarkupContainer` that can be toggled visible/invisible)
    2. Inside that `Enclosure`, places a `Form` with an `IFormSubmitListener` (e.g., a `Button` or `SubmitLink`)
    3. Renders the page in **both** states (child visible and child invisible/initially invisible)
    4. Uses `wicketTester.clickLink(...)` or `wicketTester.newFormTester().submit()` to trigger form submission
    5. **Verifies** the form's `action` attribute in the rendered HTML — expected:
        - When Enclosure is visible and form is present: action URL should be a **page render URL** (e.g., `./page?0-1.IFormSubmitListener...`)
        - When Enclosure is invisible (form not rendered): action URL should be a **bookmarkable URL** (e.g., `./bookmarkable/...`) or the form should not appear in the output at all
    6. The test should **fail on the buggy version** by comparing the actual rendered HTML against an expected result file or string — specifically, the form action URL should be wrong when the enclosure is initially invisible

- **Common pitfalls to avoid**:
    - Testing only with the enclosure visible (the bug only manifests when the enclosure is initially invisible and the form submits to a bookmarkable URL instead of a page render URL)
    - Using only String type components inside the enclosure instead of actual Form+Button components that trigger form submission
    - Not checking the specific `action` attribute of the `<form>` tag in the rendered HTML output
    - Testing with `tester.startPage()` only once — the test must run in at least two configurations (visible vs invisible, or use `tester.getRequest().setRequestParameters()` to simulate form submission)

- **Correct example** (Java, using WicketTester):
```java
@Test
public void testEnclosureFormActionUrl() {
    // Create page where Enclosure's visibility depends on a model/child
    // EnclosurePage_9 pattern: Form inside Enclosure, child container controls visibility
    wicketTester.startPage(EnclosurePage_9.class);
    
    // Submit the form via a button click
    wicketTester.clickLink("form:submit");
    
    // Assert the rendered page has correct action URL
    // Expected on fixed version: action="./page?0-1.IFormSubmitListener..."
    // Buggy version produces: action="./bookmarkable/org.apache.wicket...IFormSubmitListener..."
    wicketTester.assertResultPage(EnclosurePageExpectedResult_9.class);
}
```

- **Incorrect example** (would miss the bug):
```java
// BAD: Only tests visible enclosure state, never submits the form
@Test
public void testEnclosureRendering() {
    // This only checks initial render, not form submission URL
    wicketTester.startPage(EnclosurePage_9.class);
    wicketTester.assertContains("form");
    // Never submits the form to check the action URL
}
```
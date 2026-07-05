---
name: stateless-form-submitlink-input-name-encoding
description: When a StatelessForm contains a SubmitLink component, the form action
  URL must properly exclude the submit link's input name from query parameters. Without
  this, the link's name leaks into the action URL, breaking statelessness and causing
  Wicket to fail redirecting to the correct page.
code_tags:
- VALIDATION
- STATE_MUTATION
test_pattern: INTERACTION_TEST
---

# stateless-form-submitlink-input-name-encoding

## Instructions

# StatelessForm SubmitLink Input Name Encoding

## Instructions

- WHEN the code under test involves a `StatelessForm` that contains a `SubmitLink` component with a specific `inputName` (e.g., `"submitLink1"`)
- THEN the TG MUST write a test that:
  1. Creates a `StatelessForm` with a `SubmitLink` that has a custom wicket:inputName attribute (e.g., `"submitLink1"`)
  2. Renders the form to a `Response` (e.g., `StringResponse`)
  3. Asserts that the `<form action="..."` attribute does NOT contain the submit link's input name as a query parameter
  4. Specifically verifies that the action URL does not contain `?submitLink1=...` or `&submitLink1=...`
  5. Verifies that the action URL is valid (not empty, starts with `/`) and contains no unexpected query parameters

- This applies when the `SubmitLink` in a `StatelessForm` overrides `onSubmit` and the form's `getActionUrl()` method is called during render. The bug is that the submit link's component path or input name leaks into the form action URL, causing a malformed URL that prevents proper form submission/redirect.

- Common pitfalls to avoid:
  - Testing only the form's submit behavior (button click) without checking the rendered HTML action URL
  - Testing only that the form renders without errors, not checking the URL content
  - Assuming `SubmitLink` in a `StatelessForm` works the same as in a regular `Form` — stateless forms have different URL encoding requirements
  - Using only GET method forms — the bug may only manifest with POST method forms where the action URL is generated differently

### Correct Example:

```java
@Test
public void submitLinkInputNameNotEncodedIntoFormAction()
{
    // Create a StatelessForm with a SubmitLink
    StatelessForm<Void> form = new StatelessForm<Void>("form")
    {
        @Override
        protected void onSubmit()
        {
            // custom submit logic
        }
    };
    
    SubmitLink submitLink = new SubmitLink("submit")
    {
        @Override
        public void onSubmit()
        {
            // custom link submit logic
        }
    };
    submitLink.setInputName("submitLink1");
    form.add(submitLink);
    
    // Render the page/form
    tester.startPage(new MyPage(form));
    String response = tester.getLastResponse().getDocument();
    
    // Extract the form action URL
    String actionUrl = /* parsed from response using e.g. JSoup */;
    
    // Assert that the submit link's input name is NOT in the action URL
    assertThat(actionUrl, not(containsString("submitLink1")));
    assertThat(actionUrl, not(containsString("?submit")));
}
```

### Incorrect Example:

```java
// BAD: Only tests form submission, not the rendered action URL
@Test
public void submitLinkWorks()
{
    tester.startPage(new MyPage());
    tester.clickLink("form:submit");
    tester.assertRenderedPage(NextPage.class); // May pass even if URL is subtly broken
}
```
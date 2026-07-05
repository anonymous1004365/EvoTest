---
name: render-css-reference-url-validation
description: When rendering CSS references that may have a URL instead of a resource
  reference, the TG should validate that the URL is not null or empty before rendering,
  otherwise an IllegalArgumentException is thrown. Apply this skill when testing methods
  that render CSS/JavaScript references with conditional logic for URL vs resource.
code_tags:
- NULL_CHECK
- TYPE_CONVERSION
- VALIDATION
test_pattern: EXCEPTION_TEST
---

# render-css-reference-url-validation

## Instructions

# Render CSS Reference URL Validation

## Instructions

- WHEN the TG encounters a `renderCSSReference` or similar header contribution method that conditionally handles CSS references based on whether the reference has a URL (e.g. `ResourceReference.getUrl()` is non-null) vs a proper resource reference
- THEN the TG should test with a CSS reference that returns a **null or empty URL** from `getUrl()` to verify the method throws an `IllegalArgumentException` with the message "url cannot be empty or null"
- Specifically, use a `PackageResourceReference` subclass that overrides `getUrl()` to return `""` (empty string) or `null`, and ensure the correct `Condition` (e.g., a custom condition that evaluates to true) is set so the conditional rendering path executes
- The test should verify that the exception is thrown on rendering, and that the exception message contains "url cannot be empty or null"
- Common pitfalls:
  - Only testing with valid/well-formed CSS references and URLs; the bug manifests specifically when the URL is empty/null
  - Forgetting to set a Condition that evaluates to true, causing the conditional render path to be skipped entirely
  - Testing with `org.apache.wicket.markup.html.internal.HeaderResponse` directly without going through a proper page/render pipeline — use `PageRenderer` or `tester.executeTest()` to trigger header rendering

### Correct example (Java pseudo-code):

```java
// Override getUrl to return empty string
PackageResourceReference cssRef = new PackageResourceReference(MyPage.class, "style.css") {
    @Override
    public String getUrl() {
        return "";
    }
};
// Set condition to true so the render path is taken
cssRef.setCondition(Condition.alwaysTrue());
// Add the CSS reference to the page and render
Page page = new MyPage();
page.add(new CssHeaderItem(cssRef));
tester.startPage(page);
// Expect exception during render
// ...
```

### Incorrect example (Java pseudo-code):

```java
// BAD: Only tests with a valid URL
PackageResourceReference cssRef = new PackageResourceReference(MyPage.class, "style.css");
cssRef.setCondition(Condition.alwaysTrue());
page.add(new CssHeaderItem(cssRef));
tester.startPage(page);
// This passes but doesn't catch the empty URL bug
```

### Incorrect example 2 (Java pseudo-code):

```java
// BAD: Forgets to set a Condition, so the conditional path never executes
PackageResourceReference cssRef = new PackageResourceReference(MyPage.class, "style.css") {
    @Override
    public String getUrl() {
        return "";
    }
};
page.add(new CssHeaderItem(cssRef));
tester.startPage(page);
// No exception because the condition check skipped the render
```
---
name: wicket-page-rendering-validation
description: WHEN tests render Wicket pages and verify the rendered HTML markup, THEN
  use executeTest() with the page class and expected HTML file to catch rendering
  bugs like missing/incorrect component output in the markup. The test should compare
  the rendered result against a static expected HTML file.
code_tags:
- HTML_RENDERING
test_pattern: PARAMETRIC_TEST
---

# wicket-page-rendering-validation

## Instructions

# Wicket Page Rendering Validation

## Instructions

WHEN the TG encounters a Wicket `WebPage` class with component markup (e.g., `SimplePage_13`, `MarkupInheritanceExtension_13`, `HeaderSectionPage_13`) that should render specific output (HTML, CSS, JavaScript, or component content), AND the page includes components like `WebMarkupContainer`, `Label`, `Link`, `AjaxFallbackLink`, or `Panel` that produce contribution headers or body content:

- THEN the TG should write a test that calls `executeTest(PageClass.class, "ExpectedResultFile.html")` where `PageClass` is the page under test and `ExpectedResultFile.html` is a static expected HTML result file placed in the same package directory.
- The test should be annotated with `@Test` and throw `Exception`.
- The expected HTML file should contain the **full rendered page output** including DOCTYPE, html/head/body tags, component contributions (e.g., Wicket AJAX JavaScript resources, wicket-ajax-jquery.js, JQueryResourceReference scripts), and page-specific markup.
- When the bug involves markup inheritance or header section contributions, verify that the expected HTML contains all contributed `<script>` and `<style>` tags, plus any wicket:id containers with correct attributes.

**Common pitfalls to avoid:**
- ❌ Testing only a substring of the rendered output instead of the full page rendering.
- ❌ Not including the expected HTML result file in the test resources directory alongside the test class.
- ❌ Using `executeTest(String, String)` overload without proper markup file mapping.
- ❌ Forgetting to import `org.apache.wicket.util.tester.WicketTester` and set up the tester in `@Before` method.

**Example (correct):**
```java
@Test
public void renderHomePage_13() throws Exception
{
    executeTest(SimplePage_13.class, "SimplePageExpectedResult_13.html");
}

@Test
public void renderHomePage_13() throws Exception
{
    executeTest(MarkupInheritanceExtension_13.class, "MarkupInheritanceExtensionExpectedResult_13.html");
}

@Test
public void renderHomePage_13() throws Exception
{
    executeTest(HeaderSectionPage_13.class, "HeaderSectionPageExpectedResult_13.html");
}
```

**Example (incorrect — partial check):**
```java
@Test
public void renderHomePage_13() throws Exception
{
    // WRONG: only checking part of the rendered page
    String response = tester.renderPage(SimplePage_13.class).toString();
    Assert.assertTrue(response.contains("some text"));
}
```
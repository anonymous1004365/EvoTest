---
name: ajax-domready-script-ordering
description: When components contribute JavaScript via both Ajax behaviors and header
  contributions with domReady priority, the TG should test that the order of execution
  is preserved across both normal and Ajax requests. Covers ordering between behavior-injected
  scripts and header-contributed scripts in Ajax responses.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
- BOUNDARY_CHECK
- ORDER_DEPENDENCY
- STATE_MUTATION
- AJAX_SCRIPT_DECORATION
test_pattern: PARAMETRIC_TEST
---

# ajax-domready-script-ordering

## Instructions

# Ajax DomReady Script Ordering

## Instructions

- WHEN the TG encounters a code path where multiple AJAX behaviors contribute JavaScript that runs on `domReady`, AND header contributions also produce `domReady` scripts
- THEN the TG should write a parametric test that:
  1. Creates a page with multiple components, each contributing a script via a different mechanism (e.g., one via an AJAX behavior's `respond()` or `getScript()`, another via a header contribution's `renderHead()`)
  2. Triggers an AJAX request (e.g., click event) that updates one of those components
  3. Captures the full Ajax response (including header contributions and behavior-generated scripts)
  4. Asserts that the order of `domReady` JavaScript execution in the Ajax response matches the order expected from the request: behavior-specific scripts should appear BEFORE header-contributed domReady scripts in the Ajax response
- The test should verify that:
  - When the page is initially rendered, domReady scripts from behaviors and headers appear in the correct order
  - When an AJAX update occurs, the domReady scripts in the AJAX response preserve the same relative ordering (behavior scripts before header scripts, or the specific order defined by component hierarchy)
  - Use string matching on the JavaScript content inside `<![CDATA[...]]>` sections of the Ajax response to verify execution order
- Common pitfalls to avoid:
  - Only testing one mechanism (e.g., only AJAX behaviors, not header contributions)
  - Only testing initial page render, not the Ajax response
  - Not capturing the full Ajax response body including header-contribution sections
  - Assuming behavior scripts and header scripts are ordered independently without considering their interleaving
  - Checking only that all scripts are present, not that they execute in the correct order

## Example

Correct test approach:
```java
@Test
public void domReadyOrder() throws Exception
{
    tester.startPage(DomReadyOrderPage.class);
    
    // Test initial render order
    String doc = tester.getLastResponseAsString();
    assertScriptOrder(doc, "Wicket.Ajax.ajax", "test1", "test2", "test3");

    // Trigger Ajax behavior that updates test1
    tester.clickLink("test1");
    
    // Verify Ajax response preserves order: behavior script before header scripts
    String ajaxResponse = tester.getLastResponseAsString();
    assertThat(ajaxResponse, containsString("Wicket.Ajax.ajax"));
    assertScriptOrder(ajaxResponse, "test1", "test2");
}

private void assertScriptOrder(String response, String... scripts)
{
    int prevIndex = -1;
    for (String script : scripts) {
        int index = response.indexOf(script);
        assertTrue("Missing script: " + script, index > prevIndex);
        prevIndex = index;
    }
}
```

Incorrect test approach (misses the ordering bug):
```java
@Test
public void domReadyOrder() throws Exception
{
    tester.startPage(DomReadyOrderPage.class);
    // Only checks initial page render, not Ajax response
    assertTrue(tester.getLastResponseAsString().contains("Wicket.Ajax.ajax"));
    assertTrue(tester.getLastResponseAsString().contains("test1"));

    // Only checks Ajax response has required scripts, not their order
    tester.clickLink("test1");
    String ajaxResponse = tester.getLastResponseAsString();
    assertTrue(ajaxResponse.contains("Wicket.Ajax.ajax"));
    assertTrue(ajaxResponse.contains("test1"));
    // BUG: Missing ordering assertion - behavior and header scripts may be reversed
}
```
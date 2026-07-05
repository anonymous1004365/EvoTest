---
name: path-parameter-stripping-in-class-name
description: When parsing class names from URLs that may contain path parameters (semicolon-delimited
  segments like ";jsessionid=xxx"), the TG should test that such parameters are stripped
  from the class name before class resolution. This prevents ClassNotFoundException
  or NoClassDefFoundError when path parameters leak into the class name.
code_tags:
- ARGUMENT_VALIDATION
- STATE_MUTATION
- VALIDATION
test_pattern: EXCEPTION_TEST
---

# path-parameter-stripping-in-class-name

## Instructions

# Path Parameter Stripping in URL Class Name Resolution

## Instructions

- WHEN the TG encounters a method that parses a class name from a URL segment (e.g., `cleanClassName(String)`, `getPageClass(String)`, or any mapper code that calls `WicketObjects.resolveClass()` after extracting a class name from a URL path)
- THEN the TG should test that path parameters in the URL (semicolon-delimited segments such as `;something=else`, `;jsessionid=xxx`, etc.) are properly stripped from the class name BEFORE it is used for class resolution. Include a test case where the URL contains a class name followed by a path parameter like `MockPage;something=else` and verify that:
  1. The mapper successfully resolves the page (returns `RenderPageRequestHandler`, not `null` or throws `ClassNotFoundException`)
  2. The resolved page class is the expected class (e.g., `MockPage.class`)
  3. The page parameters are not polluted by the path parameter content
- Common pitfalls:
  - Testing only clean URLs without path parameters in class name position
  - Assuming the fix is in the mapper itself when it may be in the helper method (`cleanClassName()` in `AbstractComponentMapper`) — verify where the stripping happens
  - Expecting the path parameter to be preserved as a page parameter — it should be removed entirely, not passed through

### Correct Example
```java
@Test
public void decodePageClassWithPathParameters()
{
    Url url = Url.parse("wicket/bookmarkable/" + MockPage.class.getName() + ";something=else");
    IRequestHandler handler = encoder.mapRequest(getRequest(url));

    assertTrue(handler instanceof RenderPageRequestHandler);
    IRequestablePage page = ((RenderPageRequestHandler)handler).getPage();
    assertEquals(MockPage.class.getName(), page.getClass().getName());
    assertEquals(0, page.getPageParameters().getIndexedCount());
    assertTrue(page.getPageParameters().getNamedKeys().isEmpty());
}
```

### Incorrect Example (what would fail on buggy code)
```java
@Test
public void decodePageClassWithPathParameters_incorrect()
{
    Url url = Url.parse("wicket/bookmarkable/" + MockPage.class.getName() + ";something=else");
    IRequestHandler handler = encoder.mapRequest(getRequest(url));
    
    // WRONG: This assertion would fail on buggy version because the class 
    // resolution would include the path parameter, causing a ClassNotFoundException
    // or the handler would be null
    assertNotNull(handler);
}
```
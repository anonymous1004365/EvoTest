---
name: page-component-info-with-named-query-parameters
description: Teaches how to test URL parsing where PageComponentInfo is preceded by
  named query parameters (e.g., ?param1=value1&15-.4-foo-bar). The bug occurs when
  MapperUtils.getPageComponentInfo() fails to find the PageComponentInfo because a
  named parameter with both name and value appears before it in the query string.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
test_pattern: PARAMETRIC_TEST
---

# page-component-info-with-named-query-parameters

## Instructions

# PageComponentInfo Parsing with Interleaved Named Query Parameters

## Instructions

- WHEN the TG encounters code that parses a `PageComponentInfo` from a URL's query string (e.g., `MapperUtils.getPageComponentInfo(url)` or `PageComponentInfo.parse(s)`), specifically where the `PageComponentInfo` is embedded as a query parameter with only a name and no value (e.g., `?15-.4-foo-bar`)
- THEN the TG should test URLs where **named query parameters (with values) appear BEFORE the PageComponentInfo parameter** in the query string (e.g., `?param1=value1&15-.4-foo-bar`). The test must verify that the `PageComponentInfo` is still correctly extracted even though earlier parameters have both a name and a value.
- Include tests with:
  - Named parameter(s) with values before the PageComponentInfo (e.g., `?a=b&15-.4-foo-bar`)
  - Multiple named parameters before the PageComponentInfo (e.g., `?a=b&c=d&15-.4-foo-bar`)
  - PageComponentInfo without any named parameters before it (baseline — e.g., `?15-.4-foo-bar`)
  - No PageComponentInfo at all (null case)
- Verify that `PageComponentInfo.parse()` returns a non-null result with the correct `pageInfo` (e.g., page ID = 15), component path (e.g., "foo:bar"), and behavior index (e.g., 4).
- **Common pitfall**: Testing only with the PageComponentInfo as the first/only query parameter (e.g., `?15-.4-foo-bar`). The bug manifests when named parameters with values appear before the PageComponentInfo in the query string. Do NOT assume named parameters only appear at the end.
- **Another common pitfall**: Assuming `MapperUtils.getPageComponentInfo()` iterates parameters correctly; the method checks each parameter, so ensure the test URL has the parameter order that would expose the parsing bug.

### Correct Test Example
```java
@Test
public void testParseWithPrecedingNamedParameters()
{
    // PageComponentInfo: pageId=15, renderCount=null, behaviorIndex=4, componentPath="foo:bar"
    // Named parameter "param1=value1" appears BEFORE the PageComponentInfo
    Url url = Url.parse("some/mount/path?param1=value1&15-.4-foo-bar");
    PageComponentInfo info = MapperUtils.getPageComponentInfo(url);
    
    assertNotNull("PageComponentInfo should be found even with preceding named params", info);
    assertEquals(Integer.valueOf(15), info.getPageInfo().getPageId());
    assertNotNull(info.getComponentInfo());
    assertEquals("foo:bar", info.getComponentInfo().getComponentPath());
    assertEquals(Integer.valueOf(4), info.getComponentInfo().getBehaviorIndex());
}
```

### Incorrect Test Example
```java
@Test
public void testParseOnlyFirstParameter()
{
    // This only tests the case where no named parameters precede the PageComponentInfo
    // It will NOT catch the bug where earlier named parameters interfere
    Url url = Url.parse("some/mount/path?15-.4-foo-bar");
    PageComponentInfo info = MapperUtils.getPageComponentInfo(url);
    // This passes even on the buggy version — no regression detection
}
```
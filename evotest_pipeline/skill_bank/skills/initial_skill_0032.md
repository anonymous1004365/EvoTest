---
name: query-string-equals-sign-in-value
description: WHEN parsing URL query strings with encoded equals signs (=) in parameter
  values, THEN test that the parser correctly preserves equals signs that appear inside
  parameter values, not just the first occurrence. The bug causes a parser to split
  on every '=' character instead of only the first '=' per key=value pair.
code_tags:
- QUERY_STRING_PARSING
- STRING_PARSING
test_pattern: PARAMETRIC_TEST
---

# query-string-equals-sign-in-value

## Instructions

# Query String Parsing: Equals Sign in Parameter Values

## Instructions

- WHEN the TG encounters a URL query string parser that splits parameters on `&` and key-value pairs on `=`
- THEN the TG should test with query strings that contain **encoded equals signs (`%3D`) or raw equals signs (`=`) inside parameter values**, not just in key positions
- The parser must only split on the **first `=`** in each key=value pair and treat any subsequent `=` as part of the value
- Test with inputs like `?a=b%3Dc&d=e%3Df` — the expected result is that parameter `a` has value `b=c` (after decoding `%3D`), NOT that `a` has value `b` with a separate empty value for `c`
- Verify using `Url.parse(queryString)` and check `getQueryParameters()` returns the correct key-value pairs
- **Common pitfall**: Testing only with query strings where values contain no `=` signs, missing the bug where the parser naively splits on every `=` instead of only the first one

### Correct test approach:
```java
@Test
public void parseQueryStringWithEqualsSignInParameterValue()
{
    String s = "?a=b%3Dc&d=e%3Df";
    Url url = Url.parse(s);
    List<QueryParameter> params = url.getQueryParameters();
    assertEquals(2, params.size());
    assertEquals("a", params.get(0).getName());
    assertEquals("b=c", params.get(0).getValue()); // %3D decoded to =
    assertEquals("d", params.get(1).getName());
    assertEquals("e=f", params.get(1).getValue());
}
```

### Common pitfall — WRONG test (would pass on buggy code):
```java
@Test
public void parseQueryStringWithStandardValues() // Only tests simple case, misses the bug
{
    String s = "?a=b&c=d";
    Url url = Url.parse(s);
    List<QueryParameter> params = url.getQueryParameters();
    assertEquals(2, params.size());
    assertEquals("a", params.get(0).getName());
    assertEquals("b", params.get(0).getValue());
    assertEquals("c", params.get(1).getName());
    assertEquals("d", params.get(1).getValue());
}
```
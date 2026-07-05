---
name: post-parameter-name-null-value-handling
description: When a method processes URL query/post parameter names returning a StringValue,
  test that a null value for a non-null parameter name is correctly converted to an
  empty/null string rather than causing issues. This applies to parameter parsing/encoding
  code where null values need explicit handling.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
test_pattern: STATE_TEST
---

# post-parameter-name-null-value-handling

## Instructions

# Handling Null Values for Named Query Parameters

## Instructions

- WHEN the TG encounters a method that processes URL query parameters (e.g., parsing `Url.QueryParameter` objects, converting `StringValue` values, or encoding/decoding parameters)
- THEN it should test that a parameter with a non-null name but a null value (`new Url.QueryParameter("name", null)`) is correctly handled — specifically:
  - The method should not throw a `NullPointerException`
  - The method should produce a consistent, predictable result (e.g., the value should be `StringValue.valueOf(null)` which may be `null` or empty)
  - Verify that the returned `PageParameters` has the correct count of parameters and that the indexed value is as expected
- Common pitfalls to avoid:
  - Testing only with non-null parameter values and forgetting that null values are valid and must be handled
  - Testing only with the `getQueryParameters()` method but not with `getPostParameters()` (or vice versa) — the bug may exist in one path but not the other
  - Assuming that `Url.QueryParameter.getValue()` always returns non-null — it can return null if the query parameter has no value

### Example (Correct)

```java
@Test
public void decodePostParametersWithNullValues()
{
    // Create an empty URL and manually add parameters
    Url url = new Url(List.of("foo"));
    
    // Add a parameter with a null value
    url.getQueryParameters().add(new Url.QueryParameter("param1", null));
    
    PageParametersEncoder encoder = new PageParametersEncoder();
    PageParameters params = encoder.decodePageParameters(url);
    
    // The parameter should be present with null value
    assertEquals(1, params.getIndexedCount());
    // Depending on implementation, null may become null, empty string, or StringValue.valueOf(null)
    assertNotNull("Parameter 'param1' should be present", params.get("param1"));
}
```

### Example (Incorrect — too narrow)

```java
@Test
public void decodePostParameters()
{
    // Only tests with non-null values — misses the null-value bug
    Url url = new Url(List.of("foo"));
    url.getQueryParameters().add(new Url.QueryParameter("param1", "value1"));
    
    PageParametersEncoder encoder = new PageParametersEncoder();
    PageParameters params = encoder.decodePageParameters(url);
    
    assertEquals(1, params.getIndexedCount());
    assertEquals("value1", params.get("param1").toString());
    // No test with null values — won't catch this bug
}
```
---
name: url-query-string-separator-preservation
description: When resolving relative URLs, query string parameters must be separated
  from the rest of the URL by a '?' character. This skill teaches how to test that
  query string separators are correctly preserved during URL resolution, especially
  when the base URL has no query string but the relative URL does.
code_tags:
- NULL_CHECK
- VALIDATION
- ARRAY_INDEX_ACCESS
- STATE_MUTATION
test_pattern: STATE_TEST
---

# url-query-string-separator-preservation

## Instructions

# URL Query String Separator Preservation

## Instructions

- WHEN the TG encounters a `Url.resolveRelative(Url relative)` method that resolves a relative URL against a base URL (e.g., combining path segments, merging query parameters)
  - THEN the TG should verify that when the base URL has no query string (`fragment` is null or empty AND `queryParameters` is empty) but the relative URL contains query parameters (e.g., `?p1=v1`), the resolved URL correctly includes the `?` separator between the path and the query string in the string representation
  - The test should: create a base URL with path segments only (no query), create a relative URL with query parameters, call `resolveRelative(relative)`, then call `toString()` and verify the output contains `?` between the path and the first query parameter
  - Example: base = `Url.parse("c/a/b")`, relative = `Url.parse("?p1=v1")`. After `base.resolveRelative(relative)`, `base.toString()` should be `"c/a/b?p1=v1"` (with `?` separator), not `"c/a/bp1=v1"` (missing `?`)
  - Common pitfall #1: Testing only with base URLs that already have a query string — this masks the bug because the `?` is already present
  - Common pitfall #2: Only checking the query parameters list (e.g., `getQueryParameters()`) without checking the string output (`toString()`) — the `?` separator is only visible in the string representation
  - Common pitfall #3: Assuming that `toString()` will correctly reconstruct the `?` separator from an internal flag or state variable. The test must explicitly check the full string output.

- WHEN the TG writes a test for `resolveRelative` with query parameters
  - THEN it should always include at least one test case where the base URL's query string is empty and the relative URL brings query parameters, and verify `toString()` contains `?` before the query string
  - Correct example:
    ```java
    @Test
    public void resolveRelative_QueryParametersFromRelative()
    {
        Url baseUrl = Url.parse("c/a/b");
        Url relative = Url.parse("?p1=v1");
        baseUrl.resolveRelative(relative);
        assertEquals("c/a/b?p1=v1", baseUrl.toString());
    }
    ```
  - Incorrect example (missing `?` check):
    ```java
    @Test
    public void resolveRelative_QueryParametersFromRelative()
    {
        Url baseUrl = Url.parse("c/a/b");
        Url relative = Url.parse("?p1=v1");
        baseUrl.resolveRelative(relative);
        // Only checking query params exist, not the string representation
        assertEquals("p1=v1", baseUrl.getQueryString());
    }
    ```
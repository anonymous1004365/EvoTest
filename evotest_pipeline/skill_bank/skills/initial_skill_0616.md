---
name: null-data-resource-handling
description: WHEN creating tests for resource classes that extend BaseDataResource
  (like ByteArrayResource) and can be constructed without providing data, THEN test
  the null-data case where getData() returns null, and ensure the resource handles
  it gracefully by returning SC_NOT_FOUND rather than crashing with NullPointerException.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
- NULL_DATA_RESOURCE_HANDLING
test_pattern: EXCEPTION_TEST
---

# null-data-resource-handling

## Instructions

# Null Data Resource Handling

## Instructions

- WHEN the TG encounters a resource class that extends `BaseDataResource<T>` and has a constructor that accepts only `contentType` (no data parameter), e.g. `ByteArrayResource(String contentType)`
- THEN the TG MUST write a test that creates such a resource WITHOUT providing data and invokes it via `tester.startResource(resource)` or `resource.respond(attributes)`, and then verifies:
  1. The response status is `HttpServletResponse.SC_NOT_FOUND` (404)
  2. The response body is empty
- WHEN `BaseDataResource.newResourceResponse()` calls `getData(attributes)` and if it returns `null`, the existing code path already calls `response.setError(HttpServletResponse.SC_NOT_FOUND)` — the bug is that the subclass's `getLength()` method (e.g., `ByteArrayResource.getLength(byte[] data)`) calls `data.length` which throws `NullPointerException` when `data` is null, but this only happens if the null check in `newResourceResponse()` doesn't cover the path OR if `getLength()` is called before the null check.
- The TG should not assume that `getLength()` handles null — the test must explicitly trigger the full lifecycle to catch the `NullPointerException` or verify the SC_NOT_FOUND status is correctly returned.
- **Common pitfalls to avoid**:
  - Testing only the static or dynamic data paths (where data is non-null) and forgetting the no-data constructor path
  - Testing `getLength(null)` or `getData(null)` in isolation instead of testing the full `respond()` lifecycle
  - Assuming that because `newResourceResponse()` has a null check for data, the subclass methods won't be called with null — write the integration test anyway to be safe
  - Only testing that no exception is thrown, without verifying the HTTP 404 status code and empty body

### Correct example (Java/JUnit):
```java
@Test
public void noData() {
    ByteArrayResource resource = new ByteArrayResource("text/plain");
    tester.startResource(resource);

    assertEquals(HttpServletResponse.SC_NOT_FOUND, tester.getLastResponse().getStatus());
    assertEquals(0, tester.getLastResponse().getBinaryContent().length);
}
```

### Incorrect example (missing the null-data case):
```java
// Only testing static data — misses the null constructor bug!
@Test
public void staticResource() {
    ByteArrayResource resource = new ByteArrayResource("text/plain", new byte[] {1, 2, 3});
    tester.startResource(resource);
    assertEquals(200, tester.getLastResponse().getStatus());
}
```
---
name: exception-handler-response-caching-disabled
description: When testing exception handler classes that use a mocked WebResponse,
  verify that disableCaching() is called on the response to prevent caching of error
  pages. Mock the response before passing it to the handler and verify caching-disabled
  behavior.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- STATE_MUTATION
test_pattern: MOCK_TEST
---

# exception-handler-response-caching-disabled

## Instructions

# Exception Handler Should Disable Caching on Response

## Instructions

- WHEN the TG encounters an exception mapper/handler class (e.g., `DefaultExceptionMapper`) that takes a `RequestCycle` or `WebRequestCycle` parameter and internally uses `getWebResponse()` to obtain a `WebResponse` object:
  - THEN the TG should test that the handler calls `disableCaching()` on the `WebResponse` to prevent the error page from being cached by the browser.

- WHEN the TG is constructing a test for an exception handling method:
  - THEN the TG should create a mock `WebResponse` (e.g., using Mockito's `mock(WebResponse.class)`) and inject it into the request cycle so that `cycle.getWebResponse()` returns the mock.
  - THEN the TG should verify that `response.disableCaching()` was called exactly once after the exception handler runs.

- Common pitfalls:
  - Testing only the exception mapping result (e.g., checking the error page class) but forgetting to verify the side-effect of disabling caching on the response.
  - Passing a real `WebResponse` (e.g., `ServletWebResponse`) instead of a mock — this makes it harder to verify `disableCaching()` was invoked.
  - Injecting the mock response through `RequestCycle.setResponsePage()` or other component/response assignment instead of through the request cycle's `getWebResponse()` method chain.

- Example on `DefaultExceptionMapper`:

```java
// Correct test
@Test
public void shouldDisableCaching() {
    // Arrange
    WebResponse response = mock(WebResponse.class);
    RequestCycle cycle = mock(RequestCycle.class);
    when(cycle.getWebResponse()).thenReturn(response);
    DefaultExceptionMapper mapper = new DefaultExceptionMapper();

    // Act
    mapper.mapException(cycle, new RuntimeException("test"));

    // Assert
    verify(response).disableCaching();
}

// Incorrect test — verifies only the error page, ignores caching
@Test
public void shouldMapException() {
    RequestCycle cycle = mock(RequestCycle.class);
    DefaultExceptionMapper mapper = new DefaultExceptionMapper();
    AbstractErrorPage page = mapper.mapException(cycle, new RuntimeException("test"));
    assertNotNull(page);  // misses the disableCaching() verification
}
```
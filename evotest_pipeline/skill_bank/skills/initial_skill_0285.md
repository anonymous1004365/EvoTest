---
name: mock-http-session-type-guard
description: When a mock class expects its own specialized session type (e.g., MockHttpSession),
  the getSession() method should throw an informative exception if passed a non-mock
  HttpSession. Use this skill to write tests that verify the type guard works correctly.
code_tags:
- TYPE_CONVERSION
- EXCEPTION_HANDLING
test_pattern: EXCEPTION_TEST
---

# mock-http-session-type-guard

## Instructions

# Mock HttpSession Type Guard Testing

## Instructions

- WHEN the TG encounters a mock implementation (e.g., `MockHttpServletRequest`) that has a `getSession(boolean create)` method which checks whether an existing `HttpSession` is an instance of the mock's own session type (e.g., `MockHttpSession`)
- THEN it should write a test that:
  1. Creates a plain/real `HttpSession` object (e.g., using `EasyMock.createMock(HttpSession.class)` or `mock(HttpSession.class)`)
  2. Passes it into the mock request via `setSession(HttpSession)` or equivalent setter
  3. Calls `getSession(boolean create)` (or `getSession()`) on the mock request
  4. Asserts that an informative exception is thrown — specifically, verify the exception message matches the exact string thrown by the buggy code (e.g., `"MockHttpServletRequest knows how to work only with MockHttpSession"`)
- Include concrete examples with the actual class names: `MockHttpServletRequest`, `MockHttpSession`, `HttpSession`
- Common pitfalls to avoid:
  - Testing only with a `MockHttpSession` and missing the non-mock case entirely
  - Calling `getSession(true)` with `create=true` — the type guard may only fire when an existing non-mock session is set and `getSession(false)` is called
  - Forgetting to create a mock `HttpSession` via a mocking framework (e.g., Mockito, EasyMock) — a simple anonymous class implementation may not trigger the `instanceof` check correctly if it doesn't bypass the mock class hierarchy
  - Not asserting the exact exception message — the test should verify not just that an exception is thrown, but that it's the informative RuntimeException with the correct message

### Correct example (Java):
```java
@Test
public void getSessionFromNonMockHttpSession()
{
    MockHttpServletRequest request = new MockHttpServletRequest(null, null, null);
    HttpSession httpSession = EasyMock.createMock(HttpSession.class);
    request.setSession(httpSession);
    IllegalStateException e = Assert.assertThrows(IllegalStateException.class, () -> {
        request.getSession(false);
    });
    Assert.assertEquals("MockHttpServletRequest knows how to work only with MockHttpSession",
        e.getMessage());
}
```

### Incorrect example (Java):
```java
@Test
public void testGetSession()
{
    MockHttpServletRequest request = new MockHttpServletRequest(null, null, null);
    // BUG: Only testing with MockHttpSession, missing the non-mock case
    request.setSession(new MockHttpSession(null));
    HttpSession session = request.getSession(false);
    Assert.assertNotNull(session);
    // This test never exercises the type guard!
}
```
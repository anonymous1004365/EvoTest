---
name: reset-after-written-content-exception
description: When a response buffer transitions from buffering state to written content
  state, calling reset() must throw IllegalStateException. This skill teaches how
  to test state-dependent exception throwing for buffered web responses.
code_tags:
- BUFFERED_RESPONSE_RESET
- STATE_MUTATION
- EXCEPTION_HANDLING
test_pattern: EXCEPTION_TEST
---

# reset-after-written-content-exception

## Instructions

# Testing State-Dependent Exceptions in Buffered Web Responses

## Instructions

- WHEN the TG encounters a class that wraps a response buffer (like `HeaderBufferingWebResponse`) with a `buffering` boolean flag that tracks whether content has already been written
- THEN the TG should write a test that:
  1. Creates an instance of the response wrapper with a concrete delegate (e.g., `MockWebResponse`)
  2. Calls `reset()` on the wrapper while it is still in buffering state (no content written yet) — this should succeed without throwing
  3. Then writes content using `response.write("some content")`
  4. Then calls `reset()` again — this must throw `IllegalStateException` because content was already written (buffering flag is now `false`)
  5. Verify the exception with `@Test(expected = IllegalStateException.class)` or a try-catch with `fail()` in the catch block
- Concrete example from actual code: the `HeaderBufferingWebResponse.reset()` method checks `if (buffering)` — if true it calls `bufferedResponse.reset()`, otherwise it throws `new IllegalStateException("Response is no longer buffering!")`
- Common pitfalls:
  - NOT testing the successful reset before content is written — the bug is about the *stateful transition* from buffering to non-buffering. A test that only calls reset once after writing content might miss that the reset method is broken for both cases.
  - Using a mock instead of a concrete `MockWebResponse` — the test needs a real delegate that implements the `reset()` contract
  - Testing only with header operations but not writing actual content — content writing (`response.write(...)`) is what triggers `stopBuffering()`, which flips the `buffering` flag to `false`

### Correct example (from HeaderBufferingWebResponseTest):
```java
@Test
public void resetAfterWrittenContent()
{
    MockWebResponse originalResponse = new MockWebResponse();

    HeaderBufferingWebResponse response = new HeaderBufferingWebResponse(originalResponse);

    response.addHeader("key1", "value1");

    assertNull(originalResponse.getHeader("key1"));

    response.reset();  // reset while still buffering — should succeed

    response.write("written");  // triggers stopBuffering, buffering becomes false

    try
    {
        response.reset();  // reset after content written — must throw
        fail();
    }
    catch (IllegalStateException expected)
    {
    }
}
```

### Incorrect example:
```java
// WRONG: Only tests the exception case, not the successful reset before content
@Test(expected = IllegalStateException.class)
public void resetAfterWrittenContent_wrong()
{
    MockWebResponse originalResponse = new MockWebResponse();
    HeaderBufferingWebResponse response = new HeaderBufferingWebResponse(originalResponse);
    response.write("written");
    response.reset(); // throws, but doesn't verify the successful reset path
}

// WRONG: Uses mocking instead of real delegate
@Test(expected = IllegalStateException.class)
public void resetAfterWrittenContent_wrong2()
{
    WebResponse mock = Mockito.mock(WebResponse.class);
    HeaderBufferingWebResponse response = new HeaderBufferingWebResponse(mock);
    response.write("written");
    response.reset(); // Mock may not throw the correct exception
}
```
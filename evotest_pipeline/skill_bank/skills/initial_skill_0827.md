---
name: resource-stream-close-on-error
description: When a method accepts an InputStream and wraps it in another stream that
  performs cleanup in close(), a test should verify that if an IOException occurs
  during reading, the original stream is properly closed. This skill teaches testing
  resource cleanup under exceptional conditions.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
- BOUNDARY_CHECK
- RESOURCE_MANAGEMENT
test_pattern: EXCEPTION_TEST
---

# resource-stream-close-on-error

## Instructions

# Resource Stream Close on Error

## Instructions

- WHEN the TG encounters a method that accepts an `InputStream` parameter and passes it to a `writeStream(Attributes, InputStream)` or similar method that reads from the stream and may throw an `IOException`
- THEN the TG should write a test that:
  1. Creates an `InputStream` that throws an `IOException` during reading (e.g., override `read()` to throw `IOException`)
  2. Passes that stream to the method under test
  3. Catches the `IOException` in the test
  4. **Verifies that the stream was closed** by asserting that `stream.close()` was called (e.g., use a custom wrapper that records whether `close()` was invoked)
- Common pitfalls:
  - Testing only the happy path where the stream is consumed successfully
  - Forgetting that if a method wraps the stream (e.g., in a `GZIPInputStream` or similar), the outer stream's `close()` propagates to the inner stream, so checking the outer stream's close is sufficient
  - Not catching the `IOException` in the test — the test should handle the expected exception gracefully

## Example

### Correct test (what to do):

```java
@Test
public void writeStream_ThrowsIOException_StreamIsClosed() throws IOException
{
    // create an input stream that throws on read
    InputStream throwingStream = new InputStream()
    {
        boolean closed = false;

        @Override
        public int read() throws IOException
        {
            throw new IOException("read error");
        }

        @Override
        public void close() throws IOException
        {
            closed = true;
            super.close();
        }

        public boolean isClosed()
        {
            return closed;
        }
    };

    // wrap in a way that allows checking close
    InputStream wrapper = new InputStream()
    {
        boolean closed = false;

        @Override
        public int read() throws IOException
        {
            return throwingStream.read();
        }

        @Override
        public void close() throws IOException
        {
            closed = true;
            throwingStream.close();
        }

        public boolean isClosed()
        {
            return closed;
        }
    };

    Attributes attributes = new Attributes(...);
    try
    {
        callback.writeStream(attributes, wrapper);
        fail("Expected IOException was not thrown");
    }
    catch (IOException e)
    {
        // expected
    }

    assertTrue("The input stream must be closed when writeStream fails", wrapper.isClosed());
}
```

### Incorrect test (what to avoid):

```java
@Test
public void writeStream_ThrowsIOException()
{
    InputStream throwingStream = ...;
    Attributes attributes = ...;
    
    // BAD: only checks that the exception propagates
    assertThrows(IOException.class, () -> {
        callback.writeStream(attributes, throwingStream);
    });
    
    // BAD: does NOT verify that the stream was closed,
    // which could leak resources
}
```
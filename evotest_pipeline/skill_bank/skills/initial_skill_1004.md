---
name: urlconnection-getinputstream-npe-on-close
description: When closing an URLConnection via Connections.close() in a finally block,
  the close() method calls connection.getInputStream().close() for "file" protocol
  connections — but getInputStream() may return null, causing a NullPointerException
  that masks the original exception. This skill teaches you to test that resource
  cleanup code handles null from getInputStream() gracefully.
code_tags:
- RESOURCE_MANAGEMENT
- NULL_CHECK
test_pattern: EXCEPTION_TEST
---

# urlconnection-getinputstream-npe-on-close

## Instructions

# URLConnection getInputStream() Null Safety on Close

## Instructions

- WHEN the TG encounters code that calls `Connections.close(URLConnection)` or `Connections.closeQuietly(URLConnection)` — particularly in a `finally` block after a try block that opens connections
- THEN it should write a test that verifies the code handles the case where `connection.getInputStream()` returns `null` without throwing a `NullPointerException`. Specifically:
  - The `close()` method calls `connection.getInputStream().close()` when the connection's protocol is `"file"`. If `getInputStream()` returns null, this line will throw a `NullPointerException`.
  - The test should use a real `file:` URL that points to an existing local file to trigger the "file" protocol path in `Connections.close()`.
  - Verify that `Connections.getLastModified(URL)` with a `file:` URL successfully returns a non-null `Time` object with non-zero milliseconds, WITHOUT throwing a `NullPointerException` either from the main logic or from the `finally` block's cleanup.
  - Consider using `assertThat(lastModified, is(notNullValue()))` and `assertThat(lastModified.getMilliseconds(), is(not(0L)))`.
- Common pitfall: Only testing with `jar:` or `http:` URLs, missing the `file:` protocol path in `close()`. Another pitfall: Assuming `Connections.closeQuietly()` silently swallows all exceptions — it does, but it swallows the NPE too, so the bug manifests as a silent resource leak and the `getLastModified()` call may fail silently or return an unexpected result. Another pitfall: Not checking that the returned timestamp is non-zero, since a zero timestamp means "not available."

**Example (correct test):**
```java
@Test
public void getLastModified() throws Exception
{
    URL url = new URL("file:///some/existing/file.txt");
    Time lastModified = Connections.getLastModified(url);
    assertThat(lastModified, is(notNullValue()));
    assertThat(lastModified.getMilliseconds(), is(not(0L)));
}
```

**Example (incorrect test — only tests remote URL):**
```java
@Test
public void getLastModified() throws Exception
{
    URL url = new URL("http://localhost/some/resource");
    Time lastModified = Connections.getLastModified(url);
    // This doesn't exercise the "file" protocol path in close()
    // and misses the NPE bug entirely
}
```
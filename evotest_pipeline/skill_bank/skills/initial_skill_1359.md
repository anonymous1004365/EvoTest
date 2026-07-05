---
name: crypto-stream-close-on-read-failure
description: When implementing crypto/file streams that wrap underlying input streams,
  ensure streams are properly closed on all read failure paths. The TG should test
  that partial reads (e.g., reading into a buffer that has remaining capacity) trigger
  stream cleanup, not just successful reads.
code_tags:
- RESOURCE_MANAGEMENT
test_pattern: STATE_TEST
---

# crypto-stream-close-on-read-failure

## Instructions

# Crypto Stream Close on Read Failure

## Instructions

- WHEN the TG encounters a stream wrapper (e.g., CryptoInputStream) that wraps an underlying input stream and overrides the `read(byte[], int, int)` method
- THEN the TG should test that when the wrapped stream's `read(byte[], int, int)` returns a partial read (a value > 0 but less than `len`), AND an encryption/decryption error occurs during processing of that partial buffer, the wrapper correctly closes the underlying stream (or releases associated resources)
- Specifically: construct a stream scenario where `read()` on the underlying stream returns a partial fill (e.g., returns 10 when the buffer's `len` is 1000), then simulate a crypto failure (e.g., by providing invalid cipher parameters or a corrupted stream). Verify that the wrapper stream's `close()` is invoked on the underlying stream after the failure and that no resource leak occurs.
- To detect the bug: after the crypto failure, call `read()` again or check for stream state. The buggy version may NOT close the underlying stream on partial-read failure, leaving the stream open and leaking resources. The fixed version DOES close on such failure.
- Include at least one test where: (1) the underlying stream provides multiple chunks via `read()` that partially fill the buffer; (2) a crypto error occurs mid-read; (3) verify the stream is closed afterward (e.g., subsequent `read()` returns -1, or a flag confirms `close()` was called).
- Common pitfall: Testing only with a single `read()` call that fills the buffer completely. This misses the bug because the leak only manifests when `read()` returns a partial fill before the crypto error. Always test with partial reads.

**Correct test pattern (abstract):**
```java
// Arrange: create an underlying stream that returns partial reads
InputStream badSource = new InputStream() {
  boolean closed = false;
  boolean first = true;
  @Override public int read(byte[] b, int off, int len) {
    if (first) { first = false; return 5; } // partial read
    return -1;
  }
  @Override public void close() { closed = true; }
  @Override public int read() { throw new UnsupportedOperationException(); }
};
// Wrap with crypto stream that will fail during decryption
InputStream cryptoStream = new CryptoInputStream(badSource, ...invalidParams...);
// Act: attempt read, which should fail
assertThrows(IOException.class, () -> cryptoStream.read(new byte[100], 0, 100));
// Assert: underlying stream is closed
assertTrue(badSource.closed);
```

**Incorrect test pattern (missing the bug):**
```java
// Only tests full-buffer reads or successful reads — won't catch the bug
InputStream fullSource = new ByteArrayInputStream(new byte[1000]);
InputStream cryptoStream = new CryptoInputStream(fullSource, validParams);
byte[] buf = new byte[1000];
int n = cryptoStream.read(buf, 0, 1000); // full read, no failure
// This works fine on both buggy and fixed versions
```
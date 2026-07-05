---
name: blocking-io-stream-giant-write
description: When implementing a buffered output stream with block-sized writes, test
  that writing a giant byte array (larger than block size) does not cause infinite
  recursion or StackOverflowError. This skill applies to any OutputStream that splits
  large writes into block-sized chunks.
code_tags:
- ARGUMENT_VALIDATION
- BOUNDARY_CHECK
- STATE_MUTATION
test_pattern: EXCEPTION_TEST
---

# blocking-io-stream-giant-write

## Instructions

# Blocking IO Stream Giant Write

## Instructions

- WHEN the TG encounters an `OutputStream` implementation that splits a large write operation into smaller block-sized chunks (e.g., a `BlockedOutputStream` that has a `blockSize` field and a `write(byte[], int, int)` or `write(byte[])` method that invokes itself or a helper to write data in block-size increments)
- THEN the test must verify that writing a large buffer significantly larger than the block size (e.g., a buffer of size 100x the block size, or a "giant write" of e.g. 1024*1024 bytes with a 1K block) does NOT cause a `StackOverflowError`. The test should expect the write to complete normally (no exception thrown) or, if the stream is unbounded, to at least not crash with a recursive overflow.
- HOW: The test should:
  1. Create a `BlockedOutputStream` wrapping a simple `ByteArrayOutputStream` (or a mock `OutputStream`) with a known small `blockSize` (e.g., 1024 bytes).
  2. Call `write(byte[])` with a very large byte array (e.g., 1024*1024 bytes == 1MB, which is 1024 blocks for a 1K block size).
  3. Assert that the write completes without throwing a `StackOverflowError` (i.e., the method returns normally). Typically this means calling the write method and not expecting any exception.
  4. Optionally verify that the underlying stream received the correct total number of bytes.
- Common pitfalls:
  - Testing only writes that fit within a single block, which would never trigger the recursive splitting path.
  - Testing with mock objects that silently swallow recursive calls — use a real `ByteArrayOutputStream` or a verifying mock that expects exactly the right number of block-sized writes.
  - Assuming the method uses a loop when it actually uses recursion — always check the implementation. If the write method calls itself for partial writes, recursion depth grows with (totalSize / blockSize) and can overflow the stack.
  - Writing a test that expects a specific exception when the buggy version crashes — the correct test expects no exception at all.

### Example (Correct)

```java
@Test
public void testGiantWrite() throws Exception {
  int blockSize = 1024;
  int giantSize = 1024 * 1024; // 1 MB = 1024 blocks
  byte[] giantData = new byte[giantSize];
  new Random().nextBytes(giantData);

  ByteArrayOutputStream baos = new ByteArrayOutputStream(giantSize);
  BlockedOutputStream bos = new BlockedOutputStream(baos, blockSize);

  // This must NOT throw StackOverflowError
  bos.write(giantData);

  assertArrayEquals(giantData, baos.toByteArray());
}
```

### Example (Incorrect — would miss the bug)

```java
@Test
public void testSmallWrite() throws Exception {
  int blockSize = 1024;
  byte[] smallData = new byte[blockSize];
  // This only writes one block — never triggers recursive splitting
  bos.write(smallData);
  // Passes even on buggy version
}
```
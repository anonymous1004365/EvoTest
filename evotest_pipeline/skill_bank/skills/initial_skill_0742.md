---
name: bytebuffer-context-position-preservation
description: When constructing a Reader/wrapper from a ByteBuffer, the TG must test
  that the buffer's position and limit remain unchanged after construction. This skill
  helps detect bugs where the constructor modifies the ByteBuffer's state (e.g. flipping
  or resetting it), corrupting subsequent reads from the original buffer.
code_tags:
- BUFFER_OFFSET_HANDLING
- STATE_MUTATION
test_pattern: STATE_TEST
---

# bytebuffer-context-position-preservation

## Instructions

# ByteBuffer Context Position Preservation

## Instructions

- WHEN the TG encounters a constructor or factory method that accepts a `ByteBuffer` and stores or wraps it for later reading (e.g., `UnsynchronizedBuffer.Reader(ByteBuffer)`),
- THEN the TG MUST write a test that:
  1. Creates a `ByteBuffer` with known content (e.g., `ByteBuffer.wrap(new byte[] {3,4,5,6,7})`)
  2. Records the buffer's **position** and **limit** BEFORE calling the constructor
  3. Calls the constructor to create the wrapper/reader object
  4. Asserts that the **position** and **limit** of the original `ByteBuffer` are **unchanged** after construction
  5. Additionally, reads back content from the wrapper/reader and asserts the content is correct (e.g., `assertEquals(3, reader.readInt())`)
  6. **Also** reads back content from the original `ByteBuffer` directly and asserts that its content is also correct

- Common pitfalls:
  - Testing only that the wrapper can read data correctly, without also checking that the original `ByteBuffer` is unmodified — the bug is that the constructor corrupts the buffer's state (e.g. by calling `flip()`), so the buffer becomes unreadable
  - Using `flip()` or `clear()` on the passed-in buffer inside the constructor, which changes position/limit — always use explicit `get()`/`put()` methods and validate input separately
  - Not verifying both the wrapper/reader output AND the original buffer's ability to be read independently

### Correct example:

```java
ByteBuffer original = ByteBuffer.wrap(new byte[] {3,4,5,6,7});
int origPos = original.position();
int origLimit = original.limit();

UnsynchronizedBuffer.Reader reader = new UnsynchronizedBuffer.Reader(original);

// Reader should read its content
assertEquals(3, reader.readInt());

// Original buffer must be untouched
assertEquals(origPos, original.position());
assertEquals(origLimit, original.limit());
// Original buffer should still be readable
assertEquals(3, original.get());
```

### Incorrect example (buggy code this skill catches):

```java
// Buggy constructor that flips the buffer:
public Reader(ByteBuffer buffer) {
  this.buffer = buffer;
  buffer.flip();  // BUG: mutates original buffer's position/limit!
}
```
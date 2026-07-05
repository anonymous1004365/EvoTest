---
name: original-indexinput-close-propagation
description: When IndexInput wrappers (e.g., copy-on-write or buffered) are created
  around an original delegate IndexInput from openInput(), closing the wrapper must
  propagate the close to the original or mark it as unusable. Without this, the original
  IndexInput can be read after close, causing "cannot use IndexInput once closed"
  errors.
code_tags:
- RESOURCE_MANAGEMENT
- ORIGINAL_INDEX_INPUT_HANDLING
test_pattern: INTERACTION_TEST
---

# original-indexinput-close-propagation

## Instructions

# Original IndexInput Close Propagation

## Instructions

- WHEN the TG encounters a Directory implementation (like OakDirectory) that has an `openInput(String, IOContext)` method returning an IndexInput, and that returned IndexInput wraps or buffers data from an underlying/delegate/original IndexInput obtained from a blob store or NodeBuilder
- THEN the TG should write a test that:
  1. Creates the Directory and writes some data to a file using `createOutput`
  2. Opens the file with `openInput` to obtain an IndexInput (call it `input`)
  3. Closes `input` with `input.close()`
  4. Attempts to use the closed IndexInput (e.g., `input.readByte()`, `input.readBytes(...)`, or `input.length()`) and verifies that it throws `AlreadyClosedException` with message containing "cannot use IndexInput once closed"
- Common pitfalls:
  - Testing only that `close()` does not throw, without verifying the post-close state of the IndexInput
  - Testing only the high-level Directory operations (listAll, fileExists, etc.) without actually opening and closing an IndexInput
  - Not testing that the *original* underlying IndexInput (not just a wrapper) becomes unusable after close

### Correct example

```java
@Test
public void testCloseOnOriginalIndexInput() throws Exception {
    Directory dir = createDir(builder, false, "/foo");
    byte[] data = randomBytes(100);
    createFile(dir, "test.txt", data);
    
    // Open an IndexInput
    IndexInput input = dir.openInput("test.txt", IOContext.DEFAULT);
    
    // Close it
    input.close();
    
    // Verify the closed IndexInput cannot be used
    try {
        input.readByte();
        fail("Expected AlreadyClosedException");
    } catch (AlreadyClosedException e) {
        assertThat(e.getMessage(), containsString("cannot use IndexInput once closed"));
    }
}
```

### Incorrect example

```java
@Test
public void testCloseOnOriginalIndexInput() throws Exception {
    Directory dir = createDir(builder, false, "/foo");
    byte[] data = randomBytes(100);
    createFile(dir, "test.txt", data);
    
    // Open an IndexInput
    IndexInput input = dir.openInput("test.txt", IOContext.DEFAULT);
    
    // Close it - no post-close verification
    input.close();
    
    // This test passes even if the underlying/original IndexInput
    // remains usable after close, because nothing is checked.
}
```
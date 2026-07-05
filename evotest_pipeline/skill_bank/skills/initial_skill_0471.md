---
name: servlet-30-write-implementation-difference
description: When testing file upload write operations (e.g., writeToTempFile), the
  underlying write() mechanism differs between FileItem and Part implementations —
  FileItem.write(File) vs Part.write(String). A test must verify that writeToTempFile()
  actually triggers the write on the underlying implementation, not just that it doesn't
  throw. Apply this skill when a FileUpload-like class delegates write operations
  to an interface/abstract implementation that may have different contract semantics.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- NULL_CHECK
- RESOURCE_MANAGEMENT
- TEMP_FILE_CLEANUP
test_pattern: INTERACTION_TEST
---

# servlet-30-write-implementation-difference

## Instructions

# Testing Write Operations on Delegated File Upload Implementations

## Instructions

WHEN the TG encounters a method like `writeToTempFile()` that delegates to an underlying implementation's write method (e.g., `FileItem.write(File)` or `Part.write(String)`), THEN the TG should write an interaction-style test that:

1. Creates a mock/stub implementation of the underlying interface (e.g., a custom `Part` implementation) that tracks whether the write method was actually called (e.g., using an `AtomicReference<String>` or similar side-effect tracker).

2. Constructs the wrapper class (e.g., `FileUpload`) using this stub implementation.

3. Calls the method under test (e.g., `writeToTempFile()`) and verifies that:
   - The underlying write method was indeed invoked (i.e., the side-effect tracker confirms the write happened).
   - The wrapper does not silently swallow the write call or delegate to a different code path.

4. Additionally, verify that cleanup operations (e.g., `delete()`) also work correctly by checking side-effect trackers on the underlying implementation.

**Common pitfalls to avoid:**
- Testing only that `writeToTempFile()` does NOT throw an exception — the bug was that the write to the underlying Part was never actually triggered.
- Assuming all write implementations have the same semantics — `FileItem.write(File)` passes a `File` object while `Part.write(String)` passes a `String` filename, so the wrapper must handle this correctly.
- Neglecting to verify the side effects on the underlying object using separate trackers for write versus delete operations.

**Example (correct):**
```java
// Custom Part stub tracking write calls
private static class Servlet3Part implements Part {
    private final AtomicReference<String> written = new AtomicReference<>();
    private final AtomicBoolean deleted = new AtomicBoolean(false);

    @Override
    public void write(String fileName) throws IOException {
        written.set(fileName);  // Track that write was called
    }

    @Override
    public void delete() throws IOException {
        deleted.set(true);  // Track that delete was called
    }
    // ... other methods ...
}

// Test
FileUpload fileUpload = new FileUpload(part);
assertThat(part.written.get(), is(nullValue()));  // Not called yet
fileUpload.writeToTempFile();
assertThat(part.written.get(), is(notNullValue())); // Must be called!

assertThat(part.deleted.get(), is(false));
fileUpload.delete();
assertThat(part.deleted.get(), is(true));
```

**Example (incorrect — misses the bug):**
```java
// Only testing that no exception is thrown
FileUpload fileUpload = new FileUpload(somePart);
fileUpload.writeToTempFile();  // This would pass even if Part.write() is never called!
fileUpload.delete();
// No assertions on side effects!
```
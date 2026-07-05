---
name: file-parent-directory-null-check
description: Teach the TG to test that File.getParentFile() result is checked for
  null before calling methods on it. File.getParentFile() returns null for files without
  a parent (e.g., a plain filename with no directory), causing NullPointerException
  when calling mkdirs(), exists(), or other methods on the result.
code_tags:
- NULL_CHECK
- NULL_CHECK_PARENT_FILE
test_pattern: EXCEPTION_TEST
---

# file-parent-directory-null-check

## Instructions

# File Parent Directory Null Check

## Instructions

- WHEN the code calls `File.getParentFile()` on a `File` object (e.g., `fileStore.getParentFile()`), THEN the TG must verify that the code handles the case where `getParentFile()` returns `null`.
- WHEN `getParentFile()` could return `null` (e.g., the file is a simple name like `"file.data"` with no parent directory), THEN the TG must write a test that uses a `File` object with no parent directory and verify no `NullPointerException` occurs.
- Specifically, test with a `File` object constructed with a simple filename (e.g., `new File("file.data")`) — this file has no parent, so `getParentFile()` returns `null`. Verify the code does NOT call `.mkdirs()`, `.exists()`, or any other method on the null parent reference.
- WHEN testing `FileIdempotentRepository` or similar classes that create/store files, THEN the TG must test with a file path that has no parent directory (a bare filename or a root path like `/`), and verify that operations complete without throwing `NullPointerException`.
- Common pitfall: Only testing with file paths that have parent directories (e.g., `new File("target/file.data")`), which does NOT trigger the bug because `getParentFile()` returns a non-null value.
- Correct: Use `new File("simpleFilename.data")` — `getParentFile()` returns `null`, and calling `.mkdirs()` on that null would throw `NullPointerException`.
- The test should verify the operation succeeds (no exception is thrown) and the file/repo is in the expected state.

### Example (Correct)
```java
@Test
public void shouldHandleFileWithNoParent() {
    // A File with no parent directory - getParentFile() returns null
    FileStore store = new FileStore("testfile.data");
    FileIdempotentRepository repo = FileIdempotentRepository.fileIdempotentRepository(store);
    // Should not throw NullPointerException
    repo.start();
    assertTrue("File should be created", store.exists());
}
```

### Example (Incorrect — does not trigger the bug)
```java
@Test
public void testWithParentDirectory() {
    // This has a parent directory, so getParentFile() returns non-null
    FileStore store = new FileStore("target/testfile.data");
    FileIdempotentRepository repo = FileIdempotentRepository.fileIdempotentRepository(store);
    repo.start();  // Always works because parent is not null
    // This test would pass even on the buggy version
}
```
---
name: corrupted-file-cleanup-on-failure
description: When a file copy operation fails with an exception, the test must verify
  that partially-copied or corrupted local files are deleted. This skill applies to
  IndexCopier's file caching where a corrupt local file should not remain after a
  copy failure.
code_tags:
- CORRUPTED_FILE_CLEANUP
- EXCEPTION_HANDLING
- RESOURCE_MANAGEMENT
test_pattern: STATE_TEST
---

# corrupted-file-cleanup-on-failure

## Instructions

# Corrupted File Cleanup on Copy Failure

## Instructions

- WHEN the TG encounters a class that copies files from a remote/source directory to a local/cache directory (e.g., `IndexCopier.copy()` in `IndexCopier.java` which copies index files from a remote `Directory` to a local `Directory`)
- THEN the TG should write a test that:
  1. Creates a remote directory that **throws an exception** during file reading/copying (e.g., override `openInput` on a `RAMDirectory` subclass to throw `IllegalStateException("boom")`)
  2. Wraps the remote directory using the copier (e.g., `c1.wrap("/foo", defn, remote)`)
  3. Writes a file to the remote directory (e.g., `writeFile(remote, "failed.txt")`)
  4. Attempts to read the file through the wrapped directory, expecting the exception to propagate (use `try-catch` or `expected = IllegalStateException.class`)
  5. After the exception, asserts that the **local/cache directory does NOT contain the file** — the partially-copied or corrupted file must have been cleaned up (e.g., `assertFalse(c1.baseDir.fileExists("failed.txt"))`)

- Common pitfalls:
  - Testing only the happy path where all files copy successfully, ignoring failure scenarios
  - Forgetting to verify the **absence** of the corrupted file in the local directory after failure — verifying only that the exception was thrown is insufficient
  - Using a remote directory that doesn't actually throw during copy — the test must force a failure during the copy operation itself (e.g., throwing from `openInput`, which is called by `remote.copy()`)
  - Not using `sameThreadExecutor()` to ensure synchronous execution of the copy task

- Example correct test pattern:
  ```java
  // Create remote that throws on copy
  Directory remote = new RAMDirectory(){
      @Override
      public IndexInput openInput(String name, IOContext context) throws IOException {
          throw new IllegalStateException("boom");
      }
  };
  
  Directory baseDir = new RAMDirectory();
  IndexCopier copier = new RAMIndexCopier(baseDir, sameThreadExecutor(), getWorkDir());
  Directory wrapped = copier.wrap("/foo", defn, remote);
  
  String fileName = "failed.txt";
  writeFile(remote, fileName);
  
  try {
      readAndAssert(wrapped, fileName, someBytes);
      fail("Read of file should have failed");
  } catch (IllegalStateException ignore) { }
  
  assertFalse(copier.baseDir.fileExists(fileName));
  ```

- Incorrect pattern (missing cleanup verification):
  ```java
  // BAD: Only checks that exception was thrown, not that file was cleaned up
  try {
      readAndAssert(wrapped, "failed.txt", data);
  } catch (Exception e) {
      // Test passes but corrupted file remains!
  }
  ```
---
name: marker-file-exclusive-read-lock-concurrency
description: When testing file-based exclusive read lock strategies that use marker
  files, write multi-threaded tests to verify that marker lock files are properly
  created during acquisition and cleaned up after release, even under concurrent file
  processing. This ensures no orphan marker files are left behind.
code_tags:
- CONCURRENCY
- RESOURCE_MANAGEMENT
test_pattern: INTERACTION_TEST
---

# marker-file-exclusive-read-lock-concurrency

## Instructions

# Marker File Exclusive Read Lock Concurrency Testing

## Instructions

- WHEN the TG encounters a class that implements `GenericFileExclusiveReadLockStrategy<File>` (e.g., `MarkerFileExclusiveReadLockStrategy`) and uses marker files (e.g., files with `.camelLock` suffix) to acquire/release read locks on files
- THEN it should write a multi-threaded integration test that:
  1. Creates a Camel route using the `file:` component with `readLock=markerFile` (or `readLock=markerFileExclusive`) and uses `threads(N)` to process files concurrently (where N > 1).
  2. Writes multiple data files (e.g., 2-5 files) to the input directory before the route starts.
  3. Verifies that after all files are processed:
     - Each output file contains the expected content (e.g., all lines in order).
     - The marker lock files (e.g., `*.camelLock`) are deleted from the input directory.
     - The input files themselves are deleted/moved as expected.
     - The exact count of files processed equals the number of input files.
  4. Uses a mock endpoint (`mock:result`) to verify the expected message count.
  5. Uses an `AtomicInteger` counter to track the number of files fully processed, and waits until all files are done before asserting final state.

- WHEN the TG tests a `releaseExclusiveReadLockOnCommit` that deletes the marker lock file
- THEN it should assert that `FileUtil.deleteFile(lock)` is called on the lock file, and verify that the lock file no longer exists after processing completes. Common pitfalls:
  - Testing only single-threaded scenarios, which may not expose race conditions where multiple threads try to acquire/release locks on different files simultaneously.
  - Forgetting to assert that marker lock files (`.camelLock`) are cleaned up — the test should assert `assertFileDoesNotExists` for each lock file.
  - Using `Thread.sleep()` with insufficient delays — prefer `await().untilAsserted()` or a polling loop with `AtomicInteger` to wait for completion.

### Correct Example (Multi-threaded with marker file cleanup verification):

```java
public void testMultithreadedLocking() throws Exception {
    MockEndpoint mock = getMockEndpoint("mock:result");
    mock.expectedMessageCount(2);
    mock.expectedFileExists("target/marker/out/file1.dat");
    mock.expectedFileExists("target/marker/out/file2.dat");

    writeFiles();  // writes file1.dat and file2.dat to target/marker/in

    assertMockEndpointsSatisfied();

    // Verify content integrity in output files
    String content = context.getTypeConverter().convertTo(String.class, new File("target/marker/out/file1.dat"));
    String[] lines = content.split(LS);
    for (int i = 0; i < 20; i++) {
        assertEquals("Line " + i, lines[i]);
    }

    // Verify marker lock files are deleted
    assertFileDoesNotExists("target/marker/in/file1.dat.camelLock");
    assertFileDoesNotExists("target/marker/in/file2.dat.camelLock");

    // Verify source files are gone
    assertFileDoesNotExists("target/marker/in/file1.dat");
    assertFileDoesNotExists("target/marker/in/file2.dat");
}
```

### Incorrect Example (Single-threaded, no marker file assertion):

```java
// WRONG: Only tests single consumer, does not verify lock cleanup
public void testSingleThreadedLocking() throws Exception {
    MockEndpoint mock = getMockEndpoint("mock:result");
    mock.expectedMessageCount(1);
    template.sendBodyAndHeader("file:target/in", "Hello World", Exchange.FILE_NAME, "test.txt");
    assertMockEndpointsSatisfied();
    // Missing: assert no orphan .camelLock files remain
    // Missing: multi-threaded concurrency scenario
}
```
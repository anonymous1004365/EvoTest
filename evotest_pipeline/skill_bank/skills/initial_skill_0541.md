---
name: done-file-deletion-on-rollback
description: When testing file consumer routes with doneFileName and moveFailed options,
  verify that the done file is properly deleted on rollback/failure, and the original
  file is moved to the failed folder. This skill prevents bugs where done files silently
  persist after failed processing.
code_tags:
- RESOURCE_MANAGEMENT
- STATE_MUTATION
test_pattern: STATE_TEST
---

# done-file-deletion-on-rollback

## Instructions

# Done File Deletion on Rollback in File Consumers

## Instructions

- WHEN the TG encounters a file consumer route that uses both `doneFileName` (e.g., `doneFileName=done`) and `moveFailed` (e.g., `moveFailed=failed`) — i.e., a route that processes files based on done-file markers AND moves files to a "failed" directory on processing failure
- THEN the TG MUST write a test that:
  1. Sends both a data file (e.g., `hello.txt` with content `"Hello World"`) AND a done file (e.g., `done` with empty content) to the input directory
  2. Configures the route to throw an exception (e.g., `throwException(new IllegalArgumentException("Forced"))`) after processing, to simulate a failure
  3. After asserting the mock endpoint received the message, waits for the exchange to complete (e.g., `oneExchangeDone.matchesMockWaitTime()`)
  4. Asserts that the done file has been DELETED — i.e., `assertFalse("Done file should be deleted", new File("target/done/done").exists())`
  5. Asserts that the original file has been MOVED to the failed folder — i.e., `assertTrue("Original file should be moved", new File("target/done/failed/hello.txt").exists())`
- The test must verify BOTH conditions: (a) done file is cleaned up after failure, and (b) the original file is relocated to the `moveFailed` target directory.
- Common pitfalls to avoid:
  - Testing only the `moveFailed` behavior without checking the done file cleanup
  - Assuming the done file is always deleted — on rollback the done file should only be deleted if `moveFailed` is configured (otherwise it should remain to allow retry)
  - Not cleaning up test directories in `setUp()` (e.g., `deleteDirectory("target/done")`) which can cause stale state from previous test runs
  - Not using `oneExchangeDone.matchesMockWaitTime()` before checking file existence, as the file operations are asynchronous
  - Forgetting that the done file deletion in `processStrategyRollback()` is guarded by `if (endpoint.getMoveFailed() != null)` — without `moveFailed`, the done file should NOT be deleted during rollback so the file can be retried

### Correct Example

```java
public void testDoneFile() throws Exception {
    getMockEndpoint("mock:input").expectedMessageCount(1);

    template.sendBodyAndHeader("file:target/done", "Hello World", Exchange.FILE_NAME, "hello.txt");
    template.sendBodyAndHeader("file:target/done", "", Exchange.FILE_NAME, "done");

    assertMockEndpointsSatisfied();
    oneExchangeDone.matchesMockWaitTime();

    // done file should be deleted now
    File file = new File("target/done/done");
    assertFalse("Done file should be deleted: " + file, file.exists());

    // as well the original file should be moved to failed
    file = new File("target/done/failed/hello.txt");
    assertTrue("Original file should be moved: " + file, file.exists());
}
```

### Incorrect Example (Missing done file check)

```java
public void testDoneFile() throws Exception {
    getMockEndpoint("mock:input").expectedMessageCount(1);

    template.sendBodyAndHeader("file:target/done", "Hello World", Exchange.FILE_NAME, "hello.txt");
    template.sendBodyAndHeader("file:target/done", "", Exchange.FILE_NAME, "done");

    assertMockEndpointsSatisfied();

    // BUG: Missing oneExchangeDone.matchesMockWaitTime() — file operations may not have completed
    // BUG: Only checking moveFailed, not done file deletion
    File file = new File("target/done/failed/hello.txt");
    assertTrue("Original file should be moved: " + file, file.exists());
}
```
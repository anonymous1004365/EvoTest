---
name: file-append-verification-with-consumer-poll
description: When testing file producers with the fileExist=Append option, the TG
  should verify that the appended content can be consumed and read back correctly
  via a file consumer endpoint, not just that the file exists on disk. This catches
  bugs where the append operation corrupts or overwrites content.
code_tags:
- NULL_CHECK
- VALIDATION
- STATE_MUTATION
- RESOURCE_MANAGEMENT
test_pattern: STATE_TEST
---

# file-append-verification-with-consumer-poll

## Instructions

# File Append Verification With Consumer Poll

## Instructions

- WHEN the TG encounters a `GenericFileProducer` or file endpoint URI using `fileExist=Append` (e.g., `file://target/file?fileExist=Append`)
- THEN the TG should write a test that:
  1. Writes initial content to a file (e.g., `"Hello World\n"`)
  2. Appends additional content to the same file using the `fileExist=Append` option (e.g., `"Bye World"`)
  3. Uses a file consumer endpoint (e.g., `from("file://target/file?noop=true&initialDelay=0&delay=10")`) to read back the file content
  4. Verifies the consumed message body contains both original and appended content (e.g., `"Hello World\nBye World"`)
  5. Also verifies via `expectedFileExists` that the file on disk has the expected combined content
- The test should fail on the buggy version because `fileExist=Append` may produce a file with only the appended content (overwriting the original instead of appending), causing the consumer to read only the new content
- Common pitfalls to avoid:
  - **Testing only file existence**: Merely checking that the file exists after the append does not verify the content is correct
  - **Only checking disk content**: The bug may manifest in what the consumer reads (e.g., truncated body `"Bye World"` instead of `"Hello World\nBye World"`) even if the file on disk appears correct
  - **Missing consumer route**: Without a file consumer route that polls and converts the body, the TG may not detect that the file's content was corrupted/overwritten during the append
  - **Forgetting to include the initial content body**: The test must set up initial content before appending, otherwise append has nothing to test against

- **Correct example** (what the TG should write):
```java
public void testAppend() throws Exception {
    template.sendBodyAndHeader("file://target/file", "Hello World\n", Exchange.FILE_NAME, "hello.txt");

    MockEndpoint mock = getMockEndpoint("mock:result");
    mock.expectedBodiesReceived("Hello World\nBye World");
    mock.expectedFileExists("target/file/hello.txt", "Hello World\nBye World");

    template.sendBodyAndHeader("file://target/file?fileExist=Append", "Bye World", Exchange.FILE_NAME, "hello.txt");

    context.startAllRoutes();

    assertMockEndpointsSatisfied();
}
```

- **Incorrect example** (what the TG should NOT write):
```java
public void testAppend() throws Exception {
    template.sendBodyAndHeader("file://target/file", "Hello World\n", Exchange.FILE_NAME, "hello.txt");
    template.sendBodyAndHeader("file://target/file?fileExist=Append", "Bye World", Exchange.FILE_NAME, "hello.txt");
    
    // Only checks disk file exists, does NOT verify content via consumer
    assertTrue(new File("target/file/hello.txt").exists());
}
```
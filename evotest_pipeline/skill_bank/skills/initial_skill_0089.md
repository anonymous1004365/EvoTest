---
name: file-move-done-custom-header-handling
description: When configuring file consumer routes with custom move/done file name
  headers expressed as absolute paths, tests must verify that the done file is actually
  moved (or renamed) to the correct absolute path directory — not just set as a header
  value. The TG should test with both relative path base directories and custom header-driven
  absolute paths to ensure the file system operation matches the configuration.
code_tags:
- VALIDATION
- STATE_MUTATION
- ABSOLUTE_PATH_FILE_MOVE
test_pattern: INTERACTION_TEST
---

# file-move-done-custom-header-handling

## Instructions

# File Move Done Custom Header Handling

## Instructions

- WHEN the TG encounters a file consumer endpoint (e.g., `from("file:...")`) that uses a custom `doneFileName` or `move` configuration via a header (e.g., `CamelFileDoneFileName`), especially when the header value specifies an **absolute path** target for the done/move file:
  - THEN the TG should write a test that creates a source file, triggers file consumption, and **verifies on the filesystem** that the done/move file actually exists at the expected absolute path (not just that the header was set).
  - The test must use `java.io.File` existence assertions (e.g., `assertTrue(new File(expectedDonePath).exists())`) targeting the final filesystem state, not just mock endpoint message assertions.
  - When testing with an absolute path for `CamelFileDoneFileName`, the test should specify a path like `target/inbox/dones/myabsolute.txt` (relative to the working directory) and verify that the file was physically written there.
  - Include a negative test: set `doneFileName` to a relatively-specified path without a corresponding parent directory ensuring the directory exists, and verify the done file still gets created.

- Common pitfalls to avoid:
  - Testing only that the message header `CamelFileDoneFileName` is present/not-null without verifying the actual filesystem operation.
  - Assuming that done file behavior is identical across both relative and absolute paths — the bug specifically manifests with absolute paths that get correctly set as headers but are not properly processed by the file move/rename logic.
  - Using mock endpoints exclusively (e.g., `mock:result`) when the real assertion requires checking the filesystem for the done file's existence.
  - Not cleaning up the done file parent directory in `@Before` or setup methods, which can cause false positives from leftovers of previous test runs.

- Example correct test (interaction-based):
```java
// Setup: create source file
template.sendBodyAndHeader("file://target/inbox", "Hello World", Exchange.FILE_NAME, "test.txt");

// Configure consumer with absolute done file path
from("file://target/inbox?doneFileName=${file:parent}/dones/myabsolute.txt&initialDelay=0&delay=10")
    .to("mock:result");

// Verify the done file was physically created
Thread.sleep(500); // wait for consumer to process
assertTrue("The done file should exist at the absolute path",
    new File("target/inbox/dones/myabsolute.txt").exists());
```

- Example incorrect test (that would miss the bug):
```java
// ❌ BAD: Only checks header, does not verify filesystem
from("file://target/inbox?doneFileName=${file:parent}/dones/myabsolute.txt&initialDelay=0&delay=10")
    .to("mock:result");

mockResult.assertIsSatisfied();
// No filesystem check for the done file!
```
---
name: file-consumed-filename-mutation-test
description: WHEN testing file component message headers for consumed files, THEN
  verify that mutating fileName on a GenericFile does not corrupt the FILE_NAME_CONSUMED
  header. This skill catches bugs where the fileName is modified after a file is consumed
  but the fileNameConsumed reference is not protected via defensive copying.
code_tags:
- NULL_CHECK
- VALIDATION
- STATE_MUTATION
test_pattern: STATE_TEST
---

# file-consumed-filename-mutation-test

## Instructions

# File Consumed Filename Mutation Test

## Instructions

- WHEN the TG encounters a test that verifies the `Exchange.FILE_NAME_CONSUMED` header (e.g., `header(Exchange.FILE_NAME_CONSUMED).isEqualTo(...)`) in file consumer workflows
- THEN it should verify that mutating the `GenericFile.fileName` field **after** the file has been consumed does **not** retroactively alter the `FILE_NAME_CONSUMED` header value.
- The bug pattern occurs in `GenericFile.populateHeaders(GenericFileMessage, boolean)` where `fileNameConsumed` is stored as a **reference** to the same `String` object as `fileName`, so calling `changeFileName(...)` after headers are populated corrupts the `FILE_NAME_CONSUMED` header.
- To catch this, the TG should write a test that:
    1. Consumes a file (e.g., via a route with `from("file:...")`)
    2. Stores the `FILE_NAME_CONSUMED` header value
    3. Modifies the `fileName` property of the GenericFile object (e.g., via `GenericFileRenameExclusiveReadLockStrategy` or `GenericFileExpressionRenamer`)
    4. Asserts that the stored `FILE_NAME_CONSUMED` header still contains the **original** filename, not the renamed one
- Common pitfall: Testing only that the `FILE_NAME_CONSUMED` header is set at all, without checking that it is **immutable** after subsequent file renames.
- Another pitfall: Using a direct mock of `GenericFile` without exercising the actual `populateHeaders` codepath that triggers the bug.

**Correct approach (catches the bug):**
```java
MockEndpoint mock = getMockEndpoint("mock:result");
mock.expectedMessageCount(1);
mock.message(0).header(Exchange.FILE_NAME_CONSUMED).isEqualTo("hello.txt");
// The route renames the file after consumption — this should NOT change FILE_NAME_CONSUMED
assertMockEndpointsSatisfied();
```

**Incorrect approach (misses the bug):**
```java
MockEndpoint mock = getMockEndpoint("mock:result");
mock.expectedMessageCount(1);
// Missing assertion on FILE_NAME_CONSUMED being the original filename
// Just checking that headers exist is not enough
mock.message(0).header(Exchange.FILE_NAME_CONSUMED).isNotNull();
assertMockEndpointsSatisfied();
```
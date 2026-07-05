---
name: file-consumer-idempotent-on-completion-cleanup
description: When using an idempotent repository with file consumers, the TG should
  test that in-progress entries are properly cleaned up even when the Exchange is
  completed without a full file processing lifecycle. This ensures no stale in-progress
  entries remain.
code_tags:
- NULL_CHECK
- STATE_MUTATION
- ARGUMENT_VALIDATION
- RESOURCE_MANAGEMENT
test_pattern: STATE_TEST
---

# file-consumer-idempotent-on-completion-cleanup

## Instructions

# File Consumer Idempotent Repository Cleanup on Completion

## Instructions

- WHEN the TG sees a file consumer configured with `idempotent=true` and a `FileIdempotentRepository` (or any `IdempotentRepository`) being used as an in-progress repository via `setInProgressRepository()`
- THEN the TG should write a STATE_TEST that verifies the in-progress entry is properly removed when the file exchange completes — specifically through `GenericFileOnCompletion.onCompletion()` and `GenericFileProcessStrategySupport.commitCommitStrategy()` paths
  - The test must verify that after a file exchange completes (either commit or rollback), the `FileIdempotentRepository`'s `contains()` method returns `false` for the file's in-progress entry key
  - The test should set up the file consumer endpoint with an `idempotentRepository` (e.g., `FileIdempotentRepository.fileIdempotentRepository(...)`) and an `inProgressRepository` (same instance), then send a file and assert that post-consumption the in-progress repository does NOT contain the file's absolute path
- Common pitfalls:
  - Testing only that the idempotent repository drops the file from its main store (after duplicate detection) rather than also checking the in-progress repository cleanup
  - Forgetting that `GenericFileOnCompletion` calls `commitCommitStrategy()` which in turn calls `releaseExclusiveReadLockOnCommit()` on the strategy, and that path must clean up in-progress entries
  - Assuming the in-progress repository and the main idempotent repository are the same instance when testing cleanup — they may be separate; test each individually

### Correct Example
```java
// Given a FileIdempotentRepository used as both the idempotent and in-progress repo
FileIdempotentRepository repo = FileIdempotentRepository.fileIdempotentRepository(new File("target/data/idempotent.dat"), 200, 500000);
context.getRegistry().bind("myRepo", repo);

// When a file is consumed
template.sendBodyAndHeader("file://target/data/inbox", "Hello World", Exchange.FILE_NAME, "hello.txt");

// Then the in-progress entry should be cleaned up
Thread.sleep(2000); // wait for async consumer
assertFalse("In-progress entry should be removed after file consumption", 
    repo.contains(new File("target/data/inbox/hello.txt").getAbsolutePath()));
```

### Incorrect Example (common pitfall)
```java
// This test only checks the main idempotent store, not the in-progress cleanup
FileIdempotentRepository repo = FileIdempotentRepository.fileIdempotentRepository(new File("target/data/idempotent.dat"), 200, 500000);
template.sendBodyAndHeader("file://target/data/inbox?idempotent=true&idempotentRepository=#myRepo", "Hello World", Exchange.FILE_NAME, "hello.txt");
// Only checking main store — missing the separate inProgressRepository cleanup path
assertTrue("File should be in idempotent store", repo.contains(...));
// Missing: assertFalse(inProgressRepo.contains(...))
```
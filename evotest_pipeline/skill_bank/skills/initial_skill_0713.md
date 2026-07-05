---
name: done-file-noop-deletion
description: When the file consumer has noop=true and a doneFileName is configured,
  the done file must NOT be deleted after processing. Test that the done file survives
  the exchange lifecycle when noop mode is set.
code_tags:
- STATE_MUTATION
- NULL_CHECK
test_pattern: STATE_TEST
---

# done-file-noop-deletion

## Instructions

# Done File Should Not Be Deleted in Noop Mode

## Instructions

- WHEN the TG encounters code where a file consumer endpoint has both `noop=true` and a `doneFileName` option configured (e.g., `from("file:inbox?noop=true&doneFileName=done")`)
- THEN the TG should write a test that:
  1. Creates a source file and a done file in the input directory
  2. Routes the file through a consumer with `noop=true&doneFileName=done`
  3. After the exchange completes, asserts that the done file STILL EXISTS on the filesystem using `assertTrue("Done file should not be deleted", new File(doneFilePath).exists())`
  4. The test must use a `MockEndpoint` or similar to wait for the exchange to be processed
- The expected behavior on the buggy version: the done file is incorrectly deleted after processing
- Common pitfalls:
  - Testing only that the source file is not deleted (noop behavior) without also checking the done file
  - Using `delete=true` instead of `noop=true` which would make done file deletion expected
  - Not waiting for the exchange to fully complete before checking the done file existence
  - Testing file existence using `.isFile()` which returns false for directories — use `.exists()` instead

### Example (correct):
```java
// In your test route setup:
// from("file:target/doneFileTest?noop=true&doneFileName=done")
//     .to("mock:result");

// During assertions:
// assertTrue("Done file should not be deleted", new File("target/doneFileTest/done").exists());
```

### Example (incorrect — would miss the bug):
```java
// Only checking source file:
// assertTrue("Source file should exist", new File("target/doneFileTest/source.txt").exists());
// Missing: checking the done file
```
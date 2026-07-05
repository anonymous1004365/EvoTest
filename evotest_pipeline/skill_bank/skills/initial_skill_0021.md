---
name: file-move-failed-path-construction
description: WHEN configuring file component move/moveFailed with relative paths,
  THEN verify the constructed target path correctly resolves relative to the original
  file's parent directory, not the work directory. This skill prevents path duplication
  bugs where moved file paths contain repeated directory segments.
code_tags:
- PATH_PARSING_VALIDATION
- STATE_MUTATION
- RESOURCE_MANAGEMENT
test_pattern: STATE_TEST
---

# file-move-failed-path-construction

## Instructions

# Path Duplication in File Move/MoveFailed

## Instructions

WHEN the TG encounters code that constructs a target path for file move operations (e.g., `.move()`, `.moveFailed()`, or similar file relocation logic), specifically when:

1. A **relative path** is used as the move target (e.g., `target/input.bak/${date:now:yyyyMMddHHmmss}/hello.txt`)
2. The source file is **not at the root** of the input directory (e.g., in a subdirectory like `target/input/`)
3. The move target is meant to be relative to the **original file's parent directory** (not the work directory or consumer root)

THEN the TG should:

- **Verify the final moved file path** is constructed correctly by testing with files in subdirectories (not just files at the root of the watched directory)
- **Test with both successful move (`.move()`) and failed move (`.moveFailed()`)** scenarios to ensure both path construction logic is correct
- **Check that relative paths in `.move()` / `.moveFailed()` do NOT cause path duplication** — e.g., a file `target/input/hello.txt` with move pattern `target/input.bak/...` should move to `target/input.bak/.../hello.txt`, NOT `target/input/target/input.bak/.../hello.txt`
- **Assert the final file exists** at the expected destination path after the route completes
- **Use the `file:exists` or check file existence** in the expected target directory to validate the outcome

### Common Pitfalls

- ❌ Testing only move (success) without also testing moveFailed
- ❌ Only testing files at the root of the watched directory — this hides the path duplication bug because relative resolution works differently for root-level files
- ❌ Assuming the move/moveFailed target is relative to the consumer endpoint root rather than relative to the source file's parent directory
- ❌ Not checking intermediate path segments for unintended path nesting

### Example: Correct Test Pattern

```java
// Test file in subdirectory with relative moveFailed path
RouteBuilder builder = new RouteBuilder() {
    public void configure() {
        from(fileUri("?moveFailed=target/input.bak/${date:now:yyyyMMddHHmmss}/hello.txt&initialDelay=0&delay=10"))
            .throwException(new IllegalArgumentException("Forced failure"));
    }
};

// First verify the source file exists in a subdirectory
template.sendBodyAndHeader(fileUri(), "Hello World", Exchange.FILE_NAME, "target/input/hello.txt");

// Then assert the failed file appears at the expected path
// Expected: target/input.bak/<timestamp>/hello.txt
// NOT: target/input/target/input.bak/<timestamp>/hello.txt
assertTrue("The file should exist at the correctly constructed path", 
    destFile.expectsFileAt("target/input.bak/<timestamp>/hello.txt"));
```

### Example: Incorrect Test Pattern

```java
// ❌ Only tests root-level files — won't catch path duplication bug
from(fileUri("?moveFailed=backup/${date:now:yyyyMMddHHmmss}/hello.txt"))
    .throwException(new IllegalArgumentException("Forced failure"));

template.sendBodyAndHeader(fileUri(), "Hello World", Exchange.FILE_NAME, "hello.txt");
// This works fine even with the bug, since root-level files don't trigger the duplication
```
---
name: file-move-absolute-path-testing
description: WHEN testing file move/rename operations with explicit absolute paths
  in Camel file component, THEN verify the moved file lands at the correct absolute
  path and not a concatenation of the original directory and the move directory. This
  skill applies to `GenericFileEndpoint` move expressions like `file:move=file:///absolute/path`.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- BOUNDARY_CHECK
- STATE_MUTATION
test_pattern: PARAMETRIC_TEST
---

# file-move-absolute-path-testing

## Instructions

# File Move Absolute Path Testing

## Instructions

WHEN the TG encounters a test for the Camel file component's `GenericFileEndpoint` (or `FileEndpoint`) where the `move` expression is set to an **absolute file path** (e.g., `file:///absolute/path`), THEN the TG must write a test that:

1. Creates a source directory with a file in it.
2. Configures the endpoint with `move=file:///absolute/path` (the move target).
3. Sends the file through the route (process it), triggering the move.
4. Asserts that the file ends up at the **absolute path** specified in the `move` expression, and NOT at a concatenation of the original file's parent directory and the move directory.

**Concrete Example from the actual bug:**

Given:
- Source directory: `file:///tmp/testfile`
- Move expression: `file:///tmp/testfile2` (absolute path)
- File created in source: `file:///tmp/testfile/hello.txt`

The buggy behavior was that after processing, the file was moved to `file:///tmp/testfile/file:///tmp/testfile2/hello.txt` instead of the correct `file:///tmp/testfile2/hello.txt`.

**What the TG should test:**
```java
// Correct approach: Test move to an absolute path
@Test
public void testMoveAbsolute() throws Exception {
    File srcDir = new File("target/absolutedir");
    File dstDir = new File("target/absolutedir2");
    srcDir.mkdirs();
    dstDir.mkdirs();

    // Create a file in the source directory
    File srcFile = new File(srcDir, "hello.txt");
    assertTrue(srcFile.createNewFile());

    // Use move with an absolute path (file:///... or just absolute path)
    String sourceUri = "file:///" + srcDir.getAbsolutePath().replace('\\', '/')
        + "?move=file:///" + dstDir.getAbsolutePath().replace('\\', '/');

    // Run the route and consume the file
    template.sendBodyAndHeader(sourceUri, "Hello World", Exchange.FILE_NAME, "hello.txt");

    // Wait for the move
    Thread.sleep(2000);
    
    // Assert file exists in the destination absolute directory
    File movedFile = new File(dstDir, "hello.txt");
    assertTrue("File should have been moved to the destination absolute path", movedFile.exists());
    
    // Critical bug check: file should NOT be in a path like srcDir + "/" + dstDir 
    File wrongPath = new File(srcDir, dstDir.getAbsolutePath() + "/hello.txt");
    assertFalse("File should NOT be at a path concatenating source and destination", wrongPath.exists());
}
```

**Common pitfalls to avoid:**

- ❌ Testing only relative move paths (e.g., `move=.done`) — this does not trigger the absolute path bug.
- ❌ Assuming that an absolute path in the `move` expression is always handled correctly by the file component's normalization logic.
- ❌ Not checking that the file actually ends up at the correct absolute location (just checking the file was processed/moved somewhere is insufficient).
- ❌ On Windows, forgetting to use forward-slash paths or `file:///` prefix to properly express the absolute path in the URI.
- ❌ Forgetting to create the destination directory before running the test — the move may silently fail if the target directory doesn't exist.

**Incorrect test approach (would not detect the bug):**
```java
// BAD: Only tests move to a relative path
@Test
public void testMoveRelative() throws Exception {
    File srcDir = new File("target/srcdir");
    template.sendBodyAndHeader("file:///" + srcDir.getAbsolutePath().replace('\\', '/') 
        + "?move=.done", "Hello World", Exchange.FILE_NAME, "hello.txt");
    // This would pass even on the buggy version because relative moves work fine
}
```

**When writing this test, the TG should ensure:**
- The `move` expression is an absolute path (starts with `file:///` or is a full filesystem path).
- The destination directory is explicitly created before the test runs.
- The test verifies the file exists at the exact absolute path target.
- The test explicitly checks that the file does NOT exist at an incorrect concatenated path.
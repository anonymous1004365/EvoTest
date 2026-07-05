---
name: file-tree-traversal-directory-filtering
description: When using Google Guava's Files.fileTreeTraverser().postOrderTraversal()
  to walk a directory tree and filter out only data files (not directory segments),
  a file named like a directory segment (e.g., a single character "c") in the root
  folder may pass through if the filter only checks the immediate parent. Use this
  skill to detect such incorrect inclusion of short-named files.
code_tags:
- ARGUMENT_VALIDATION
- BOUNDARY_CHECK
- ARRAY_INDEX_ACCESS
- FILE_TREE_TRAVERSAL_FILTER
test_pattern: PARAMETRIC_TEST
---

# file-tree-traversal-directory-filtering

## Instructions

# File Tree Traversal with PostOrder and Directory-Like File Names

## Instructions

- WHEN the TG encounters a method that uses `Files.fileTreeTraverser().postOrderTraversal()` (or similar Guava tree traversal) combined with a `Predicate<File>` filter to identify data store files by checking `input.isFile() && !input.getParent().equals(path)`:
  - THEN the TG should recognize that `postOrderTraversal()` visits ALL nodes in the tree — including files that happen to be siblings of directory nodes at the top level, and files at ANY depth.
  - Specifically, when the data store layout follows a pattern like `ab/cd/ef/abcdef` (sharding directories of 2-character names), a file named with a short string (e.g., `"c"` or `"ab"`) placed directly inside the root directory will have its **parent equal to the root path**, so the filter condition `!input.getParent().equals(path)` will EXCLUDE it — yet this is correct behavior (non-data files at root level should be excluded).
  - BUT the BUG is the **opposite**: a file named `"c"` (a single character) that is NOT at the root but at depth 1 (e.g., `root/c`) will have a parent path like `root` which equals `path`, so it will be FILTERED OUT — but it should NOT be filtered out because it IS a valid data identifier at depth 2+ in the tree... wait, let's re-examine.

  - **The actual bug**: The filter `input.isFile() && !input.getParent().equals(path)` is meant to keep only files that are NOT directly in the root (since root-level files are metadata, not data files — data files live in subdirectories like `ab/cd/ef/abcdef`). However, because `postOrderTraversal()` visits nodes at ALL depths, a file with a short name (e.g., `"c"`) that is placed at depth 2 (e.g., `root/someDir/c`) will have `input.getParent()` equal to `root/someDir`, which is NOT equal to `path` (`root`). So it PASSES the filter and gets included as a data identifier — but it's NOT a valid data file (it doesn't follow the `xx/yy/zz/xxxxxxxx...` sharding pattern). The test `testGetAllIdentifiers` in `OakFileDataStoreTest` includes a file named `"c"` at the root depth and expects it NOT to appear in the results.

  - **Key insight**: The bug is that `postOrderTraversal()` flattens the tree. A file named `"c"` sitting at depth 1 (directly under root) IS correctly excluded by the filter (parent == path). BUT a file with the SAME name `"c"` that happens to be nested inside a subdirectory would INCORRECTLY pass through. The test in `OakFileDataStoreTest` creates a file at `testDir/c` directly and the result shows `"c"` unexpectedly appearing — meaning there IS a scenario where the filter fails.

  - **Correct action for the TG**: Write a test that places a short-named file (e.g., `"c"`, `"ab"`, `"x"`) inside the datastore path but NOT following the sharding directory structure (either directly at the root or in a non-standard subdirectory), and verify that `getAllIdentifiers()` does NOT include it. The test should:
    1. Create a temporary directory
    2. Create valid data files following the 2-2-2 sharding scheme: e.g., `ab/cd/ef/abcdef`, `bc/de/fg/bcdefg`, `cd/ef/gh/cdefgh`
    3. Create a short-named file at the root level (e.g., `c` directly under the temp dir, or `ab` directly under the temp dir)
    4. Initialize `OakFileDataStore` with this path
    5. Call `getAllIdentifiers()` and collect the results
    6. Assert that the result set equals only the valid data identifiers: `{"abcdef", "bcdefg", "cdefgh"}` — i.e., short-named files like `"c"` must NOT appear

- Common pitfalls to avoid:
  - **Testing only with standard sharding paths**: The TG might test only with `ab/cd/ef/abcdef`-style paths and miss edge cases where non-standard short-named files appear in the tree.
  - **Assuming the filter correctly handles all depths**: The predicate `!input.getParent().equals(path)` only checks if the parent is the root path. It does NOT verify whether the file actually follows the expected sharding pattern (e.g., at least 2 levels of nesting, or minimum path length).
  - **Not considering that `postOrderTraversal` visits every node**: The TG might forget that tree traversal visits directories too (though the `.filter(input.isFile())` handles that), and also visits files at every depth level.
  - **Assuming file names at the root are always metadata**: While root-level files ARE metadata, the filter is designed to exclude them. But a file nested even 1 level deep (e.g., `someDir/myfile`) with a name that doesn't match the sharding scheme would pass through. The TG should test that such files are NOT included (since they're not valid data files).

- **Correct test code example**:

```java
@Test
public void testGetAllIdentifiersExcludesShortNamedFiles() throws Exception {
    File testDir = new File("./target/oak-fds-test-" + System.currentTimeMillis());
    testDir.mkdirs();
    
    // Create valid data files with sharding directories
    FileUtils.touch(new File(testDir, "ab/cd/ef/abcdef"));
    FileUtils.touch(new File(testDir, "bc/de/fg/bcdefg"));
    FileUtils.touch(new File(testDir, "cd/ef/gh/cdefgh"));
    
    // Create a short-named file directly at root that should be excluded
    FileUtils.touch(new File(testDir, "c"));
    
    OakFileDataStore fds = new OakFileDataStore();
    fds.setPath(testDir.getAbsolutePath());
    fds.init(null);
    
    Iterator<DataIdentifier> dis = fds.getAllIdentifiers();
    Set<String> fileNames = Sets.newHashSet(
        Iterators.transform(dis, input -> input.toString()));
    
    Set<String> expected = Sets.newHashSet("abcdef", "bcdefg", "cdefgh");
    assertEquals("Short-named file 'c' should not appear in identifiers", 
        expected, fileNames);
    
    FileUtils.cleanDirectory(testDir);
}
```

- **Incorrect test code (common pitfall)**:

```java
// BAD: Only creates valid sharded files, no edge case file
@Test
public void testGetAllIdentifiers() throws Exception {
    File testDir = new File("./target/oak-fds-test");
    FileUtils.touch(new File(testDir, "ab/cd/ef/abcdef"));
    FileUtils.touch(new File(testDir, "bc/de/fg/bcdefg"));
    
    OakFileDataStore fds = new OakFileDataStore();
    fds.setPath(testDir.getAbsolutePath());
    fds.init(null);
    
    // This passes even with the bug, because there's no edge case file
    // like 'c' that would incorrectly slip through the filter
    assertEquals(2, Iterators.size(fds.getAllIdentifiers()));
}
```
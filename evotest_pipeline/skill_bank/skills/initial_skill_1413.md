---
name: vfs-cache-directory-config-usage
description: When testing VFS (Virtual File System) cache directory configuration,
  verify that when a user sets "general.vfs.cache.dir", the generated VFS manager
  actually uses that custom path instead of the default java.io.tmpdir. The triggering
  test for this bug is testCacheDirectoryConfigured in AccumuloVFSClassLoaderTest.
code_tags:
- RESOURCE_MANAGEMENT
- NULL_CHECK
test_pattern: STATE_TEST
---

# vfs-cache-directory-config-usage

## Instructions

# VFS Cache Directory Configuration Verification

## Instructions

WHEN the TG encounters code that generates a VFS `FileSystemManager` (e.g., `AccumuloVFSClassLoader.generateVfs()`) and that code reads a configuration property like `"general.vfs.cache.dir"` to set a cache directory path via `DefaultFileSystemManager.setReplicator()` or similar, THEN the TG should:

1. **Write a test that sets the cache directory configuration to a custom, non-default value** (e.g., `"/some/random/cache/dir"`) and then verifies the generated VFS manager actually uses that custom path. Do NOT just test the default case (where no cache directory is configured and `java.io.tmpdir` is expected).

2. **Access the internal state** of the VFS `FileSystemManager` after generation to verify the cache directory. Use `Whitebox.getInternalState(manager, "fileReplicator")` to get the `UniqueFileReplicator`, then `Whitebox.getInternalState(replicator, "tempDir")` to get the `File` object representing the temp directory, and assert that the temp directory's parent path equals the configured custom cache directory path.

3. **Verify that the tempDir is actually a subdirectory of the configured cache directory**, not just that the property was read. For example, if the configured cache dir is `"/some/random/cache/dir"`, assert that `tempDir.getParent()` equals that path (not `java.io.tmpdir`).

4. **Test both scenarios**: (a) default behavior when no cache dir is configured falls back to `java.io.tmpdir`, and (b) explicit behavior when cache dir IS configured uses that configured path.

Common pitfalls to avoid:
- **Testing only the default case**: The bug is that even when a user configures the cache directory, the VFS manager still uses the default temp directory. Testing only the unconfigured case will NOT catch this bug.
- **Not accessing internal state**: The cache directory is stored in private fields of the `DefaultFileSystemManager` and `UniqueFileReplicator`. You must use reflection (e.g., `Whitebox`) to inspect them — there is no public getter.
- **Assuming the configured path IS the tempDir**: The configured cache directory is the *parent* of the actual temp directory. The tempDir is typically a randomly-named subdirectory like `"accumulo-vfs-cache-<username>"` created inside the configured cache directory. Assert `tempDir.getParent()` equals the configured path, not `tempDir.getAbsolutePath()`.
- **Forgetting to clean up**: After assertions, the test should reset the state (e.g., `Whitebox.setInternalState(AccumuloVFSClassLoader.class, "loader", null)`) to avoid test pollution.

### Correct approach (catches the bug)

```java
// Set a custom cache directory via configuration
String cacheDir = "/some/random/cache/dir";
// ... create configuration XML with general.vfs.cache.dir set to cacheDir ...
// ... initialize AccumuloVFSClassLoader with the config ...
AccumuloVFSClassLoader.getClassLoader();
FileSystemManager manager = AccumuloVFSClassLoader.generateVfs();
UniqueFileReplicator replicator = Whitebox.getInternalState(manager, "fileReplicator");
File tempDir = Whitebox.getInternalState(replicator, "tempDir");
Assert.assertEquals("The configured cache dir should be the parent of tempDir",
    cacheDir, tempDir.getParent());
```

### Incorrect approach (would NOT catch the bug)

```java
// Only testing the default case (no cache directory configured)
// ... create configuration XML WITHOUT general.vfs.cache.dir ...
// ... initialize ...
FileSystemManager manager = AccumuloVFSClassLoader.generateVfs();
UniqueFileReplicator replicator = Whitebox.getInternalState(manager, "fileReplicator");
File tempDir = Whitebox.getInternalState(replicator, "tempDir");
Assert.assertTrue(tempDir.getParent().equals(System.getProperty("java.io.tmpdir")));
// This passes even on the buggy version, so it doesn't detect the bug!
```
---
name: table-path-tableid-validation
description: When writing tests for path construction methods that extract table IDs
  from path components, test that paths missing a table ID component throw an IllegalArgumentException.
  This applies to getFullPath() variants that parse paths for VolumeManager.
code_tags:
- PATH_TABLEID_EXTRACTION
- VOLUME_PATH_CONSTRUCTION
test_pattern: EXCEPTION_TEST
---

# table-path-tableid-validation

## Instructions

# Table Path Validation: Missing TableID Extraction

## Instructions

- WHEN the TG encounters a `getFullPath(FileType, String)` or `getFullPath(String tableId, String path)` method that constructs a full filesystem path by extracting or validating a table ID from the path string
- THEN the TG should write exception tests that pass path strings **without** a table ID component (e.g., `"/default_tablet/"`, `"/t-0000001/"`, `"/default_tablet/C0000001.rf"`, `"/t-0000001/C0000001.rf"`) and verify that `IllegalArgumentException` is thrown
- Additionally, the TG should write happy-path tests that pass path strings **with** a table ID component (e.g., `"1/default_tablet/"`, `"1/t-0000001"`, `"1/default_tablet/C0000001.rf"`) and verify that the resulting `Path` is correctly constructed with the table ID as the first path component

### Concrete Values/Examples

The path structure follows this pattern:
```
<volume-base>/tables/<tableId>/<tablet-or-wal-path>
```

The regex used to extract the table ID from the path is:
```
^/([^/]+)/
```
Where the first component after the leading slash is expected to be a table ID.

**Valid paths** (containing a table ID):
- `"1/default_tablet/"` → tableId = `"1"`, tablet dir = `"default_tablet/"`
- `"1/t-0000001"` → tableId = `"1"`, tablet dir = `"t-0000001"`
- `"1/default_tablet/C0000001.rf"` → tableId = `"1"`, file = `"default_tablet/C0000001.rf"`
- `"1/t-0000001/C0000001.rf"` → tableId = `"1"`, file = `"t-0000001/C0000001.rf"`

**Invalid paths** (missing a table ID — should throw `IllegalArgumentException`):
- `"/default_tablet/"` — no leading table ID component
- `"/t-0000001/"` — no leading table ID component
- `"/default_tablet/C0000001.rf"` — no leading table ID component
- `"/t-0000001/C0000001.rf"` — no leading table ID component

### What the Test Should Verify

For exception tests: Call `getFullPath(FileType.TABLE, invalidPath)` and assert that it throws `IllegalArgumentException`.

For happy-path tests: Call `getFullPath(FileType.TABLE, validPath)` and assert:
1. The returned `Path` is not null
2. The returned `Path` ends with the original path string
3. The returned `Path` contains the volume base path as its prefix

### Common Pitfalls to Avoid

- ❌ Testing only one type of invalid path (e.g., only `"/default_tablet/"` without also testing `"/t-0000001/"`, `"/default_tablet/file.rf"`, and `"/t-0000001/file.rf"`)
- ❌ Forgetting that the path may or may not have a trailing slash — test both `"/default_tablet/"` and `"/default_tablet"`
- ❌ Assuming that paths like `"/t-0000001/"` are valid because they look like they have a table-like component — the leading slash means the first path component is empty, so no table ID is extracted
- ❌ Not testing paths with file extensions (`.rf`, `.wal`, etc.) after the tablet directory

### Correct Test Example (Java/JUnit)

```java
@Test(expected = IllegalArgumentException.class)
public void tabletDirWithoutTableId() throws Exception {
    fs.getFullPath(FileType.TABLE, "/t-0000001/");
}

@Test(expected = IllegalArgumentException.class)
public void defaultTabletFileWithoutTableId() throws Exception {
    fs.getFullPath(FileType.TABLE, "/default_tablet/C0000001.rf");
}

@Test
public void tabletDirWithTableId() throws Exception {
    Path fullPath = fs.getFullPath(FileType.TABLE, "1/default_tablet/");
    Assert.assertTrue(fullPath.toString().endsWith("1/default_tablet/"));
}

@Test
public void tabletFileWithTableId() throws Exception {
    Path fullPath = fs.getFullPath(FileType.TABLE, "1/default_tablet/C0000001.rf");
    Assert.assertTrue(fullPath.toString().endsWith("1/default_tablet/C0000001.rf"));
}
```

### Incorrect Test Example

```java
// BAD: Only tests one invalid case, misses tablet paths with file extensions
@Test(expected = IllegalArgumentException.class)
public void onlyTestsDefaultTablet() throws Exception {
    fs.getFullPath(FileType.TABLE, "/default_tablet/");
}

// BAD: Assumes "/t-0000001/" is valid (missing tableId)
@Test
public void incorrectlyAssumesValid() throws Exception {
    Path fullPath = fs.getFullPath(FileType.TABLE, "/t-0000001/");
    // This should have thrown, but test assumes it works
    Assert.assertNotNull(fullPath);
}
```
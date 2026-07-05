---
name: file-extension-parsing-with-multiple-dots
description: WHEN testing file operations that extract extensions using split("\\.")
  or similar parsing, THEN test filenames containing multiple dots to verify the last
  segment is correctly identified as the extension.
code_tags:
- VALIDATION
- FILE_EXTENSION_PARSING
test_pattern: EXCEPTION_TEST
---

# file-extension-parsing-with-multiple-dots

## Instructions

# File Extension Parsing With Multiple Dots

## Instructions

WHEN the TG encounters code that extracts a file extension from a filename (e.g., using `name.split("\\.")` and taking the last element), THEN the TG should test with filenames that contain more than one dot to ensure the extension is correctly identified as the segment after the *last* dot (e.g., `test.file.rf` should yield extension `rf`, not `file`).

- Use `FileOperations.getInstance()` to obtain the `FileOperations` instance.
- Create a filename string with multiple dots before the actual extension, such as `"target/test.file." + RFile.EXTENSION` (where `RFile.EXTENSION` is `"rf"`).
- Attempt to create a writer using `newWriterBuilder().forFile(filename, fs, conf).withTableConfiguration(acuconf).build()`.
- On the buggy version, the code incorrectly throws an exception (e.g., `IllegalArgumentException: File type file not supported`) because it takes the wrong split segment. The test should catch this exception and fail if one is thrown.
- Verify the writer creation succeeds by calling `writer.close()`.
- Common pitfall: Only testing filenames with a single dot (e.g., `test.rf`). This misses the bug because the issue only manifests with multi-dot filenames.
- Common pitfall: Assuming `split("\\.")` on `"test.file.rf"` returns `["test", "file", "rf"]` and that `sp[sp.length-1]` always correctly picks `"rf"` — the bug is that the code uses `sp[1]` instead of `sp[sp.length-1]` in some extension comparison logic, or misreads the result. Test concretely to catch this.

Example of correct test:
```java
// Correct: tests a filename with multiple dots before the extension
String filename = "target/test.file." + RFile.EXTENSION;
FileOperations fileOperations = FileOperations.getInstance();
Configuration conf = new Configuration();
FileSystem fs = FileSystem.getLocal(conf);
AccumuloConfiguration acuconf = DefaultConfiguration.getInstance();
FileSKVWriter writer = fileOperations.newWriterBuilder()
    .forFile(filename, fs, conf)
    .withTableConfiguration(acuconf)
    .build();
writer.close();
// Expect: no exception thrown
```

Example of incorrect test (would miss the bug):
```java
// Incorrect: only tests a filename with a single dot
String filename = "target/test." + RFile.EXTENSION;
FileOperations fileOperations = FileOperations.getInstance();
// ... rest of setup ...
// This would pass even on the buggy version, giving false confidence
```
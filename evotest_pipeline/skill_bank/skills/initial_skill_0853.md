---
name: date-template-substitution-validation
description: When template expressions (e.g., ${date:pattern}) are used in configuration
  values (like file names), the test must verify they are correctly substituted with
  actual values (not left as literal template strings). This skill teaches how to
  test that date lookups and similar StrLookup template substitutions produce resolved
  values.
code_tags:
- VALIDATION
test_pattern: STATE_TEST
---

# date-template-substitution-validation

## Instructions

# Date Template Substitution Validation

## Instructions

- WHEN the TG encounters code that uses `${date:pattern}` or similar `StrLookup`-based template expressions in configuration values (e.g., `fileName`, `filePattern`, or any string field) — especially in `StrSubstitutor` or `Interpolator`-backed resolution
- THEN the TG should write a test that:
  1. Configures the system with a template string containing `${date:yyyy-MM-dd HHmmss}` (or similar date pattern)
  2. Triggers the resolution/substitution of that template (e.g., by starting a logger, writing a log event, or directly invoking the lookup)
  3. Asserts that the **resulting resolved string is NOT equal to the original template** — that is, the date expression was actually substituted with a formatted date string
  4. Specifically, assert that the result does NOT contain `${date` — use `assertFalse(result.contains("${date"))` or `assertFalse(result.contains("${date:yyyy-MM-dd HHmmss}"))`
  5. Additionally, the result should match the expected date pattern format (e.g., contain `-` or `:` characters from the format string)
- Common pitfalls:
  - Testing only that no exception is thrown, without checking the actual substituted value
  - Asserting the result equals a hardcoded date string (impossible since dates change)
  - Not accounting for the `bufferedIO="false"` setting that forces immediate file creation
  - Testing only `DateLookup.lookup()` directly, instead of testing the full `StrSubstitutor` → `Interpolator` → `DateLookup` resolution chain
  - Assuming a `null` return from a map lookup means the template should remain as-is, rather than checking for proper resolution

### Correct Example (Testing template substitution in file appender file name):
```java
@Test
public void testFileName() {
    // The appender is configured with fileName="target/${date:yyyy-MM-dd HHmmss}.log"
    // After logging, the file should have been created with a resolved date
    final File dir = new File("target");
    assertTrue("Directory 'target' should exist", dir.exists() || dir.mkdirs());
    final Logger logger = LogManager.getLogger();
    logger.error("This is a test");
    final File[] files = dir.listFiles((d, name) -> name.endsWith(".log"));
    assertNotNull(files);
    assertTrue("At least one .log file should exist after logging", files.length > 0);
    // The file name should NOT contain the literal template string
    for (File f : files) {
        assertFalse("File name should not contain literal template: " + f.getName(),
            f.getName().contains("${date"));
    }
}
```

### Incorrect Example (Only checking no exception, not checking substitution):
```java
@Test
public void testFileName() {
    // BAD: Only checks that the appender doesn't throw on start
    final Logger logger = LogManager.getLogger();
    logger.error("This is a test");
    // No assertion that the file was created with a resolved date
}
```
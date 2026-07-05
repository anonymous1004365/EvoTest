---
name: file-endpoint-directory-validation
description: When configuring file endpoints with autoCreateDirectory=true, ensure
  the endpoint does not prematurely validate the directory path before it's auto-created.
  This skill detects bugs where directory validation rejects paths containing dots
  (like 'foo.bar') even though auto-creation is enabled.
code_tags:
- DIRECTORY_VALIDATION
- FILE_ENDPOINT_CONFIG
- ERROR_HANDLING
test_pattern: EXCEPTION_TEST
---

# file-endpoint-directory-validation

## Instructions

# File Endpoint Directory Validation

## Instructions

- WHEN the TG encounters a file endpoint with `autoCreate=true` (or `autoCreateDirectory=true`) and a directory path that contains a dot/period character (e.g., `target/file/foo.bar`, `mydir/test.txt`)
- THEN the TG should write a test that:
  1. Creates a file endpoint URI with a path containing dots (e.g., `file:target/file/foo.bar?autoCreate=true`)
  2. Expects the endpoint to successfully create the directory structure and initialize without throwing an `IllegalArgumentException` with message "Only directory is supported. Endpoint must be configured with a valid starting directory"
  3. Verifies the directory was actually created (e.g., `assertTrue(new File("target/file/foo.bar").isDirectory())`)
  4. Sends/receives a file through the consumer to confirm the endpoint works end-to-end
- The TG should NOT assume that a path with dots always represents a file with an extension — directories can legally contain dots in their names
- Common pitfalls:
  - Testing only a path without dots (which passes by default, masking the bug)
  - Assuming the error thrown is a checked exception — it's an `IllegalArgumentException` (runtime)
  - Setting `autoCreate=false` — the bug only manifests with auto-creation enabled, as the validation rejects paths with dots before creation happens
  - Confusing this with file name/extension validation logic (this is about directory path validation during endpoint initialization)

### ✅ Correct test example (catches the bug):
```java
@Test
public void testAutoCreateDirectoryWithDot() throws Exception {
    FileEndpoint endpoint = context.getEndpoint("file:target/file/foo.bar?autoCreate=true", FileEndpoint.class);
    assertNotNull(endpoint);
    // Verify the directory was actually created
    File dir = new File("target/file/foo.bar");
    assertTrue("Directory should have been auto-created", dir.isDirectory());
}
```

### ❌ Incorrect test example (misses the bug):
```java
@Test
public void testAutoCreateDirectoryWithoutDot() throws Exception {
    FileEndpoint endpoint = context.getEndpoint("file:target/simple?autoCreate=true", FileEndpoint.class);
    assertNotNull(endpoint);
    // This passes even on the buggy version because path has no dots
}
```
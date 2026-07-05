---
name: enforce-mounts-configuration-flag
description: ''
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- CONFIGURATION_FLAG
test_pattern: PARAMETRIC_TEST
---

# enforce-mounts-configuration-flag

## Instructions

# Enforce Mounts Configuration Flag

## Instructions

- WHEN the TG encounters code that checks a boolean configuration flag from `SecuritySettings.getEnforceMounts()` to decide whether to enforce URL mount requirements for bookmarkable pages
- THEN it should write a parametric-style test that:
  1. Creates a `SecuritySettings` instance and sets `enforceMounts` to `true` and to `false`.
  2. For each setting, constructs a `BookmarkableMapper` (or similar mapper) and resolves a request for a page class that DOES have a proper mount path.
  3. Verifies that both the mounted and unmounted page class return a non-null `PageResult` (i.e. the mapper does not return `null`), regardless of the `enforceMounts` setting.
  4. Specifically test that setting `enforceMounts(true)` does NOT cause the mapper to reject a properly mounted page request by returning `null` for the page.
- Include concrete values: use `SecuritySettings ss = new SecuritySettings(); ss.setEnforceMounts(true);`, then `Application.get().setSecuritySettings(ss);`, then call `mapper.mapRequest(...)` and assert the result is not null.
- Common pitfalls:
  - Testing only the default (`enforceMounts = false`) and missing the `true` case.
  - Failing to re-set the security settings on the Application before each test case.
  - Testing `enforceMounts(true)` with an unmounted page class but forgetting to test it with a mounted one (the bug is that even mounted pages can return null).
  - Not calling `Application.get().setSecuritySettings(ss)` before the mapper runs — the mapper reads the setting from the global Application instance.

### Correct example (Java/JUnit 5):

```java
@Test
void enforceMountsWithMountedPage_ShouldNotReturnNullPage() {
    // Set enforceMounts to true
    SecuritySettings ss = new SecuritySettings();
    ss.setEnforceMounts(true);
    Application application = Application.get();
    SecuritySettings original = application.getSecuritySettings();
    try {
        application.setSecuritySettings(ss);
        
        BookmarkableMapper mapper = new BookmarkableMapper();
        // Resolve a page class that has a proper mount
        PageParametersEncoder encoder = new PageParametersEncoder();
        Request request = new MockRequest(application, HttpMethod.GET, "/mount/path/for/TestPage");
        PageResult result = mapper.mapRequest(request);
        
        assertNotNull("Page should not be null when enforceMounts=true and page is mounted", result);
    } finally {
        application.setSecuritySettings(original);
    }
}
```

### Incorrect example:

```java
// BUG: Only tests enforeMounts=false (default), missing the true case
@Test
void enforceMountsWithMountedPage_Default() {
    BookmarkableMapper mapper = new BookmarkableMapper();
    Request request = new MockRequest(application, HttpMethod.GET, "/mount/path/for/TestPage");
    PageResult result = mapper.mapRequest(request);
    assertNotNull(result);  // Passes by luck, but doesn't test the bug
}
```
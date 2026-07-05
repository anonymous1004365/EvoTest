---
name: mount-security-enforcement-test
description: When testing mount path security enforcement, verify that unmounted pages
  are blocked when enforceMounts=true and that the mapper's resolve method returns
  null for unmounted page classes.
code_tags:
- ARGUMENT_VALIDATION
- STATE_MUTATION
- BEAN_PROPERTY_ASSIGNMENT
test_pattern: STATE_TEST
---

# mount-security-enforcement-test

## Instructions

# Mount Security Enforcement Test

## Instructions

- WHEN the TG encounters code that uses `getSecuritySettings().getEnforceMounts()` or `setEnforceMounts(true)` in a mapper's resolve method (e.g., `BookmarkableMapper.resolve()`)
- THEN it should test that when `enforceMounts` is enabled, unmounted page classes produce a `null` result from the mapper, and that mounted page classes still resolve correctly
- Include concrete types: use `org.apache.wicket.settings.SecuritySettings`, `org.apache.wicket.core.request.mapper.BookmarkableMapper`, and a page class like `UnknownPage` that is NOT explicitly mounted
- The test should verify that `tester.executeUrl(...)` with the unmounted page's URL returns an HTTP response whose `getErrorMessage()` (or `getText()`) indicates the page was not found (e.g., expecting `null` from mapper `resolve()`)
- Common pitfalls: (1) Testing only that mounted pages work without verifying that unmounted pages are properly blocked; (2) Forgetting to call `tester.getApplication().getSecuritySettings().setEnforceMounts(true)` before the request; (3) Using a page class that is actually mounted by default (e.g., `SignInPage`), leading to a false pass

### Correct Example:
```java
// In the test method:
@Test
public void enforceMounts() {
    WicketTester tester = new WicketTester();
    tester.getApplication().getSecuritySettings().setEnforceMounts(true);
    
    // UnknownPage is NOT mounted - should be blocked
    tester.executeUrl("wicket/bookmarkable/org.apache.wicket.settings.ISecuritySettingsTest$UnknownPage");
    // On the buggy version, this incorrectly returns the page.
    // On the fixed version, this returns null/404.
}
```

### Incorrect Example:
```java
// BAD: Not enabling enforceMounts before the request
@Test
public void enforceMounts() {
    WicketTester tester = new WicketTester();
    // Missing: tester.getApplication().getSecuritySettings().setEnforceMounts(true);
    
    // This request would succeed even on the buggy version because enforceMounts is false
    tester.executeUrl("wicket/bookmarkable/org.apache.wicket.settings.ISecuritySettingsTest$UnknownPage");
    // Test passes on buggy version too - false sense of security!
}
```
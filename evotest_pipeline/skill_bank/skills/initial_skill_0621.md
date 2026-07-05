---
name: enforce-mounts-with-encrypted-mapper
description: ''
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
- RESOURCE_MANAGEMENT
- STATE_MUTATION
- VALIDATION
test_pattern: STATE_TEST
---

# enforce-mounts-with-encrypted-mapper

## Instructions

# Enforce Mounts with Encrypted Request Mapper

## Instructions

- WHEN the test verifies that `getEnforceMounts()` in `SecuritySettings` blocks access to unmounted bookmarkable pages (i.e., pages not explicitly mounted via `mountPage()` or `mountPackage()`)
- THEN the test must also set up an encrypted/chained request mapper (e.g., `CryptoMapper`) as the root request mapper via `Application.get().setRootRequestMapper(...)` and verify that `getEnforceMounts()` still correctly blocks unmounted pages.
  - Specifically, call `application.setRootRequestMapper(new CryptoMapper(application.getRootRequestMapper(), application))` before testing the mount enforcement.
  - Then attempt to render a page class that is NOT mounted (e.g., a page class like `UnknownPage` that extends `WebPage` but is never mounted).
  - Verify that the page is NOT rendered — i.e., the `LastPage` that results from the request should be `null` or should be an error page, not the unmounted page.
  - On the buggy version, the unmounted page would incorrectly be rendered (e.g., you'd get `[Page class = ...UnknownPage, id = 2, render count = 1]`).

- Common pitfalls to avoid:
  - Testing `getEnforceMounts()` only without a wrapped/encrypted mapper (this would pass even on the buggy version, missing the bug).
  - Forgetting to wrap the existing root mapper: `new CryptoMapper(application.getRootRequestMapper(), application)` — passing `null` as the delegate mapper will break the mapper chain.
  - Not checking the final rendered page: The test should assert that the last rendered page after the request is `null` (or an error handling page), not the unmounted page class.
  
  **Correct example (catches the bug):**
  ```java
  @Test
  public void enforceMountsWithCryptoMapper()
  {
      // given
      MyApplication application = new MyApplication();
      application.setRootRequestMapper(
          new CryptoMapper(application.getRootRequestMapper(), application));
      application.getSecuritySettings().setEnforceMounts(true);
  
      // when
      WebRequest request = new WebRequest(new Url(Url.parse("wicket/bookmarkable/org.apache.wicket.settings.ISecuritySettingsTest$UnknownPage")));
      application.processRequest(request, new WebResponse(null));
  
      // then - UnknownPage should NOT be rendered because it's not mounted
      assertNull("Unmounted page should not be rendered when enforceMounts=true with CryptoMapper",
          application.getLastPage());
  }
  ```

  **Incorrect example (misses the bug):**
  ```java
  @Test
  public void enforceMounts()
  {
      // given
      MyApplication application = new MyApplication();
      // BUG: No CryptoMapper wrapper is set up
      application.getSecuritySettings().setEnforceMounts(true);
  
      // when
      WebRequest request = new WebRequest(new Url(Url.parse("wicket/bookmarkable/org.apache.wicket.settings.ISecuritySettingsTest$UnknownPage")));
      application.processRequest(request, new WebResponse(null));
  
      // then - This passes even on the buggy version because the bug only manifests 
      // when a CryptoMapper (or similar wrapping mapper) is configured
      assertNull("Unmounted page should not be rendered when enforceMounts=true",
          application.getLastPage());
      // This test would pass even when the bug exists!
  }
  ```
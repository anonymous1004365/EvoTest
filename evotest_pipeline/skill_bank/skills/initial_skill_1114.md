---
name: expired-page-parameter-preservation
description: When a page is expired and recreated by a mounted mapper, the mounted
  URL's indexed parameters must be preserved and not overwritten by the recreated
  page's empty PageParameters. The TG should test that mounted page links on expired
  sessions produce URLs containing index parameters.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- NULL_CHECK
test_pattern: STATE_TEST
---

# expired-page-parameter-preservation

## Instructions

# Expired Page Parameter Preservation in Mounted Mappers

## Instructions

- WHEN the TG encounters a scenario where a mounted page is accessed after its session has expired, and the page is recreated (e.g., using `PageProvider` with `PageParameters`), THEN the TG should test that the URL generated for the recreated page still contains the indexed mount parameters (e.g., `param=value`) and does NOT drop them.

- WHEN the TG tests link rendering on a mounted page that has expired, THEN the TG should verify that the rendered URL includes the expected indexed parameters from the mount path. Specifically, use `assertMarkup` or a matcher that checks for the presence of `param=value` or similar indexed parameter patterns in the HTML output.

- WHEN the TG uses `MountedMapper` to mount a page class with a parameterized path (e.g., `/mount/path/${param}`), and the page's `getPageParameters()` is initially empty (null/empty), THEN the test should simulate session expiry (using a mock `RequestCycle` or session invalidation), recreate the page, and verify that the link's URL retains the indexed parameter (e.g., `param=value`).

- Common pitfalls to avoid:
  - Testing only the fresh (non-expired) case, which may work correctly while the expired case silently drops parameters.
  - Assuming that `PageParameters` from the mount path are always merged correctly into empty `PageParameters` of a recreated page.
  - Not using a test framework that can simulate page expiry (e.g., by clearing the session or marking the page as expired in `PageProvider`).

- Correct example (checking that indexed params appear after expiry):
  ```java
  @Test
  public void testLinkOnExpiredPage() {
      // Mount a page with indexed parameter
      getApplication().mount(new MountedMapper("/mount/path/${param}", PageWithLink.class));
  
      // Execute the page with the indexed parameter value
      execute(PageWithLink.class, new PageParameters().set("param", "value"));
  
      // Simulate expiry and recreate by getting a fresh page instance with empty params
      execute(PageWithLink.class, new PageParameters());
  
      // Expected: the link should contain "param=value"
      assertMarkup(".*param=value.*");
  }
  ```

- Incorrect example (testing only fresh session):
  ```java
  @Test
  public void testLinkOnFreshPage() {
      // Only test the non-expired case
      getApplication().mount(new MountedMapper("/mount/path/${param}", PageWithLink.class));
      execute(PageWithLink.class, new PageParameters().set("param", "value"));
      
      // This passes, but misses the expired case
      assertMarkup(".*param=value.*");
  }
  ```
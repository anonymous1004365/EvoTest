---
{}
---

---
name: enforce-mounts-with-crypto-mapper
description: When testing URL enforcement with CryptoMapper, test that plain-text bookmarkable URLs return null page when enforceMounts is enabled. Also test state transitions: starting without enforceMounts, then enabling it, to ensure each behavior is correct.
code_tags: ['EXCEPTION_HANDLING', 'VALIDATION', 'NULL_CHECK', 'STATE_MUTATION', 'ORDER_DEPENDENCY']
test_pattern: STATE_TEST
---

# enforce-mounts-with-crypto-mapper

## Instructions

# Testing Enforce Mounts With CryptoMapper Wrapping

## Instructions

- **WHEN** the TG encounters code where a `CryptoMapper` wraps a `BookmarkableMapper` (or the root request mapper) and the application uses `setEnforceMounts(true)` on `SecuritySettings`, and the `BookmarkableMapper.parseRequest()` returns `null` when `getEnforceMounts()` is `true`:
  - **THEN** the TG should write a stateful test that:
    1. Creates a `BookmarkablePageRequestHandler` with a `PageProvider` targeting a known page class (e.g., `UnknownPage.class`).
    2. Verifies that a plain-text (non-encrypted) URL generated from that handler starts with `"wicket/bookmarkable/"` and serves the page successfully (page is rendered).
    3. Sets `app.setRootRequestMapper(new CryptoMapper(app.getRootRequestMapper(), app))` and executes a dummy request to re-initialize the tester.
    4. Verifies that the encrypted URL no longer starts with `"wicket/bookmarkable/"`.
    5. Verifies that the plain-text URL returns `assertNull(tester.getLastRenderedPage())` — the page must be `null` because the `BookmarkableMapper` is now behind `CryptoMapper` and the crypted URL is the only valid path.
    6. Verifies that the encrypted URL still serves the page correctly (`assertRenderedPage(UnknownPage.class)`).
    7. After mounting the page with `app.mountPackage("unknown", UnknownPage.class)` and then setting `app.getSecuritySettings().setEnforceMounts(true)`, verifies that both plain-text AND encrypted URLs return `assertNull(tester.getLastRenderedPage())` because enforceMounts rejects all non-mounted URLs regardless of encryption.

  - **Common pitfalls to avoid**:
    - **Testing only the plain-text URL path**: Without a `CryptoMapper`, `BookmarkableMapper.parseRequest()` directly checks `getEnforceMounts()` and returns `null`. But with `CryptoMapper` wrapping it, the `CryptoMapper` decrypts the URL FIRST, and then delegates to the wrapped mapper with the decrypted URL. A plain-text URL will not decrypt correctly and will be handled differently. The test must verify BOTH plain-text AND encrypted URLs at each stage.
    - **Forgetting the dummy request after CryptoMapper installation**: After changing the root request mapper at runtime, `WicketTester` may not immediately pick up the new mapper. Execute a dummy URL (e.g., `tester.executeUrl("")`) to force re-initialization.
    - **Testing `enforceMounts(true)` without first verifying the plain-text URL fails**: The bug is that when `CryptoMapper` wraps the root mapper and `enforceMounts` is NOT yet enabled, calling the plain-text URL should already return `null` because the `CryptoMapper` doesn't understand plain `wicket/bookmarkable/` URLs. But without `enforceMounts`, the `BookmarkableMapper` (decrypted) would still serve it. The test must verify that the plain-text URL is null once the `CryptoMapper` is in place, even before `enforceMounts` is turned on.
    - **Not checking that the page reference is null**: Use `assertNull(tester.getLastRenderedPage())` not just `assertRenderedPage(someOtherPage)` to confirm no page was rendered at all.

  - **Example (correct)**:
    ```java
    IRequestHandler handler = new BookmarkablePageRequestHandler(new PageProvider(UnknownPage.class));
    String plainTextNonMountedUrl = tester.urlFor(handler).toString();
    assertTrue(plainTextNonMountedUrl.startsWith("wicket/bookmarkable/"));
    
    // Without CryptoMapper, the plain URL works
    tester.executeUrl(plainTextNonMountedUrl);
    tester.assertRenderedPage(UnknownPage.class);
    
    // Install CryptoMapper
    app.setRootRequestMapper(new CryptoMapper(app.getRootRequestMapper(), app));
    tester.executeUrl(""); // dummy request
    
    String encryptedNonMountedUrl = tester.urlFor(handler).toString();
    assertFalse(encryptedNonMountedUrl.startsWith("wicket/bookmarkable/"));
    
    // Plain text URL should now return null page (CryptoMapper doesn't understand it)
    tester.executeUrl(plainTextNonMountedUrl);
    assertNull(tester.getLastRenderedPage());
    
    // Encrypted URL should work
    tester.executeUrl(encryptedNonMountedUrl);
    tester.assertRenderedPage(UnknownPage.class);
    
    // Now enforce mounts
    app.getSecuritySettings().setEnforceMounts(true);
    tester.executeUrl(plainTextNonMountedUrl);
    assertNull(tester.getLastRenderedPage());
    tester.executeUrl(encryptedNonMountedUrl);
    assertNull(tester.getLastRenderedPage());
    ```

  - **Example (incorrect)**:
    ```java
    // WRONG: Only testing enforceMounts=true without CryptoMapper, or only testing encrypted URL
    IRequestHandler handler = new BookmarkablePageRequestHandler(new PageProvider(UnknownPage.class));
    String url = tester.urlFor(handler).toString();
    
    app.setRootRequestMapper(new CryptoMapper(app.getRootRequestMapper(), app));
    app.getSecuritySettings().setEnforceMounts(true);
    
    tester.executeUrl(url);
    // assertNull(tester.getLastRenderedPage()); -- Missing! Also forgot dummy request after mapper change.
    ```
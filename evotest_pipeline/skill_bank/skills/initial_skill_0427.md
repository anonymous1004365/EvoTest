---
name: page-provider-stored-page-parameter-mismatch
description: When a PageProvider retrieves a stored page by ID, its PageParameters
  must also match the requested parameters — not just the class. Test that a stored
  page with matching class but different PageParameters is NOT reused and a fresh
  page is created instead.
code_tags:
- STATE_MUTATION
- STALE_PAGE_CLASS_CHECK
test_pattern: STATE_TEST
---

# page-provider-stored-page-parameter-mismatch

## Instructions

# PageProvider Stored Page Parameter Mismatch Detection

## Instructions

- WHEN the TG encounters code in `PageProvider` (or similar page caching/reuse logic) that retrieves a stored page by `pageId` and checks whether the stored page's class matches the requested `pageClass`
- THEN the TG should also test that **PageParameters match** — not just the class — before reusing a stored page. Specifically:
  - Store a page with specific `PageParameters` (e.g., `new PageParameters().set("key1", "value1")`)
  - Create a `PageProvider` with the same `pageId`, the same `pageClass`, but **different** `PageParameters` (e.g., `new PageParameters().set("key2", "value2")`)
  - Call `isNewPageInstance()` — it must return `true` (the stored page should NOT be reused because parameters differ)
  - Call `getPageInstance()` — it must return a **fresh page instance**, not the stored one
  - Verify the fresh page has the **new** PageParameters, not the old stored ones
- WHEN calling `isNewPageInstance()` the method may have a **side effect**: it may assign the stored page to `pageInstance` field even when it shouldn't. The TG must verify that when class matches but parameters differ, `pageInstance` remains `null` after `isNewPageInstance()` so that `getPageInstance()` creates a fresh page.
- WHEN testing with `TestMapperContext`, use `mapperContext.new TestPageProvider(pageId, renderCount)` and set `pageClass` and `pageParameters` via setters before calling `isNewPageInstance()` or `getPageInstance()`.
- AVOID the common pitfall of testing only class mismatch (different page class) — the bug is that **same class + same id but different parameters** also incorrectly reuses the stored page.
- AVOID assuming that `getPageParameters()` on the PageProvider returns the stored page's parameters — it should return the **requested** parameters when provided.

### Correct Example (what the test should look like)

```java
/**
 * https://issues.apache.org/jira/browse/WICKET-4488
 *
 * There is a stored page with id = 0, class Page1, and parameters {key1=value1}.
 * A following request to page1?0&key2=value2 should not use the stored page with id=0
 * because the requested and the found page parameters do not match.
 */
@Test
public void ignorePageFoundByIdIfItsClassMatchButPageParametersDont()
{
    TestMapperContext mapperContext = new TestMapperContext();

    // Store a page with specific parameters
    PageParameters storedParams = new PageParameters();
    storedParams.set("key1", "value1");
    Page page = new TestPage();
    page.getPageParameters().set("key1", "value1");
    mapperContext.getPageManager().touchPage(page);
    mapperContext.getPageManager().commitRequest();
    mapperContext.cleanSessionCache();

    // Create a PageProvider requesting same pageId, same class, but different parameters
    PageParameters requestedParams = new PageParameters();
    requestedParams.set("key2", "value2");
    PageProvider provider = mapperContext.new TestPageProvider(page.getPageId(), 0);
    provider.setPageClass(TestPage.class);
    provider.setPageParameters(requestedParams);

    // isNewPageInstance() should return true because parameters don't match
    boolean isNew = provider.isNewPageInstance();
    assertTrue("The stored page has different PageParameters, so it should NOT be reused", isNew);

    // getPageInstance() should return a fresh page with the new parameters
    IRequestablePage freshPage = provider.getPageInstance();
    assertNotNull("A fresh page should have been created", freshPage);
    assertEquals("Fresh page should have the requested parameters",
        "value2", freshPage.getPageParameters().get("key2").toString());
}
```

### Incorrect Example (what the TG might write — WRONG)

```java
// WRONG: Only tests class mismatch, not parameter mismatch
@Test
public void ignorePageFoundByIdIfItsClassMatchButPageParametersDont()
{
    TestMapperContext mapperContext = new TestMapperContext();
    Page page = new TestPage();
    mapperContext.getPageManager().touchPage(page);
    mapperContext.getPageManager().commitRequest();
    mapperContext.cleanSessionCache();

    // Only checking that a DIFFERENT class causes new page creation
    // Missing: same class + same id but DIFFERENT parameters should ALSO create new page
    PageProvider provider = mapperContext.new TestPageProvider(page.getPageId(), 0);
    provider.setPageClass(DifferentPage.class);  // different class — trivial case
    boolean isNew = provider.isNewPageInstance();
    assertTrue("Class doesn't match, so new instance needed", isNew);
}
```

### Common Pitfalls

- Testing only class mismatch — this misses the bug where same class but different parameters incorrectly reuses the stored page
- Forgetting that `isNewPageInstance()` has a side effect (it sets `pageInstance` field) — the TG must verify that when parameters differ, the side effect does NOT occur (pageInstance stays null)
- Not using `TestMapperContext.cleanSessionCache()` before testing — this ensures the stored page is deserialized from the store rather than being the same in-memory object
- Assuming the default `PageParameters()` (empty) and explicit empty `PageParameters()` are different — use distinct non-empty parameters to trigger the bug
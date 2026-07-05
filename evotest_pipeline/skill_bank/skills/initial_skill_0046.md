---
name: expired-page-processing-behavior
description: When mapping requests to bookmarkable pages, the system should properly
  handle expired page IDs by throwing PageExpiredException rather than conflicting
  with non-expired page assertions. Use this skill when testing page request mapping
  with expired and non-expired page scenarios.
code_tags:
- EXCEPTION_HANDLING
- STATE_MUTATION
- CONDITIONAL_BRANCH
test_pattern: EXCEPTION_TEST
---

# expired-page-processing-behavior

## Instructions

# Expired Page Processing Behavior

## Instructions

- WHEN the TG encounters code that processes bookmarkable page requests (e.g., `processHybrid` in `AbstractBookmarkableMapper`) and has logic that branches based on whether a page is expired or not (using `PageInfo` with an expired ID)
- THEN the TG should test that:
  1. Processing a page request with a non-null expired page ID (e.g., `new PageInfo(EXPIRED_ID)`) throws `PageExpiredException` when `shouldRecreateMountedPagesAfterExpiry()` returns `false`
  2. Processing a page request with a fresh page (no ID, `new PageInfo()`) succeeds without throwing any exception when `shouldRecreateMountedPagesAfterExpiry()` returns `false`
  3. These two test cases are separate — the expired-page test must NOT assert that non-expired pages work correctly in the same test scenario, because the processing logic may short-circuit differently for expired vs non-expired pages

- The test should use `Assert.assumeTrue(...)` or `@Assume` to ensure the mapper's `shouldRecreateMountedPagesAfterExpiry()` returns `false` before testing the expired page path (or mock the mapper to override this method to return `false`)

- **Common pitfalls to avoid**:
  - Do NOT test expired page processing and non-expired page processing in the same test method without isolating them — if the non-expired page path fails first (e.g., with an `AssertionError`), the test never reaches the `PageExpiredException` assertion
  - Do NOT assume that because a fresh page processes successfully, the expired page path will even be reached — the mapper may short-circuit or fail on an earlier condition for different page info states
  - Do NOT use `assertThrows` alone without separating the happy-path setup from the exception-expected path, as a pre-condition failure in the same method can mask the expected exception
  - Do NOT forget to use the correct exception class: `org.apache.wicket.protocol.http.PageExpiredException`

### Correct Example
```java
@Test
public void itFailsToProcessAnExpiredPageIfShouldNotRecreateMountedPagesAfterExpiry()
{
    AbstractBookmarkableMapper mapper = new AbstractBookmarkableMapper()
    {
        @Override
        protected boolean shouldRecreateMountedPagesAfterExpiry()
        {
            return false;
        }
    };
    assertThrows(PageExpiredException.class, () -> {
        mapper.processHybrid(new PageInfo(EXPIRED_ID), MockPage.class, null, NOT_RENDERED_COUNT);
    });
}
```

### Incorrect Example
```java
// BAD: Tests both expired and non-expired in the same method without isolation
@Test
public void testHybridProcessing()
{
    AbstractBookmarkableMapper mapper = ...;
    // This assertion might fail first, masking the PageExpiredException test
    Assert.assertNotNull(mapper.processHybrid(new PageInfo(), EmptyPage.class, null, 0));
    assertThrows(PageExpiredException.class, () -> {
        mapper.processHybrid(new PageInfo(EXPIRED_ID), MockPage.class, null, NOT_RENDERED_COUNT);
    });
}
```
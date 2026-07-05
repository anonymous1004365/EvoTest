---
name: stateless-page-bookmarkable-check
description: When a page is annotated with @StatelessComponent, the StatelessChecker
  validates it must be bookmarkable. This skill teaches testing that non-bookmarkable
  @StatelessComponent pages throw StatelessCheckFailureException with the message
  "Only bookmarkable pages can be stateless".
code_tags:
- STATEFUL_COMPONENT_CHECK
- BOOKMARKABLE_PAGE_VALIDATION
test_pattern: EXCEPTION_TEST
---

# stateless-page-bookmarkable-check

## Instructions

# Stateless Page Bookmarkable Check

## Instructions

**WHEN** the TG encounters a `Page` subclass annotated with `@StatelessComponent` (e.g., `org.apache.wicket.devutils.stateless.StatelessComponent`) that is NOT bookmarkable (i.e., the page class does not have a corresponding bookmarkable page mapping in the application),

**THEN** the TG should write a test that:
1. Creates a `WicketTester` instance.
2. Creates a `StatelessChecker` instance (from `org.apache.wicket.devutils.stateless.StatelessChecker`).
3. Adds the checker to the application's `ComponentPostOnBeforeRenderListeners`: `tester.getApplication().getComponentPostOnBeforeRenderListeners().add(checker);`
4. Calls `tester.startPage(NonBookmarkablePage.class)` inside a try-catch block.
5. Asserts that the caught exception is a `StatelessCheckFailureException` with message containing `"Only bookmarkable pages can be stateless"`.
6. Asserts that the component class of the exception is the non-bookmarkable page class.

**Concrete details:**
- The exception class is `org.apache.wicket.devutils.stateless.StatelessCheckFailureException`.
- The failure message format for non-bookmarkable pages is: `"'[Page class = <PageClass>, id = 0, render count = 1]' claims to be stateless but isn't. Only bookmarkable pages can be stateless"`.
- The `StatelessCheckFailureException` has a method `getComponent()` that returns the `Component` that failed the check. Use `ex.getComponent().getClass()` to assert the expected page class.
- To create a non-bookmarkable page, extend `org.apache.wicket.util.tester.DummyHomePage` (a simple page class available in wicket-core test fixtures) with `@StatelessComponent` annotation: `@StatelessComponent public static class StatelessPage extends DummyHomePage {}`.

**Also verify the "quiet" variant:** Test with a `StatelessChecker` subclass that overrides `protected void fail(StatelessCheckFailureException e)` to store the exception instead of throwing it. This tests that the same validation logic applies even when the checker uses the non-throwing override:
1. Create a subclass that stores the exception in a field.
2. Call `startPage()` — no exception should be thrown.
3. Retrieve the stored exception via a getter method.
4. Assert the same message and component class.

**Common pitfalls to avoid:**
- ❌ Testing only with a page that IS bookmarkable (positive test) — the bug is specifically about non-bookmarkable pages being silently accepted.
- ❌ Forgetting to add the checker to `ComponentPostOnBeforeRenderListeners` — the checker only runs when registered.
- ❌ Using a page that is bookmarkable by default — `DummyHomePage` is not bookmarkable, which is why it triggers the bug.
- ❌ Not checking the exception message content to distinguish between different failure modes (stateful behaviors vs. non-bookmarkable vs. unknown stateless reason).
- ❌ Testing only the throwing (`fail` method throws) variant without also testing the quiet (overridden `fail` stores exception) variant.

**Correct example:**
```java
@Test
public void testNonBookmarkablePage()
{
    try
    {
        tester.getApplication().getComponentPostOnBeforeRenderListeners().add(checker);
        tester.startPage(StatelessPage.class);
        fail("Expected tester.startPage() to fail with StatelessCheckFailureException");
    }
    catch (StatelessCheckFailureException ex)
    {
        assertTrue(ex.getMessage().contains("Only bookmarkable pages can be stateless"));
        assertEquals(StatelessPage.class, ex.getComponent().getClass());
    }
}

@Test
public void testNonBookmarkablePageQuietly()
{
    tester.getApplication().getComponentPostOnBeforeRenderListeners().add(checkerQuietly);
    tester.startPage(StatelessPage.class);
    StatelessCheckFailureException ex = checkerQuietly.getFailureException();
    assertTrue(ex.getMessage().contains("Only bookmarkable pages can be stateless"));
    assertEquals(StatelessPage.class, ex.getComponent().getClass());
}
```

**Incorrect example (would miss the bug):**
```java
// Only tests a bookmarkable page — won't catch the non-bookmarkable bug
@Test
public void testPositive()
{
    tester.getApplication().getComponentPostOnBeforeRenderListeners().add(checker);
    tester.startPage(BookmarkablePage.class);
    // No assertion — silently passes even when non-bookmarkable pages are broken
}
```
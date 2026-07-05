---
name: border-body-container-parent-after-removal
description: When testing Border subclasses that remove their body container during
  onRender, verify getBodyContainer().getParent() is null after removal. This catches
  NullPointerException bugs caused by accessing detached components during rendering.
code_tags:
- ARGUMENT_VALIDATION
- BOUNDARY_CHECK
- STATE_MUTATION
test_pattern: STATE_TEST
---

# border-body-container-parent-after-removal

## Instructions

# Border Body Container Parent After Removal

## Instructions

- WHEN the TG encounters a `Border` subclass that removes its body container (via `remove()`, `replace()`, or `setParent(null)`) inside `onRender()` or `onComponentTagBody()` 
- THEN the TG should write a test that renders the border and then verifies that `border.getBodyContainer().getParent()` is `null` after rendering
- The test should render the page containing the border (e.g., via `tester.startPage(page)`) and then assert that `getBodyContainer().getParent()` returns `null`
- The test should also verify that rendering does not throw a `NullPointerException` — if the fix is missing, a `NullPointerException` will occur when the framework tries to walk the component hierarchy after the body container has been detached without clearing its parent
- Common pitfalls:
  - Testing only that rendering succeeds without asserting the null parent state — this passes even if the parent reference is stale
  - Asserting that `getBodyContainer()` itself is null — the body container still exists, it's just detached from the hierarchy
  - Testing visibility changes only (e.g., `setVisible(false)`) without actually calling `remove()` — different code paths with different bugs

### Correct Example (would catch this bug)

```java
@Test
public void hideableBorder() throws Exception
{
    HideableBorderPage page = new HideableBorderPage();
    tester.startPage(page);

    // After rendering, the body container should have no parent
    // because it was removed during onRender
    assertNull("body container must have no parent after rendering", 
        page.getBorder().getBodyContainer().getParent());
}
```

### Incorrect Example (would miss this bug)

```java
@Test
public void hideableBorder() throws Exception
{
    HideableBorderPage page = new HideableBorderPage();
    tester.startPage(page);
    
    // WRONG: Only testing that rendering doesn't throw
    // This doesn't catch the stale parent reference
    assertTrue(tester.isValid());
    
    // WRONG: Testing the wrong thing
    // assertNotNull("body container must still exist", 
    //     page.getBorder().getBodyContainer());
}
```
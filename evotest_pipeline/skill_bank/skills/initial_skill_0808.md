---
name: re-added-component-same-id
description: When a Test Generator encounters components that are removed and re-added
  with the same component ID, they should test re-attachment lifecycle — ensuring
  the re-added component works correctly without stale state or initialization failures
  from the previous attachment.
code_tags:
- STATE_MUTATION
- ORDER_DEPENDENCY
test_pattern: STATE_TEST
---

# re-added-component-same-id

## Instructions

# Re-Added Component With Same ID

## Instructions

- WHEN the TG encounters a component that is detached/removed from a parent and then re-added to the same (or different) parent with the **same component ID** (e.g., `new FencedFeedbackPanel("id")` → remove → `new FencedFeedbackPanel("id")` again)
- THEN the TG should write a **state test** that:
  1. Creates the component, adds it to a parent/container
  2. Removes the component from the parent (or replaces it)
  3. Creates a **new instance** of the same component class with the **same ID**
  4. Adds the new instance back to the parent
  5. Verifies that the re-added component works correctly — e.g., renders, responds to feedback messages, does not throw `NullPointerException`
  6. Expects that the **buggy version** may throw a `NullPointerException` or produce incorrect output (empty/null) when the component is re-added, while the **fixed version** works normally

- **Common pitfalls to avoid**:
  - Testing only the first addition of a component without testing re-adding with the same ID
  - Assuming that removing and re-adding a component is always safe
  - Not checking that the re-added component's internal state is properly re-initialized
  - Testing only static/stateless components — this bug is specific to components with internal mutable state (like feedback collectors, message caches)

**Correct example** (Java/JUnit):
```java
@Test
void testReAddingFencedFeedbackPanel()
{
    // First addition works
    FencedFeedbackPanel panel = new FencedFeedbackPanel("feedback");
    Page page = new MyPage();
    page.add(panel);
    // ... use panel ...
    
    // Remove it
    page.remove(panel);
    
    // Re-add a NEW instance with the SAME ID
    FencedFeedbackPanel reAddedPanel = new FencedFeedbackPanel("feedback");
    page.add(reAddedPanel);
    
    // Verify re-added panel works without NullPointerException
    assertNotNull(reAddedPanel.getFeedbackMessages());
    // or: tester.startPage(page); assertNoError();
}
```

**Incorrect example** (does not exercise the bug):
```java
@Test
void testFencedFeedbackPanel()
{
    // Only tests first addition — misses the re-add bug
    FencedFeedbackPanel panel = new FencedFeedbackPanel("feedback");
    page.add(panel);
    assertNotNull(panel.getFeedbackMessages());
}
```
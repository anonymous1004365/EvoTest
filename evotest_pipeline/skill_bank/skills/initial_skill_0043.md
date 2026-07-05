---
name: component-markup-id-generation-for-unattached-components
description: WHEN a Component class lazily generates a markup ID using a flag-based
  mechanism that checks whether the component is attached to a Page, THEN the TG should
  test that methods like getMarkupId() return a valid non-null ID even when the component
  has never been added to a page, and that getMarkupId(false) returns null in that
  state.
code_tags:
- NULL_CHECK
- STATE_MUTATION
- CHILD_REMOVAL
test_pattern: STATE_TEST
---

# component-markup-id-generation-for-unattached-components

## Instructions

# Component Markup ID Generation for Unattached Components

## Instructions

**WHEN** encountering a `Component` class (or similar hierarchical component framework) that has:
- A `getMarkupId(boolean createIfDoesNotExist)` method with a branch that checks whether the component is attached to a parent/page (e.g., checking a flag like `FLAG_ID` or `findParent(Page.class)`)
- A lazy-generation strategy where a markup ID is either obtained from markup or auto-generated
- A `getMarkupIdImpl()` method that returns an `Object` (which can be `null`)

**THEN** the TG should write a test that:

1. **Creates a component WITHOUT adding it to a page** — e.g., `new Label("id", "value")` with no `Page` attachment.
2. **Calls `getMarkupId()`** (which internally uses `createIfDoesNotExist=true`) and **asserts that the return value is non-null** — the buggy version would throw a `NullPointerException` because `getMarkupIdImpl()` returns `null` for unattached components, and the code does not auto-generate an ID.
3. **Calls `getMarkupId(false)`** and **asserts that the return value is `null`** — confirming that no ID is available when creation is suppressed.
4. **Verifies that both calls complete WITHOUT throwing any exception** — catching `NullPointerException`, `IllegalStateException`, or any other unchecked exception.

**Common Pitfalls to Avoid:**
- ❌ Testing only with the component attached to a page, which never exercises the unattached branch.
- ❌ Assuming `getMarkupId()` always returns a non-null value from `getMarkupIdImpl()` — when the component is unattached, the implementation may return `null`, requiring a fallback generation.
- ❌ Not testing both `getMarkupId(true)` (via `getMarkupId()`) and `getMarkupId(false)` separately, since they exercise different code paths.
- ❌ Testing only `getMarkupId()` and missing that `getMarkupId(false)` should return `null` (regression risk).
- ❌ Adding the component to a dummy `Page` or calling any attachment lifecycle methods before the test — this masks the bug.

**Example of a correct test (Java, JUnit 4):**
```java
@Test
public void idGeneratedWhenComponentNotAddedToPage()
{
    Component component = new Label("componentId", "value");
    // Component was never added to a Page
    
    // getMarkupId() uses createIfDoesNotExist=true — must not throw
    String markupId = component.getMarkupId();
    assertNotNull("Markup ID must not be null for unattached component when creation is requested", markupId);

    // getMarkupId(false) — must return null, no ID available
    assertNull("Markup ID must be null when creation is not requested for unattached component", component.getMarkupId(false));
}
```

**Example of an incorrect test (would NOT catch the bug):**
```java
@Test
public void idGeneratedWhenComponentAddedToPage()
{
    // Adding the component to a page masks the unattached bug
    Page page = new MyPage();
    Component component = new Label("componentId", "value");
    page.add(component);
    
    assertNotNull(component.getMarkupId());  // Always passes because FLAG_ID is set
}
```
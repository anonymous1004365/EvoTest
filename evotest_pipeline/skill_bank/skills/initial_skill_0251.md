---
name: vetoed-component-onbeforerender-skip
description: WHEN a component's onBeforeRender triggers authorization that vetoes/rejects
  child rendering and removes children from the parent, THEN test that removed children
  do NOT have onBeforeRender called on them. This skill catches bugs where state mutation
  (child removal) during tree traversal is not properly respected and the component
  tree continues rendering removed children.
code_tags:
- COMPONENT_TREE_NAVIGATION
- CHILD_REMOVAL
- STATE_MUTATION
test_pattern: STATE_TEST
---

# vetoed-component-onbeforerender-skip

## Instructions

# Vetoed Component: onBeforeRender Skip After Child Removal

## Instructions

### WHEN the TG encounters code where:
- A component's `onBeforeRender()` (or similar lifecycle method) triggers an authorization check (e.g., `isActionAuthorized()` for RENDER action) that can **veto/reject** child rendering
- A **parent container** calls `remove(childComponent)` or similar during rendering/traversal when authorization fails
- The component tree continues traversal after removal

### THEN the TG should:

1. **Create a test that verifies a removed/vetoed child component does NOT have its lifecycle methods called**
   - Create a custom `IAuthorizationStrategy` (or equivalent) that returns `false` for `isActionAuthorized(component, action)` for specific child components
   - Attach a spy/flag (e.g., an `onBeforeRender()` override that sets a boolean flag) to the child component to detect if it was rendered
   - After rendering the parent page/container, assert that the removed child's `onBeforeRender()` was **NOT** called

2. **Use concrete types from the codebase:**
   - Authorization strategy interface: `org.apache.wicket.authorization.IAuthorizationStrategy`
   - Action class: `org.apache.wicket.authorization.Action` (use `Action.RENDER`)
   - Component class: `org.apache.wicket.Component`
   - Test framework: WicketTester (or equivalent)

3. **Verify the specific behavior:**
   - When a child is removed from its parent due to authorization veto, the child should be skipped in the remaining render traversal
   - Check that the child's `onBeforeRender()` never executes

### Common pitfalls to avoid:
- ❌ Testing only that `remove()` is called — the bug is that **after** removal, traversal continues and calls `onBeforeRender()` on the removed child anyway
- ❌ Using `isVisible()` or visibility checks instead of actual `remove()` — the bug specifically involves child **removal** (detachment from parent)
- ❌ Not clearing the `beforeRender` phase flag on removed children — the fix should clear the phase so the removed component appears as if it was never traversed
- ❌ Testing with only one level of component hierarchy — the bug manifests when parent renders, removes children mid-traversal, and then later calls `onBeforeRender()` on the already-removed child

### Example test pattern (correct):

```java
@Test
public void onBeforeRenderNotCalledOnVetoedComponents()
{
    // Create a page with a container that has children
    TestPage page = new TestPage();
    
    // Flag to detect if child's onBeforeRender was called
    final boolean[] childRendered = {false};
    
    // Add a child that veto-removes its sibling
    page.add(new TestComponent("child1") {
        @Override
        public void onBeforeRender() {
            // This child's parent will have authorization that 
            // vetoes child2 and removes it
            super.onBeforeRender();
        }
    });
    
    // Child that should NOT be rendered
    page.add(new TestComponent("child2") {
        @Override
        public void onBeforeRender() {
            childRendered[0] = true; // This should NOT happen
            super.onBeforeRender();
        }
    });
    
    // Set up authorization strategy that vetoes child2 RENDER action
    // This causes child2 to be removed from its parent
    
    // Render the page
    tester.startPage(page);
    
    // Verify child2's onBeforeRender was NOT called
    assertFalse("Removed component should not have onBeforeRender called", childRendered[0]);
}
```

### Incorrect test pattern (won't catch the bug):

```java
// ❌ BAD: Only checks that remove() was called, doesn't verify
// that onBeforeRender is skipped for the removed component
@Test
public void testRemoval() {
    // ... setup ...
    assertTrue(child.isRemoved()); // This passes even if onBeforeRender was called
}
```
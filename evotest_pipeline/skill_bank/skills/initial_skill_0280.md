---
name: component-stateless-hint-override
description: Teaches how to test that stateful components (with stateful behaviors
  or own getStatelessHint=false) may pretend to be stateless when invisible/disabled
  AND they cannot call listeners. Use when testing isStateless() logic intertwined
  with canCallListener().
code_tags:
- COMPONENT_TREE_NAVIGATION
- STATE_MUTATION
test_pattern: STATE_TEST
---

# component-stateless-hint-override

## Instructions

# Component Stateless Hint Override

## Instructions

- WHEN testing `Component.isStateless()` (e.g., `org.apache.wicket.Component.isStateless()`)
- THEN verify that a component:
  1. Starts stateless by default: `assertTrue(component.isStateless())`
  2. Becomes stateful when a behavior returns `false` from `getStatelessHint()`:  
     `component.add(behavior); assertFalse(component.isStateless())`
  3. Can pretend to be stateless when invisible (`setVisible(false)`) AND `canCallListener()` returns `false`:  
     `assertTrue(component.isStateless())`
  4. Can pretend to be stateless when disabled (`setEnabled(false)`) AND `canCallListener()` returns `false`:  
     `assertTrue(component.isStateless())`
  5. Must NOT pretend to be stateless when invisible/disabled BUT `canCallListener()` is overridden to return `true`:  
     Override `canCallListener()` to return `true`, set invisible, `assertFalse(component.isStateless())`
- WHEN the component is inherently stateful (e.g., `Link` returns `false` from its own `getStatelessHint()`)
- THEN apply the same logic: invisible/disabled makes it pretend stateless only if `canCallListener()` returns `false`; override `canCallListener()` to `true` and it stays stateful.

- Common pitfall: Asserting that invisible/disabled always makes a component isStateless=true. This is WRONG — the component must also have `canCallListener() == false`. If a component overrides `canCallListener()` to return `true`, it remains stateful even when invisible/disabled.
- Common pitfall: Testing only behavior-based statefulness. Also test components that are inherently stateful by their own `getStatelessHint()` (e.g., `Link`).
- Common pitfall: Forgetting to test both `setVisible(false)` and `setEnabled(false)` as separate cases.

### Correct Example (from the bug-fixing test):
```java
@Test
public void isStateless()
{
    Behavior statefulBehavior = new Behavior() {
        @Override
        public boolean getStatelessHint(Component component) {
            return false;
        }
    };

    WebComponent component = new WebComponent("someId");
    assertTrue(component.isStateless());

    component.add(statefulBehavior);
    assertFalse(component.isStateless());

    component.setVisible(false);
    assertTrue(component.isStateless());

    component.setVisible(true).setEnabled(false);
    assertTrue(component.isStateless());

    component = new WebComponent("someId") {
        @Override
        public boolean canCallListener() {
            return true;
        }
    };
    component.add(statefulBehavior);
    component.setVisible(false);
    assertFalse(component.isStateless());

    // Also test inherently stateful component (Link)
    Link<Void> link = new Link<Void>("someId") {
        @Override
        public void onClick() {}
    };
    assertFalse(link.isStateless());

    link.setVisible(false);
    assertTrue(link.isStateless());

    link.setVisible(true).setEnabled(false);
    assertTrue(link.isStateless());

    link = new Link<Void>("someId") {
        @Override
        public boolean canCallListener() {
            return true;
        }
        @Override
        public void onClick() {}
    };
    link.setVisible(false);
    assertFalse(link.isStateless());
}
```

### Incorrect Example (missing the canCallListener override case):
```java
@Test
public void isStateless() {
    WebComponent component = new WebComponent("someId");
    component.add(statefulBehavior);
    component.setVisible(false);
    assertTrue(component.isStateless()); // Might pass but misses the case where canCallListener=true
}
```

### What the test should verify on the buggy version
The buggy `isStateless()` implementation fails to check `canCallListener()` before allowing a component to pretend stateless when invisible/disabled. The test verifies that when `canCallListener()` returns `true`, an invisible component correctly remains stateful (`assertFalse`). On the buggy version without the fix, the last `assertFalse` assertions would incorrectly return `true` instead of `false`.
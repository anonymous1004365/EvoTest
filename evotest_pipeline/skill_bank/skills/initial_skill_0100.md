---
name: constructor-child-access-before-parent-assignment
description: When a component's constructor calls methods (like toString()) that access
  parent-dependent state (e.g., markup resolution), the TG must test that calling
  such methods from within the constructor works or throws a meaningful exception.
  The component is not yet connected to a parent during construction.
code_tags:
- CONSTRUCTOR_BODY_EMPTINESS
- STATE_MUTATION
test_pattern: EXCEPTION_TEST
---

# constructor-child-access-before-parent-assignment

## Instructions

# Constructor Child Access Before Parent Assignment

## Instructions

- WHEN the TG encounters a Java class that calls `this.toString()` or any method relying on parent container state (e.g., `getMarkup()`, `findParent()`, `getParent()`) from within its own constructor body before `super(...)` completes or before the component is added to a parent container:
  - THEN the TG should write a test that instantiates the component directly (without adding it to any parent) and calls the method that was invoked inside the constructor (e.g., `toString()`), expecting either a meaningful exception or a graceful fallback (e.g., a default string representation).
  - The test must verify that the buggy version throws an exception like `"Can not determine Markup. Component is not yet connected to a parent."` or similar state-dependent error, while the fixed version produces a safe default (e.g., `[ToStringComponent [Component id = id]]` without throwing).
  - Include concrete examples: create component subclass that calls `toString()` in its constructor and test it standalone.
  - Common pitfalls to avoid:
    - Testing only after the component has been added to a parent container — this masks the bug.
    - Assuming `toString()` or other introspection methods are safe to call at any lifecycle stage.
    - Not checking the exception message content to distinguish between real bugs and expected lifecycle limitations.

- Correct test pattern (for the fixed version):
```java
@Test
public void callToStringFromConstructor()
{
    // Component is NOT added to any parent — simulates what happens during construction
    ToStringComponent component = new ToStringComponent("id");
    // Should NOT throw; should return a safe default string
    assertNotNull(component.toString());
}
```

- Incorrect test pattern (would miss the bug):
```java
@Test
public void callToStringFromConstructor()
{
    // Adding to parent masks the lifecycle issue
    MarkupContainer parent = new MarkupContainer("parent");
    ToStringComponent component = new ToStringComponent("id");
    parent.add(component);
    // This always works because component now has a parent
    assertEquals("expected", component.toString());
}
```
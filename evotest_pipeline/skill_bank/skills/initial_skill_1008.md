---
name: assignment-wrapper-detach-delegation
description: When a model's wrapOnAssignment(Component) creates an inner wrapper that
  extends LoadableDetachableModel, its detach() must delegate back to the outer model.
  Test that detaching the wrapper does not hold references to assigned models after
  detachment.
code_tags:
- WRAP_ON_ASSIGNMENT
- DETACH_DELEGATION
test_pattern: STATE_TEST
---

# assignment-wrapper-detach-delegation

## Instructions

# AssignmentWrapper Must Properly Detach By Delegating Back to Outer Model

## Instructions

- WHEN the TG encounters a `wrapOnAssignment(Component)` method that returns an inner class (e.g., `AssignmentWrapper`) extending `LoadableDetachableModel<String>`
- THEN the TG should verify that calling `detach()` on the `AssignmentWrapper` properly delegates back to the outer model's `detach()` method, such that the outer model's substitute models are also detached
- Specifically, set a substitute model on the `StringResourceModel` (using e.g. `setModel()`), assign it to a component (which triggers `wrapOnAssignment`), detach the component, then assert that the substitute model returns `null` from its `getObject()`
- Use a concrete model subclass (e.g., an inner static class extending `AbstractPropertyModel` or `IModel`) that holds a reference, and verify that reference is cleared after detach
- Common pitfall: testing only that the wrapper's `getObject()` returns a value, without testing that `detach()` on the wrapper (or owning component) properly nullifies the substitute model's reference
- Correct approach: The test should call `component.detach()`, then check that the substitute model's wrapped object is null (the substitute model was detached)
- Incorrect approach: Testing only that the wrapper's `getObject()` works before detach, or testing detach only on the outer model directly without going through the wrapper/component chain

### Example (Correct test pattern):
```java
// WeatherStation extends AbstractPropertyModel with an Object target
IModel<String> substitute = new AbstractPropertyModel<Object>(weatherStation) {
    public String getObject() { return target.toString(); }
    @Override
    public void detach() { target = null; }
};
StringResourceModel srm = new StringResourceModel("key", this).setModel(substitute);
Component c = new Label("id", srm);
c.detach(); // triggers AssignmentWrapper.detach() which must delegate
assertNull(substitute.getObject()); // fails on buggy: substitute still references weatherStation
```

### Example (Incorrect test pattern):
```java
// Only testing wrapper's getObject(), no detach verification
IModel<String> substitute = ...
StringResourceModel srm = new StringResourceModel("key", this).setModel(substitute);
Component c = new Label("id", srm);
assertNotNull(c.getDefaultModelObjectAsString());
// BUG: missing c.detach() + assertNull(substitute.getObject())
```
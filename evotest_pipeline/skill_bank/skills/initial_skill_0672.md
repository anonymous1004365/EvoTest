---
name: reset-flag-on-model-change
description: When a component has a bit flag that caches whether its model is "inheritable",
  the flag must be reset whenever the model is changed. Test that after setting a
  non-inheritable model on a previously inheritable component, the flag is properly
  cleared.
code_tags:
- VALIDATION
- STATE_MUTATION
- FLAG_BIT_OPERATION
test_pattern: STATE_TEST
---

# reset-flag-on-model-change

## Instructions

# Reset Flag on Model Change

## Instructions

- WHEN the TG encounters a Component class that uses a non-zero integer bit flag (e.g., `static final int FLAG_INHERITABLE_MODEL = 0x0004`) to cache whether its model is "inheritable" (i.e., the model is an instance of `IInheritableModel`), and this flag is stored via `setFlag(FLAG, boolean)` and checked via `getFlag(FLAG)` in methods like `getDefaultModel()` or `onDetach()`:
  - THEN the TG MUST write a test that verifies the flag is reset when the model is changed via `setDefaultModel()` or `setDefaultModelObject()`.
  - The test should:
    1. Create a component (e.g., a `Label`, `TextField`, etc.) with an inheritable model (e.g., `Model.of("foo")` wrapped in something that implements `IInheritableModel`, or use a `CompoundPropertyModel`).
    2. Change the model to a NON-inheritable model (e.g., a plain `Model.of("bar")`).
    3. Verify that after the change, the component returns the new model's value — NOT the old inheritable model's value. This catches the case where the stale flag causes the component to still delegate to the parent model.
  - The test should assert an explicit expected value on the component's rendered output (e.g., via `tester.startComponentInPage()` or `Component#getDefaultModelObjectAsString()`), comparing the result before and after the model change.
  - Common pitfall: Testing only that `setDefaultModel()` does not throw or that the model reference changed, but NOT testing that the **rendered output** or **behavior** reflects the model change. The bug manifests as incorrect behavior (wrong value returned) due to a stale flag, not a crash.
  - Another common pitfall: Assuming that if the flag is defined, it is always correctly maintained. The TG should specifically test the **transition** from inheritable → non-inheritable model, which is where the bug lives.

### Example (correct approach — catches the bug):

```java
// A component with an inheritable model (e.g., CompoundPropertyModel)
// Changing to a plain Model should work
Component comp = new Label("id", new CompoundPropertyModel<>(new Model<>("foo")));
tester.startComponentInPage(comp);
// Now change to non-inheritable model
comp.setDefaultModel(Model.of("bar"));
tester.startComponentInPage(comp);
tester.assertLabel("id", "bar"); // FAILS on buggy version — returns "foo"
```

### Example (incorrect approach — misses the bug):

```java
// Only tests the initial state
Component comp = new Label("id", Model.of("bar"));
tester.startComponentInPage(comp);
tester.assertLabel("id", "bar");
// Never transitions FROM inheritable TO non-inheritable
```
---
name: inherited-model-flag-reset-on-model-change
description: When a component's model is changed, the FLAG_INHERITABLE_MODEL flag
  must be reset to false so the new model is not accidentally replaced by an inherited
  model on subsequent requests. Use this skill when testing components that use inherited
  models and the setDefaultModel() or setDefaultModelObject() methods.
code_tags:
- STATE_MUTATION
- INHERITANCE_CHECK
test_pattern: STATE_TEST
---

# inherited-model-flag-reset-on-model-change

## Instructions

# Inherited Model Flag Reset on Model Change

## Instructions

- WHEN the TG encounters a Wicket Component that has `FLAG_INHERITABLE_MODEL` (0x0004) and the component uses `setDefaultModel(IModel<?>)` or `setDefaultModelObject(Object)` to change the model after the component was already rendered
- THEN the TG should write a test that:
  1. Creates a component (e.g., a Label or custom Component subclass) with an initial model
  2. Calls `component.setDefaultModel(newSomeModel(...))` on the component to change the model
  3. Calls `component.getDefaultModel()` and asserts that it returns the new model (not the old one)
  4. The test must verify the component's internal flag `FLAG_INHERITABLE_MODEL` is properly reset so that on the next render/prepareForRender cycle the new model is not discarded
- The concrete assertion should check that after `setDefaultModel(model)` is called, `component.getDefaultModel() == newModel` (the newly set model, not some inherited model from a parent or previous render)
- Common pitfalls:
  - Not testing that the FLAG_INHERITABLE_MODEL is reset — the flag might remain set after a model change, causing the new model to be overwritten by inherited model lookup during the next render
  - Testing only with non-inheritable models — the bug manifests specifically when the component previously had an inheritable model flag set and then the model is changed
  - Testing only the constructor-injected model but not the runtime model change path

### Example (correct)

```java
// Test that setDefaultModel resets the FLAG_INHERITABLE_MODEL
Component component = new Label("id", "initial");
component.setDefaultModel(Model.of("new value"));
assertEquals("Component should return the newly set model", 
    "new value", component.getDefaultModelObject());
```

### Example (incorrect/pitfall)

```java
// INCORRECT: Only tests constructor model, doesn't test runtime model change
Component component = new Label("id", "initial");
assertEquals("initial", component.getDefaultModelObject());
// No test for setDefaultModel after component was rendered
```
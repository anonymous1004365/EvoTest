---
name: on-validate-model-objects-form-hierarchy
description: Teaches the TG to test the `onValidateModelObjects()` lifecycle callback
  in `Form` subclasses, specifically when container traversal collects child components
  and mutates their model state. The bug occurs when a `Form` subclass overrides `onValidateModelObjects()`
  and its implementation differs from what the framework expects for proper model
  validation across nested forms and panels.
code_tags:
- SUBCLASS_CALLBACK
- CONTAINER_TRAVERSAL
- STATE_MODIFICATION
- STATE_MUTATION
test_pattern: INTERACTION_TEST
---

# on-validate-model-objects-form-hierarchy

## Instructions

# OnValidateModelObjects Form Hierarchy Test

## Instructions

**WHEN** the TG encounters a `Form` subclass that overrides `onValidateModelObjects()`, or when the test interacts with nested `Form` components within panels/containers:

- **THEN** the TG should verify that the `onValidateModelObjects()` method is called at the correct point in the form lifecycle and that all child components' models are properly visited/validated.
- **THEN** the TG should create a test that:
  1. Creates a `Form` subclass (or uses an anonymous/inner class) that overrides `onValidateModelObjects()`.
  2. Adds child components with `CompoundPropertyModel` or custom models to the form.
  3. Calls `form.visitChildren(FormComponent.class, ...)` or directly calls `form.onValidateModelObjects()` to trigger the traversal.
  4. Asserts that the model objects of all child `FormComponent`s were validated (e.g., by checking model state flags or verifying `getModelObject()` was called).
- **THEN** if the form contains nested forms or panels with forms, the TG should test that `onValidateModelObjects()` is recursively called through the entire component hierarchy, not just direct children.
- **THEN** the TG should verify that calling `onValidateModelObjects()` does not cause a `NullPointerException` when child components have `null` model objects, and that the form gracefully handles components that are not `FormComponent` instances.

**Common pitfalls:**
- Only testing `onValidateModelObjects()` on simple forms with no child hierarchy — the bug manifests when nested forms/panels are involved.
- Assuming that `onValidateModelObjects()` only processes direct children — the method should traverse the entire component tree.
- Not testing the interaction between a `Form`'s override and the `super.onValidateModelObjects()` call — the bug might be in how the super call interacts with child traversal.
- Forgetting to check that `onValidateModelObjects()` is called during the form's normal validation flow (e.g., during `process()`), not just when called directly.

**Correct example:**
```java
// Test that onValidateModelObjects traverses all form components
Form<?> form = new Form<Void>("form") {
    @Override
    protected void onValidateModelObjects() {
        super.onValidateModelObjects();
        // Additional custom logic
    }
};
TextField<String> field1 = new TextField<>("field1", Model.of("value1"));
TextField<String> field2 = new TextField<>("field2", Model.of("value2"));
form.add(field1);
form.add(field2);
form.onValidateModelObjects(); // Should process both fields without exception
```

**Incorrect example:**
```java
// Missing: Not testing with nested panels or multi-level form hierarchy
// Not verifying that model objects are actually accessed/validated
Form<?> form = new Form<Void>("form") { ... };
// Only adding components but never calling onValidateModelObjects
// or checking that it works with compound property models
```
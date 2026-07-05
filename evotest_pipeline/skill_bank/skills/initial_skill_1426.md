---
name: model-change-null-detection
description: When a component has a setter that calls modelChanging() before setting
  a null model, a subsequent getDefaultModelObject() may throw NullPointerException.
  This skill teaches how to test that model change events are properly handled even
  when the model is set to null.
code_tags:
- NULL_CHECK
- STATE_MUTATION
- VALIDATION
test_pattern: STATE_TEST
---

# model-change-null-detection

## Instructions

# Model Change Null Detection

## Instructions

- WHEN the TG encounters a class that has a `setDefaultModel(IModel<?>)` method which calls `modelChanging()` — potentially followed by a NullPointerException when `getDefaultModelObject()` is later called after setting a null model
- THEN the TG should test that setting a component's model to a new value, then setting the default model object, correctly fires model change events (like `modelChanged()`) and that `getDefaultModelObject()` returns the expected value without throwing a NullPointerException
- Include tests that verify `setDefaultModelObject()` works correctly after `setDefaultModel()` has been called, especially when the model is a simple `Model<T>` object
- Common pitfalls: testing only with non-null model objects and forgetting that setting the model via `setDefaultModel()` and then setting its object via `setDefaultModelObject()` should leave the component in a consistent state where `getDefaultModelObject()` returns the newly set value

### Example

```java
// Correct test — verifies that model change works correctly after setDefaultModel + setDefaultModelObject
Component component = new ComponentUnderTest();
component.setDefaultModel(new Model<>("initial"));
component.setDefaultModelObject("changed");
assertEquals("changed", component.getDefaultModelObject());
```

```java
// Incorrect test — only tests setDefaultModelObject in isolation without setDefaultModel first
Component component = new ComponentUnderTest();
component.setDefaultModelObject("value");
assertEquals("value", component.getDefaultModelObject());
// This misses the bug: after setDefaultModel(new Model<>()), setDefaultModelObject() may throw NPE
```
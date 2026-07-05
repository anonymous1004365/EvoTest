---
name: collection-model-update-null-handling
description: When testing static methods like FormComponent.updateCollectionModel()
  that update a Collection model object, the TG should test scenarios where the model
  returns null and the converted input is null, ensuring no NullPointerException occurs.
  This skill focuses on null-safety in collection model update flows.
code_tags:
- NULL_CHECK
test_pattern: STATE_TEST
---

# collection-model-update-null-handling

## Instructions

# Handling Null Collection Models in updateCollectionModel

## Instructions

- WHEN the TG encounters a static method `updateCollectionModel(FormComponent<Collection<S>>)` in `FormComponent` that retrieves a collection from the model object, clears it, and adds converted input elements
- THEN the TG should test the scenario where:
  1. The `FormComponent` has a `LoadableDetachableModel<Collection<S>>` that returns `null` from its `load()` method (so `getObject()` returns `null`)
  2. The `FormComponent.setConvertedInput(null)` is called (no user input)
  3. `FormComponent.updateCollectionModel(formComponent)` is called
  4. The test should verify that `formComponent.getModelObject().isEmpty()` returns `true` — meaning after the update with null input and null model, the collection should be initialized to an empty collection, NOT throwing a NullPointerException

- WHEN writing a test for the null model / null converted input edge case
- THEN the TG should create a `LoadableDetachableModel<Collection<String>>` whose `load()` returns `null`, create an anonymous `FormComponent<Collection<String>>` using that model, set converted input to `null`, and call `FormComponent.updateCollectionModel(formComponent)`. The test should pass on the fixed version (no exception, model object is empty Collection).

- Common pitfalls:
  - Testing only with non-null model objects (e.g., returning `new ArrayList<>()` from `load()`) — this misses the null model case
  - Testing only with non-null `convertedInput` — the bug manifests specifically when both the model returns null AND converted input is null
  - Forgetting that `updateCollectionModel` is a static method on `FormComponent`, not an instance method
  - Expecting a `WicketRuntimeException` for this case — the bug caused a `NullPointerException`, and the fix should result in an empty collection without exception

**Correct test pattern (matches the triggering test `getModelCollectionIsNullInCaseOfNoConvertedInput`):**

```java
@Test
public void getModelCollectionIsNullInCaseOfNoConvertedInput()
{
    LoadableDetachableModel<Collection<String>> model = new LoadableDetachableModel<Collection<String>>()
    {
        @Override
        protected Collection<String> load()
        {
            return null;
        }
    };
    FormComponent<Collection<String>> formComponent = new FormComponent<Collection<String>>(
            "formComponent", model) { };
    formComponent.setConvertedInput(null);
    FormComponent.updateCollectionModel(formComponent);
    Assert.assertTrue(formComponent.getModelObject().isEmpty());
}
```

**Incorrect test pattern (does NOT catch the bug — uses non-null model):**

```java
@Test
public void testWithNonNullModel()
{
    // This test passes even on the buggy version, missing the null model issue
    LoadableDetachableModel<Collection<String>> model = new LoadableDetachableModel<Collection<String>>()
    {
        @Override
        protected Collection<String> load()
        {
            return new ArrayList<>(); // non-null, hides the bug
        }
    };
    FormComponent<Collection<String>> formComponent = new FormComponent<Collection<String>>(
            "formComponent", model) { };
    formComponent.setConvertedInput(null);
    FormComponent.updateCollectionModel(formComponent);
    Assert.assertTrue(formComponent.getModelObject().isEmpty());
}
```
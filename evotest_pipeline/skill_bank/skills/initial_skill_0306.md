---
name: collection-model-unmodifiable-conversion
description: Use when testing FormComponent.updateCollectionModel() which may convert
  collections to unmodifiable wrappers, breaking subsequent mutations. This skill
  teaches how to verify that converted collections remain modifiable after updateCollectionModel
  processing.
code_tags:
- ARGUMENT_VALIDATION
- BOUNDARY_CHECK
- STATE_MUTATION
- COLLECTION_ITERATION
test_pattern: STATE_TEST
---

# collection-model-unmodifiable-conversion

## Instructions

# Collection Model Update Must Preserve Mutability

## Instructions

- WHEN the TG encounters a call to `FormComponent.updateCollectionModel(FormComponent<Collection<S>>)` that processes a collection model (e.g., wrapping, converting, or replacing the internal collection object)
- THEN the TG should write a test that:
  1. Creates a `FormComponent` with a `Model` wrapping a mutable `Collection` (e.g., `ArrayList<String>`)
  2. Calls `FormComponent.updateCollectionModel(formComponent)` to process the collection
  3. Retrieves the collection from the model after the call
  4. Attempts to **mutate** the retrieved collection (e.g., `add("item")` or `clear()`)
  5. Verifies the mutation succeeds without throwing `UnsupportedOperationException`
- The TG should **not** conclude that a collection is safe to use just because it can be read — the test must explicitly verify mutability after `updateCollectionModel` processing.
- Common pitfalls to avoid:
  - **Pitfall 1**: Testing only that the collection contains expected values after `updateCollectionModel`, without verifying the collection remains mutable (the bug: an `unmodifiableCollection()` wrapper was applied but `add()`/`remove()`/`clear()` on the model's collection silently throws `UnsupportedOperationException` later).
  - **Pitfall 2**: Using a `List` returned from `Collections.unmodifiableList()` or `Collections.singletonList()` as the initial model object — these are immutable from the start and will fail even correctly processed collections.
  - **Pitfall 3**: Testing only with the specific collection type used internally (e.g., `ArrayList`) without verifying that the _same object identity_ or at least the same mutability contract is preserved after processing.

### Example (Correct test, would catch this bug):

```java
@Test
public void updateCollectionModelPreservesMutability() {
    // Create a FormComponent with a mutable collection model
    IModel<Collection<String>> model = Model.ofList(new ArrayList<>(Arrays.asList("a", "b")));
    FormComponent<Collection<String>> component = new TextField<Collection<String>>("comp", model);
    
    // Process the collection model (the buggy code wraps it in unmodifiableCollection)
    FormComponent.updateCollectionModel(component);
    
    // Retrieve the processed collection
    Collection<String> result = component.getModelObject();
    
    // VERIFY: the collection is still mutable
    assertDoesNotThrow(() -> result.add("c"));
    assertEquals(3, result.size());
}
```

### Example (Incorrect test — would miss this bug):

```java
@Test
public void updateCollectionModelContainsExpectedValues() {
    IModel<Collection<String>> model = Model.ofList(new ArrayList<>(Arrays.asList("a", "b")));
    FormComponent<Collection<String>> component = new TextField<Collection<String>>("comp", model);
    FormComponent.updateCollectionModel(component);
    
    // This passes even if the collection is unmodifiable — it only reads
    Collection<String> result = component.getModelObject();
    assertTrue(result.contains("a"));
    assertTrue(result.contains("b"));
    assertEquals(2, result.size());
    // Bug: result.add("c") would throw UnsupportedOperationException here!
}
```
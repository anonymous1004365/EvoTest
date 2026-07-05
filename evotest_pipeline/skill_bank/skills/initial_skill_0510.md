---
name: lazy-class-resolution-in-chained-property-models
description: When testing PropertyModel chains where intermediate models implement
  IObjectClassAwareModel and may have a null target initially, test that getObjectClass()
  returns null for unresolved targets and resolves correctly after the target is populated.
code_tags:
- CLASS_LOADING_OPERATIONS
- WILDCARD_PATTERN_MATCHING
- COLLECTION_MUTATION_IN_LOOP
test_pattern: STATE_TEST
---

# lazy-class-resolution-in-chained-property-models

## Instructions

# Lazy Class Resolution in Chained Property Models

## Instructions

- WHEN the TG encounters code where `AbstractPropertyModel.getObjectClass()` resolves a property expression through a chain of models, and an intermediate model implements `IObjectClassAwareModel` (e.g., `Model<T>`) while the innermost model target is `null`
- THEN the TG should test lazy class resolution: verify that `getObjectClass()` returns `null` when the innermost model target is `null`, and returns the correct `Class` (e.g., `Integer.class`) after the target is populated with an object that has the corresponding property.
  - Construct a chain like: `PropertyModel<Integer>(PropertyModel<CustomType>(Model<CustomBean>(null), "customType"), "someProperty")`
  - First assert `assertNull(somePropertyModel.getObjectClass())` when the outer Model holds null
  - Then set the outer model's object: `modelCustomBean.setObject(new CustomBean())`
  - Then assert `assertEquals(Integer.class, somePropertyModel.getObjectClass())` — the class should now resolve via the intermediate `IObjectClassAwareModel`
- Include concrete class definitions for `CustomBean` (with a `CustomType getCustomType()`) and `CustomType` (with an `Integer getSomeProperty()`) as private static inner classes implementing `Serializable`
- Common pitfalls to avoid:
  - Testing only the case where the innermost target is non-null from the start; the bug is specifically that `getObjectClass()` fails to re-resolve after the target becomes non-null when the intermediate model is an `IObjectClassAwareModel`
  - Not including the intermediate `PropertyModel` that wraps another `PropertyModel` — this nesting through `IObjectClassAwareModel` is essential to trigger the bug
  - Testing `getObject()` instead of `getObjectClass()` — the bug is in the class resolution path, not the value retrieval path
  - Forgetting to use `IObjectClassAwareModel` implementations like `Model<T>` as the target of the outer PropertyModel

**Correct example (what the test should do):**
```java
// Chain: PropertyModel<Integer>(PropertyModel<CustomType>(Model<CustomBean>(null), "customType"), "someProperty")
Model<CustomBean> modelCustomBean = new Model<CustomBean>(null);
PropertyModel<CustomType> customTypeModel = new PropertyModel<CustomType>(modelCustomBean, "customType");
PropertyModel<Integer> somePropertyModel = new PropertyModel<Integer>(customTypeModel, "someProperty");
assertNull(somePropertyModel.getObjectClass());  // target is null initially
modelCustomBean.setObject(new CustomBean());
assertEquals(Integer.class, somePropertyModel.getObjectClass());  // resolves after target is set
```

**Incorrect example (would miss the bug):**
```java
// Only tests non-null target from the start — does not test lazy resolution
Model<CustomBean> modelCustomBean = new Model<CustomBean>(new CustomBean());
PropertyModel<CustomType> customTypeModel = new PropertyModel<CustomType>(modelCustomBean, "customType");
PropertyModel<Integer> somePropertyModel = new PropertyModel<Integer>(customTypeModel, "someProperty");
assertEquals(Integer.class, somePropertyModel.getObjectClass());
// This single assertion passes even in the buggy version
```
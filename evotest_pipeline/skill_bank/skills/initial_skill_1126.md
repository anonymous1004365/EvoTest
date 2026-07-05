---
name: detach-before-attach-model-safety
description: When a model wrapper (e.g., StringResourceModel) has a detach() method
  that delegates to both an inner model and a parent class, tests must verify that
  detach() works safely even when the model was never attached (i.e., its wrapped
  model is null). This skill teaches how to detect and test for NullPointerException
  during premature detach on not-yet-attached models.
code_tags:
- NULL_CHECK
- STATE_CHECK
test_pattern: EXCEPTION_TEST
---

# detach-before-attach-model-safety

## Instructions

# Detach-Before-Attach Model Safety

## Instructions

WHEN the TG encounters a model wrapper class (e.g., `StringResourceModel`) that:
- Has a `detach()` method that calls `super.detach()` and then delegates `detach()` to an inner/nested model object (e.g., via `StringResourceModel.this.detach()`)
- The inner model object reference might be null before the model is properly attached/initialized

THEN the TG should write a test that:
1. Creates an instance of the model wrapper without setting/initializing the inner model (so the inner model reference is null)
2. Calls `detach()` directly on that instance WITHOUT first calling any attach/set/init method
3. Asserts that `detach()` completes WITHOUT throwing a `NullPointerException`

### Concrete values and types:
- For `StringResourceModel`, the inner model is accessed at `StringResourceModel.this.detach()` from within the nested `SerializableModelWrapper` class
- The test method should be annotated with `@Test` and use `Assert.assertNotNull(...)` or simply call `detach()` and verify no exception occurs
- Call the test method something like `detachEvenNotAttached`

### Common pitfalls:
- Testing only the normal "attach then detach" lifecycle — the bug manifests specifically when detach() is called WITHOUT prior attach
- Assuming that `detach()` is a no-op if nothing was attached — the bug is a NullPointerException crash, not incorrect behavior
- Writing a test that catches a general `Exception` — prefer catching only `NullPointerException` or expecting no exception at all

### Example:

**Correct approach:**
```java
@Test
public void detachEvenNotAttached()
{
    // StringResourceModel with null wrapped model (never attached)
    StringResourceModel model = new StringResourceModel("key", null, null);
    // This should not throw NullPointerException
    model.detach();
}
```

**Incorrect approach:**
```java
@Test
public void detachAfterAttach()
{
    // Only tests the normal lifecycle, misses the bug
    StringResourceModel model = new StringResourceModel("key", component, null);
    model.attach(); // this initializes the wrapped model
    model.detach(); // works fine because wrapped model is non-null
}
```

**Another incorrect approach:**
```java
@Test
public void detachEvenNotAttached()
{
    // Catches too broadly - masks other potential bugs
    try {
        StringResourceModel model = new StringResourceModel("key", null, null);
        model.detach();
    } catch (Exception e) {
        // Swallows everything - wrong!
    }
}
```
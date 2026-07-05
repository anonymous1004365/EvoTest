---
name: wrap-on-assignment-for-detachable-models
description: When a component internally wraps an IModel during construction and stores
  the result in a field, the internal wrapping must preserve the model's wrapOnAssignment/detach
  behavior. Test that setting a model that wrapsOnAssignment still works properly
  with component methods like getFileName or other model-consuming methods.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- VALIDATION
- WRAP_ON_ASSIGNMENT_DETACH
test_pattern: INTERACTION_TEST
---

# wrap-on-assignment-for-detachable-models

## Instructions

# Wrapping Models Must Preserve wrapOnAssignment Behavior

## Instructions

WHEN the TG encounters a component that accepts an `IModel` parameter in its constructor and wraps it (e.g., calling `wrap(model)` or similar) before storing it as a field, AND the component has methods that use or return that wrapped model indirectly (e.g., `getFileName()` returns something derived from the stored model),

THEN the TG should write a test that creates a custom `IModel` whose `wrapOnAssignment(Component)` returns a model that records whether it was called (e.g., sets a boolean flag). The test should:

- Construct the component with that custom model.
- Call the component method that uses the wrapped model (e.g., `component.getFileName()`).
- Verify that the custom model's `wrapOnAssignment` method was invoked, i.e., the internal wrapping did not intercept and lose the model's detach lifecycle.

**Common pitfalls:**
- Testing only with simple models like `Model.of(...)` that do not implement `wrapOnAssignment`. Such tests pass even if the component's internal wrapping breaks lifecycle propagation.
- Forgetting that the component's constructor might call `wrap()` on the model, and `wrap()` internally calls `wrapOnAssignment` on the model. If the component does a redundant `super(model)` call that gives back a different model than the one returned by `wrapOnAssignment`, the lifecycle is lost.
- Not verifying that the component's public API method actually triggers the wrapped model's `wrapOnAssignment` path.

**Correct example:**
```java
// Custom model that tracks wrapOnAssignment
IModel<String> fileNameModel = new AbstractModel<String>() {
    boolean wrapOnAssignmentCalled;
    
    @Override
    public <V> IWrapModel<String> wrapOnAssignment(Component component) {
        wrapOnAssignmentCalled = true;
        return super.wrapOnAssignment(component);
    }
    
    @Override
    public String getObject() {
        return "test.txt";
    }
};

// Build the component
DownloadLink link = new DownloadLink("link", new File(""), fileNameModel);

// Exercise a method that ultimately uses the stored model
String fileName = link.getFileName();

// Verify wrapOnAssignment was invoked
assertTrue("wrapOnAssignment should have been called", fileNameModel.wrapOnAssignmentCalled);
```

**Incorrect example (pitfall):**
```java
// Using a simple Model.of(...) — always works, hides the bug
DownloadLink link = new DownloadLink("link", new File(""), Model.of("test.txt"));
assertEquals("test.txt", link.getFileName());
// This test never verifies that wrapOnAssignment lifecycle is propagated.
```
---
name: class-hierarchy-method-collection-visibility
description: ''
code_tags:
- STATE_MUTATION
- NULL_CHECK
- TYPE_CONVERSION
- GET_ALL_METHODS_OVERRIDE_VISIBILITY
test_pattern: STATE_TEST
---

# class-hierarchy-method-collection-visibility

## Instructions

# Class Hierarchy Method Collection with Visibility Filtering

## Instructions

### WHEN the TG encounters a method that:
1. **Collects methods from a parent class/interface** by calling `super.getAllMethods(...)`, `super.getMethodsForClass(...)`, or similar delegation
2. **Filters those collected methods** based on visibility modifiers (e.g., `isPrivate()`, `MODIFIERS.PRIVATE`)
3. **Overrides a same-named method** in a parent class that already performs similar collection/filtering

### THEN the TG should:

1. **Create a test hierarchy** where:
   - A **parent interface/class** declares a private method (e.g., a `private` default method in an interface, or a private method in a class)
   - A **child interface/class** extends/implements the parent and calls a method-collection routine that inherits from the parent

2. **Build the specific scenario**:
   - Parent interface (`ParentInterface`) defines a `private default void privateMethod()` (or similar private method)
   - Child interface extends the parent
   - Invoke the method-collection method (e.g., `getAllMethods()`) on the **child** type
   - The parent's method collection (called via `super.xxx()`) should **include** private methods, but the child's override should **filter them out**

3. **Verify the correct behavior**:
   - Assert that private methods from the parent class are **not present** in the result set when collected via the child
   - Assert that public/protected methods from the parent **are present**
   - The test should **fail on the buggy version** (where private methods are incorrectly included) and **pass on the fixed version**

4. **What to check for**:
   - The method may call `super.getAllMethods(...)` which returns all methods (including parent-private ones), then the outer method should filter them
   - If the bug is in the filtering logic (e.g., the filter runs on the wrong set, or the `getAllMethods` override in the child doesn't filter private methods inherited from the parent), the test must expose this

### Common Pitfalls to Avoid

- **Only testing flat/leaf classes**: Do not test `getAllMethods()` only on a concrete class with no inheritance. The bug only manifests when a parent also overrides `getAllMethods()` with different visibility filtering.
- **Testing only public methods**: The test must include a `private` method in the parent to verify visibility filtering.
- **Assuming `super.getAllMethods()` returns the same type**: Verify that the child method doesn't just pass through the parent's result without filtering.
- **Forgetting to test the child type**: The bug is in collecting methods for a **child** type that inherits from a parent with its own `getAllMethods()` override — testing the parent alone won't catch it.

### Correct Example (pseudocode)

```java
// Parent interface
interface ParentInterface {
    private void privateMethod() {}
    
    default void somePublicMethod() {}
}

// Test the child's getAllMethods filters parent-private methods
@Test
public void testGetAllMethodsFiltersParentPrivateMethods() {
    CtType<?> childType = factory.Type().get(ChildInterface.class);
    Collection<CtMethod<?>> methods = childType.getAllMethods();
    
    // Parent's private method should NOT appear
    CtMethod<?> privateMethod = methods.stream()
        .filter(m -> m.getSimpleName().equals("privateMethod"))
        .findFirst().orElse(null);
    assertNull("Parent private method should not be collected via child", privateMethod);
    
    // Parent's public method SHOULD appear
    CtMethod<?> publicMethod = methods.stream()
        .filter(m -> m.getSimpleName().equals("somePublicMethod"))
        .findFirst().orElse(null);
    assertNotNull("Parent public method should be collected", publicMethod);
}
```

### Incorrect Approach (would NOT catch the bug)

```java
// ❌ Only testing on the parent type
@Test
public void testGetAllMethods_parentOnly() {
    CtType<?> parentType = factory.Type().get(ParentInterface.class);
    Collection<CtMethod<?>> methods = parentType.getAllMethods();
    // This would pass even on buggy version because the parent's
    // getAllMethods already handles its own private methods correctly
    assertTrue(methods.size() > 0);
}

// ❌ Not including a private method in the hierarchy
@Test
public void testGetAllMethods_publicOnly() {
    // If no private method exists in the parent, the bug can't manifest
    CtType<?> childType = factory.Type().get(ChildInterface.class);
    Collection<CtMethod<?>> methods = childType.getAllMethods();
    assertEquals(1, methods.size()); // passes even with the bug
}
```
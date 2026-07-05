---
name: framework-type-reflection-fallback
description: ''
code_tags:
- STATE_MUTATION
- NULL_CHECK
- REFLECTION_METADATA_LOOKUP
test_pattern: STATE_TEST
---

# framework-type-reflection-fallback

## Instructions

# Framework Type Reflection Fallback

## Instructions

**WHEN** the TG encounters an entity instantiator, property accessor factory, or similar component that:
- Uses reflection (e.g., `Class.forName()`, `Type.getDeclaredConstructor()`, `Arrays.stream(type.getConstructors())`) to look up **framework-specific types** (e.g., types from a persistence or bean framework)
- Has **two modes**: one that uses the framework type (e.g., `BeanWrapper`, `PersistentEntity`) and one that falls back to plain reflection (e.g., `Constructor.newInstance()`)
- Contains logic that **mutates internal state** (e.g., cached constructors, an `instantiator` field) based on whether the framework type is found

**THEN** the TG **MUST**:
1. Write a test that **simulates the absence** of the framework type — typically by running in an environment where the framework class is not on the classpath (or by using a stub/mock that makes `isVisible()` / `isPresent()` return `false`).
2. **Verify that the fallback path is taken**: assert that the component produces a valid result (e.g., a non-null `EntityInstantiator` or `PropertyAccessor`) even when the framework type is missing.
3. **Verify that the result uses fallback behavior**: If the fallback uses plain `Constructor.newInstance()`, then the resulting object should be creatable via that fallback. For example, if the fallback uses `ReflectionEntityInstantiator`, assert the returned type matches that fallback class.
4. **Verify the fallback works end-to-end**: Actually instantiate an entity through the fallback path and assert the resulting object is non-null and of the expected type.
5. **Test with a concrete domain class**: Use a simple POJO as the entity class to exercise the instantiation logic.

**Common pitfalls to avoid:**
- ❌ **Mocking only the success path**: Testing only the case where the framework type IS available does not catch bugs where the fallback path is broken.
- ❌ **Assuming fallback is used automatically**: Verify through assertions that the fallback implementation is actually selected (e.g., by checking the runtime type of the returned instantiator).
- ❌ **Forgetting to clear cached state**: If the component caches previous lookup results, the test must ensure no stale state from other tests influences the fallback scenario (e.g., by using `@Before` setup or fresh instances).
- ❌ **Testing with a framework type that happens to be visible**: In a test environment, framework classes might be on the classpath even though they would be absent in production. Use a type that is **guaranteed absent** or explicitly mark framework types as not visible via configuration/mocking.

**Example (correct):**

```java
// Test that when the framework type (BeanWrapper) is NOT visible,
// the factory falls back to reflection-based instantiation.

@Test
public void shouldUseReflectionIfFrameworkTypesNotVisible() {
    // Given a ClassGeneratingEntityInstantiator with no framework types visible
    ClassGeneratingEntityInstantiator instantiator = new ClassGeneratingEntityInstantiator();

    // When creating an instantiator for a simple POJO
    EntityInstantiator result = instantiator.createInstantiator(SimplePojo.class);

    // Then the result should be a reflection-based instantiator (not null, works end-to-end)
    assertThat(result).isNotNull();
    assertThat(result).isInstanceOf(ReflectionEntityInstantiator.class);

    // And it should be able to actually create an instance
    SimplePojo instance = result.createInstance();
    assertThat(instance).isNotNull();
}
```

**Example (incorrect — only tests the happy path):**

```java
// WRONG: Only tests when framework types ARE visible.
// This does NOT catch the bug where the fallback throws NPE
// or returns null when framework types are absent.

@Test
public void shouldCreateInstantiator() {
    ClassGeneratingEntityInstantiator instantiator = new ClassGeneratingEntityInstantiator();
    // BeanWrapper is on the classpath in test, so this uses the framework path
    EntityInstantiator result = instantiator.createInstantiator(SimplePojo.class);
    // The fallback path is never exercised
    assertThat(result).isNotNull();
}
```
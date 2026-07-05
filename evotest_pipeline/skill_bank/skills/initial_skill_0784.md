---
name: reactive-type-component-resolution
description: WHEN testing methods that resolve component types from reactive wrapper
  types (like Flux/Mono) by extracting generic type parameters, THEN verify that non-generic
  superclass method declarations (e.g., mocked superclass returning raw Flux) don't
  cause NPEs or type mismatches. This skill applies to code that uses Java reflection
  to extract type arguments from method return types.
code_tags:
- STATE_BASED_DECISION
- TYPE_CONVERSION
- VALIDATION
- NULL_CHECK
test_pattern: EXCEPTION_TEST
---

# reactive-type-component-resolution

## Instructions

# Reactive Type Component Resolution from Generic Return Types

## Instructions

WHEN the TG encounters a method that:
- Uses `ResolvableType`, `Type`, `ParameterizedType`, or generic reflection to extract component/generic type arguments from a return type (e.g., getting the `<T>` from `Flux<T>` or `Mono<T>`)
- The code calls `getGenericSuperclass()`, `getActualTypeArguments()`, `ResolvableType.getGeneric()`, or similar reflection-based generic type resolution
- The return type is a reactive wrapper type (like `Flux`, `Mono`, `Observable`, `Publisher`)

THEN the TG should:
1. Create a test that mocks/declares a superclass method returning a non-generic version of the reactive wrapper (e.g., `Flux` without type parameter, not `Flux<T>` or `Flux<String>`)
2. Verify that calling the type-resolution method on the subclass that inherits/overrides that method does NOT throw a `NullPointerException` or any other exception
3. Specifically, test that when `getActualTypeArguments()` returns an empty array or `ResolvableType.getGeneric()` resolves to `ResolvableType.NONE`, the code handles it gracefully (no NPE on array access or null dereference)

Concrete example (from the buggy code `DeclaredCommandMethod`):
- **Buggy behavior**: When resolving the component type from a `Flux` (raw, no generics) method declaration, the code accesses index `[0]` of `getActualTypeArguments()` without checking if the array is empty (i.e., not a `ParameterizedType`), causing an `ArrayIndexOutOfBoundsException` or `NullPointerException`.
- **Expected behavior**: The code should check if the return type is a `ParameterizedType` before accessing its type arguments, or handle the case where no type arguments exist.

**Common pitfalls to avoid:**
- ❌ Only testing with well-typed generic declarations (e.g., `Flux<String> method()`). The bug is specifically triggered by raw/non-generic usage.
- ❌ Assuming all `Flux`/`Mono` return types will have a concrete type parameter. Code may be compiled with erased generics or use raw types.
- ❌ Only testing the "happy path" where type parameters are present.

**Example test code (correct approach):**
```java
// Test: subclass method returns raw Flux (no type parameter)
// This should not throw NPE or AIOOBE
@Test
void shouldResolveFluxComponentType() {
    // Create a subclass whose method returns raw Flux (not Flux<T> or Flux<String>)
    class RawFluxMethod extends AbstractCommandMethod {
        @Override
        public Flux myMethod() { return Flux.empty(); }
        // ^ raw return type, no generics
    }

    DeclaredCommandMethod cmd = new DeclaredCommandMethod(RawFluxMethod.class.getDeclaredMethod("myMethod"));
    assertThatCode(() -> cmd.getComponentType()).doesNotThrowAnyException();
}
```

**Example test code (wrong approach — won't catch the bug):**
```java
@Test
void shouldResolveFluxComponentType() {
    // ❌ Only testing with typed generic — won't hit the bug
    class TypedFluxMethod extends AbstractCommandMethod {
        @Override
        public Flux<String> myMethod() { return Flux.empty(); }
    }
    DeclaredCommandMethod cmd = new DeclaredCommandMethod(TypedFluxMethod.class.getDeclaredMethod("myMethod"));
    assertEquals(String.class, cmd.getComponentType());
}
```

**What to assert:** When testing with raw/non-generic return types, assert that `getComponentType()` (or equivalent) returns `null` or a sentinel value like `ResolvableType.NONE`, rather than throwing an exception.
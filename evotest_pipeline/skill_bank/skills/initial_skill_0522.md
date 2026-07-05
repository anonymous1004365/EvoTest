---
name: generic-type-with-subclass-validation
description: When testing generic type extraction with subclass input types, write
  tests that verify InvalidTypesException is thrown when a generic type (like a MapFunction
  returning a generic type variable 'T') cannot be resolved due to missing concrete
  type information, especially when the input type is a subclass of the expected parameter
  type.
code_tags:
- TYPE_CONVERSION
- VALIDATION
test_pattern: EXCEPTION_TEST
---

# generic-type-with-subclass-validation

## Instructions

# Generic Type Extraction with Subclass Input Validation

## Instructions

- WHEN the TG encounters code that calls `TypeExtractor.getMapReturnTypes()` (or similar type extraction methods like `getFlatMapReturnTypes`, `getGroupReduceReturnTypes`, etc.) with a function that has generic return type parameters (e.g., `MapFunction<T, T>` where `T` is a type variable), and the input type information passed is a **subclass** (not the exact type) of the function's expected input type parameter:
  - THEN the TG should write a test that expects **`InvalidTypesException`** to be thrown.
  - Use `@Test(expected = InvalidTypesException.class)` for the test annotation.
  - Create an anonymous `MapFunction<T, T>` (or the relevant function interface) where both input and output are the same generic type parameter `T`.
  - Pass a `TypeInformation` for a **subclass** (e.g., if the function parameter is typed as a base class `MyBaseClass`, pass `TypeExtractor.getForClass(MySubClass.class)` where `MySubClass extends MyBaseClass`) as the input type information argument.
  - Verify that the call `TypeExtractor.getMapReturnTypes(function, inputTypeInfo)` throws `InvalidTypesException`.

- WHEN building the test structure:
  - THEN define helper classes: a generic base class (e.g., a simple POJO with methods) and a concrete subclass that extends it.
  - The function should be `new MapFunction<BaseClass, BaseClass>() { ... }` (not using wildcards — use the exact generic type).
  - The input type info should be `TypeExtractor.getForClass(SubClass.class)`.
  - Avoid the mistake of passing `TypeExtractor.getForClass(BaseClass.class)` (the exact type), as that would succeed and NOT trigger the bug.

- Common pitfalls to avoid:
  - Testing with the **exact** same type in both the function signature and the type info argument — this will NOT trigger the bug and the test will pass on both buggy and fixed versions.
  - Testing with unrelated types that are not in an inheritance hierarchy — the bug specifically involves subclass-to-base-class type matching.
  - Using wildcard generic types (`MapFunction<?, ?>`) in the function declaration — the function must use a concrete generic type parameter (like `T` or an actual class) to trigger the resolution logic.
  - Forgetting the `@Test(expected = InvalidTypesException.class)` annotation or not catching the exception — the test MUST verify the exception is thrown.

### Correct Example (catching the bug):
```java
// Helper classes
public static class MyBaseClass {
    public int x;
}

public static class MySubClass extends MyBaseClass {
    public int y;
}

// Test method
@Test(expected = InvalidTypesException.class)
public void testGenericTypeWithSubclassInput() {
    MapFunction<MyBaseClass, MyBaseClass> function = new MapFunction<MyBaseClass, MyBaseClass>() {
        @Override
        public MyBaseClass map(MyBaseClass value) throws Exception {
            return value;
        }
    };
    
    TypeInformation<?> inputType = TypeExtractor.getForClass(MySubClass.class);
    TypeExtractor.getMapReturnTypes(function, inputType);
}
```

### Incorrect Example (will NOT catch the bug):
```java
// Using the exact same type — will succeed on both versions
@Test
public void testGenericTypeWithExactInput() {
    MapFunction<MyBaseClass, MyBaseClass> function = ...;
    TypeInformation<?> inputType = TypeExtractor.getForClass(MyBaseClass.class);
    TypeInformation<?> result = TypeExtractor.getMapReturnTypes(function, inputType);
    Assert.assertNotNull(result); // passes on both buggy and fixed
}
```
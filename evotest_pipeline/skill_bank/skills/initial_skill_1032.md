---
name: duplicate-type-extraction-validation
description: When testing type extraction logic for POJOs or nested types, ensure
  that duplicate type variables or type arguments (e.g., same TypeVariable appearing
  multiple times in a type hierarchy) are handled correctly without throwing an InvalidTypesException.
  This skill applies to TypeExtractor tests in Flink's type system.
code_tags:
- NULL_CHECK
- TYPE_CONVERSION
- VALIDATION
test_pattern: EXCEPTION_TEST
---

# duplicate-type-extraction-validation

## Instructions

# Duplicate Type Variable Extraction Validation

## Instructions

- WHEN the TG encounters a type extraction method (such as `TypeExtractor.getForClass()` or `TypeExtractor.getForObject()`) being called on a class that contains duplicate type variables in its type hierarchy (e.g., a POJO with a field of type `Tuple2<T, T>` or a class that extends a generic superclass with the same type variable appearing multiple times)
- THEN the TG should write a test that creates a concrete instance of the class with a specific type argument (e.g., `Tuple2<String, String>`) and calls `TypeExtractor.getForObject(instance)` or `TypeExtractor.getForClass(ConcreteClass.class)`, and verify that it does NOT throw an `InvalidTypesException`. The test should expect the method to succeed and return a valid `TypeInformation`.
- WHEN the TG tests nested type variables (e.g., a class `MyClass<T>` with a field of type `Tuple2<T, T>` that is then parameterized as `MyClass<String>`), the test must use a concrete subclass or anonymous class with the type parameter bound to a specific type like `String`, and call `TypeExtractor.getForObject()` on an instance — NOT `getForClass()` which only works for basic types and may itself throw.
- Common pitfalls to avoid:
  - Testing only flat (non-duplicate) type variables and assuming nested duplicate variables are handled identically
  - Testing `getForClass()` on a parameterized type (which throws `InvalidTypesException` by design) and confusing that with the actual extraction bug
  - Forgetting that `getForObject()` requires an actual instance to be created with concrete type arguments
  - Not testing the nested/indirect case where a POJO field itself contains a generic type with the same type variable appearing twice (e.g., `Tuple2<T, T>`)

### Correct Example (catches the bug)

```java
// Suppose we have:
// public class MyDuplicateValueType<T> {
//     public Tuple2<T, T> value;
// }

@Test
public void testDuplicateValueNested() {
    // Use getForObject with a concrete instance
    MyDuplicateValueType<String> obj = new MyDuplicateValueType<>();
    obj.value = new Tuple2<>("hello", "world");
    
    // This should NOT throw InvalidTypesException
    TypeInformation<?> ti = TypeExtractor.getForObject(obj);
    
    // Verify the type is correctly extracted
    Assert.assertTrue(ti instanceof PojoTypeInfo);
    // Further assertions on the extracted type...
}
```

### Incorrect Example (misses the bug)

```java
// WRONG: Uses getForClass on a parameterized type (will throw, but for the wrong reason)
@Test
public void testDuplicateValueNested_WRONG() {
    TypeInformation<?> ti = TypeExtractor.getForClass(MyDuplicateValueType.class);
    // This throws InvalidTypesException from getForClass, which is expected behavior
    // and does NOT test the actual bug in type variable handling
}

// WRONG: Only tests flat (non-duplicate) cases
@Test
public void testDuplicateValueNested_WRONG2() {
    // Testing MyDuplicateValueType with a non-duplicate type variable
    // e.g., Tuple2<T, U> where T != U — this works fine
    // The bug only manifests when the same type variable appears twice
}
```
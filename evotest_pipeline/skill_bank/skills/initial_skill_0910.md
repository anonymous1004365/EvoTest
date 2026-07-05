---
name: nested-generics-type-resolution
description: When resolving type arguments for nested generic types (e.g., Map<String,
  List<String>>), the TG should verify that the getTypeInformation(Type fieldType,
  Type owningType) method resolves all levels of generic parameters correctly. This
  skill helps catch cases where intermediate generic types are resolved to their raw
  type instead of preserving generic type arguments.
code_tags:
- GENERICS_TYPE_ARGUMENT_RESOLUTION
- NESTED_GENERICS_DETECTION
test_pattern: PARAMETRIC_TEST
---

# nested-generics-type-resolution

## Instructions

# Nested Generics Type Resolution

## Instructions

- WHEN the TG encounters code that resolves generic type information using `ParameterizedTypeInformation` or similar type discovery utilities — specifically when resolving nested generics like `Map<String, List<String>>` or `Map<String, Comparable<String>>`
- THEN the TG should write a test that:
  1. Creates a class that extends or implements an interface with a nested generic type parameter (e.g., `class Sample extends AbstractMap<String, List<String>>`)
  2. Uses `ParameterizedTypeInformation` or `TypeDiscoverer` to resolve the type information for a method or field that exposes the nested generic type
  3. Asserts that the resolved type information correctly preserves ALL levels of generics — not just the first level
  4. Specifically, verify that a type like `List<String>` inside `Map<String, List<String>>` is resolved as `java.util.List<java.lang.String>` and NOT as the raw type `java.util.List`
- Common pitfalls to avoid:
  - ❌ Testing only with single-level generics (e.g., `Map<String, String>`) which doesn't exercise the nested resolution path
  - ❌ Only checking that the outer type parameter is resolved (e.g., verifying `Map` is correct but not checking the inner `value` type's generic parameter)
  - ❌ Using `getType()` on the type information and assuming it returns the parameterized type rather than checking `getType().getActualTypeArguments()` or using `getResolvedType()` if available

### Correct Example
```java
@Test
public void detectsNestedGenerics() {
  // Create a type information object for a class with nested generics
  TypeInformation<?> typeInfo = new ParameterizedTypeInformation<>(Sample.class, null) {
    // Or use the actual API that resolves type information
  };
  
  // Get the type information for the value type parameter (e.g., the V in Map<K,V>)
  TypeInformation<?> valueTypeInfo = typeInfo.getTypeArguments().get(1);
  
  // The value type should be a ParameterizedType (e.g., List<String>), not a raw Class
  assertThat(valueTypeInfo.getType(), is(equalTo((Type) new TypeToken<List<String>>() {}.getType())));
  // Or more specifically, the type argument of the value type should be String
  assertThat(valueTypeInfo.getTypeArguments().get(0).getType(), is(equalTo((Type) String.class)));
}
```

### Incorrect Example
```java
// ❌ This test passes even if the bug exists because it only checks the raw type
@Test
public void testGenerics() {
  TypeInformation<?> typeInfo = new ParameterizedTypeInformation<>(Sample.class, null);
  TypeInformation<?> valueTypeInfo = typeInfo.getTypeArguments().get(1);
  
  // This passes even if List<String> is resolved as raw List
  assertThat(valueTypeInfo.getType(), is(equalTo(List.class)));
}
```
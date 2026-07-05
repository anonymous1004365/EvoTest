---
name: interface-proxy-type-variable-boundary
description: When a method parameter uses a type variable but the implementation creates
  a proxy for a concrete interface, the TG should test that type variable bounds are
  respected and not incorrectly used as actual parameter types.
code_tags:
- TYPE_CONVERSION
- TYPE_CONVERSION_INTERFACE_VS_CLASS_PROXY
test_pattern: EXCEPTION_TEST
---

# interface-proxy-type-variable-boundary

## Instructions

# Interface Proxy Type Variable Boundary

## Instructions

- WHEN the TG encounters code that creates a dynamic proxy (e.g., via `java.lang.reflect.Proxy`, Jackson's proxy, or Spring's projection proxy) for an interface or abstract class that has a method parameterized with a type variable (e.g., `<T> T doSomething(Class<T> type, T value)` or `void add(T element)`), AND the implementation may conflate the type variable bound with an actual concrete type (e.g., treating a `Class<? extends TypeVariable>` as if it were `TypeVariable` itself, or passing a type variable's bound as a parameter type)

- THEN the TG should write a test that:
  - Creates a concrete implementation or subclass that binds the type variable to a specific concrete type (e.g., binds `T` to `String`)
  - Passes a value of a different but compatible type (e.g., a non-String object that is also within the bound) to the type-variable-parameterized method
  - Asserts that the proxy/implementation correctly accepts only values matching the concrete bound, and throws an appropriate exception (e.g., `IllegalArgumentException`, `JsonMappingException`, `ClassCastException`) for non-matching types

- Common pitfalls to avoid:
  - Testing only with values that match the type variable's upper bound (e.g., testing only `String` when the bound is `Object`), which would not catch the bug
  - Failing to distinguish between the type variable declaration (e.g., `<T>`) and the actual concrete type argument (e.g., `String`)
  - Not testing with a type that is assignable to the type variable's bound but NOT assignable to the concrete type the interface was projected with

- Example: If a projection interface declares `void setData(Object data)` but the implementation projects onto an interface that binds the type to `String`, then passing a non-String Object (e.g., `Integer`) should fail, while passing a `String` should succeed. The test must include both cases to verify the bug fix.

- Correct test pattern:
```java
@Test
void doesNotConsiderTypeVariableBoundTo() {
    // Create an implementation that binds T to String
    MyInterface<String> impl = new MyInterface<String>() {
        public void setData(String data) { }
    };
    // Create dynamic proxy for the interface
    MyInterface<String> proxy = createProxy(impl, MyInterface.class);
    // Passing String should work
    proxy.setData("hello");
    // Passing Integer should throw exception because T is bound to String
    assertThrows(SomeExpectedException.class, () -> proxy.setData(42));
}
```

- Incorrect test pattern (would not catch the bug):
```java
@Test
void doesNotConsiderTypeVariableBoundTo() {
    MyInterface<String> impl = new MyInterface<String>() {
        public void setData(String data) { }
    };
    MyInterface<String> proxy = createProxy(impl, MyInterface.class);
    // Only tests String, never checks that non-String values fail
    proxy.setData("hello");
    proxy.setData("world");
}
```
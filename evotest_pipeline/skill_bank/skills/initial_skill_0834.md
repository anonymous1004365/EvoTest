---
name: method-annotation-interface-lookup
description: When BeanInfo introspects methods with filtered annotations, it may fail
  to find methods when the annotation is declared on an interface and the implementing
  class has overloaded methods. Test by creating interfaces with annotated overloaded
  methods and verifying BeanInfo correctly matches the annotation to the right method.
code_tags:
- ARGUMENT_VALIDATION
- BEAN_PROPERTY_ASSIGNMENT
test_pattern: PARAMETRIC_TEST
---

# method-annotation-interface-lookup

## Instructions

# Method Annotation Interface Lookup for Overloaded Methods

## Instructions

- WHEN the TG encounters BeanInfo introspecting methods using a `MethodsFilter` (e.g., with `@Oneway` annotation filtering) on a class that implements an interface with overloaded methods
  - THEN it should test with an interface that declares TWO distinctly named methods, each annotated with `@Oneway`, and a class that implements the interface
  - THEN it should verify that `BeanInfo.getMethodInfo()` returns a non-null result for BOTH method calls (one for each method name)
  - THEN it should catch `AmbiguousMethodCallException` or any `MethodNotFoundException` from the buggy version by asserting that method lookups succeed  
  - Common pitfalls: 
    - Testing only a method that exists on the concrete class itself, not on the interface
    - Testing with only ONE overloaded method (the bug only manifests with TWO distinct methods declared on the interface, where one method's annotation lookup returns a wrong ambiguous match)
    - Assuming that if one method works, all methods work
    - Testing overloaded methods with the same name (the bug is about different method names on an interface, not same-named overloads)

- WHEN writing the test for this bug
  - THEN create a bean interface such as `MyOneWayInterfaceWithOverloadedMethod` that declares TWO methods, e.g., `void inOnlyMethod()` and `void overloadedMethod()`, both annotated with `@Oneway`
  - THEN create a concrete class that implements this interface (can be anonymous or a simple implementation)
  - THEN create a `BeanInfo` using the interface `Class<?>` as the type parameter to `createBeanInfo(type)`
  - THEN call `info.getMethodInfo(methodName)` for EACH method name (e.g., `"inOnlyMethod"` and `"overloadedMethod"`)
  - THEN assert that both calls return non-null results
  - Common pitfalls:
    - Testing with only one method (the bug is a lookup failure that occurs for one of the methods)
    - Passing the implementation class instead of the interface class to `createBeanInfo`
    - Not checking both methods independently

### Correct Example
```java
public interface MyOneWayInterfaceWithOverloadedMethod {
    @Oneway void inOnlyMethod();
    @Oneway void overloadedMethod();
}

@Test
public void testMethodPatternUsingMethodAnnotationsOnInterface() throws Exception {
    BeanInfo info = createBeanInfo(MyOneWayInterfaceWithOverloadedMethod.class);
    
    MethodInfo methodInfo = info.getMethodInfo("inOnlyMethod");
    assertNotNull("Should find methodInfo for inOnlyMethod", methodInfo);
    
    methodInfo = info.getMethodInfo("overloadedMethod");
    assertNotNull("Should find methodInfo for overloadedMethod", methodInfo);
}
```

### Incorrect Example (Would Not Catch the Bug)
```java
// Only tests one method — would pass even on buggy version
@Test
public void testMethodPatternUsingMethodAnnotationsOnInterface() throws Exception {
    BeanInfo info = createBeanInfo(MyOneWayInterfaceWithOverloadedMethod.class);
    MethodInfo methodInfo = info.getMethodInfo("overloadedMethod");
    assertNotNull(methodInfo);
}
```
---
name: interface-default-method-selection-priority
description: When selecting handler methods for bean invocation, default methods from
  interfaces should be preferred over concrete class methods when the interface is
  explicitly specified. This skill teaches the TG to test method selection order in
  bean proxy scenarios involving interface default methods.
code_tags:
- STATE_MUTATION
- TYPE_CONVERSION
test_pattern: INTERACTION_TEST
---

# interface-default-method-selection-priority

## Instructions

# Interface Default Method Selection Priority

## Instructions

- WHEN the TG encounters code that selects a method to invoke on a bean proxy where:
  - The bean implements an interface that declares a default method
  - The bean's concrete class also declares a method with the same signature (e.g., implementing the interface method directly)
  - The handler selection logic iterates over candidate methods

- THEN the TG should test that:
  - When a bean proxy is cast to its interface type, invoking the interface's default method should execute the interface's default implementation, NOT the concrete class's override
  - The test should create an interface with a default method (e.g., `default String doSomething() { return "from-interface"; }`)
  - The test should create a concrete class that implements the interface AND overrides the default method (e.g., `@Override public String doSomething() { return "from-class"; }`)
  - The test should use Camel's `@Bean` annotation or bean component to invoke the method via the interface type
  - The test should verify that the returned value matches the interface default method's return value (e.g., `"from-interface"`), not the concrete class's override

- Common pitfalls to avoid:
  - **Testing only the concrete class directly**: Without casting to the interface type, the test will not exercise the buggy code path
  - **Using interfaces without default methods**: The bug only manifests when the interface has a default method implementation
  - **Assuming concrete class methods take priority**: The fix reverses the iteration order so interface methods are checked first
  - **Forgetting to use a bean proxy**: Direct method invocation on the object won't trigger the selection logic; the test must go through Camel's bean parameter binding mechanism

- Example test (correct):

  ```java
  public interface MyService {
      default String doSomething() {
          return "hello";
      }
  }
  
  public static class MyServiceImpl implements MyService {
      @Override
      public String doSomething() {
          return "doCompute";
      }
  }
  
  @Test
  public void testInterfaceDefaultMethodIsCalled() {
      MyServiceImpl myService = new MyServiceImpl();
      // When invoking via the interface type through Camel bean component,
      // the interface's default method should be selected, not the class override
      String result = endpoint.exchangeBody(myService, "doSomething", String.class);
      assertEquals("hello", result);
  }
  ```

- Example test (incorrect — would miss the bug):

  ```java
  // WRONG: Tests the concrete class directly without going through 
  // interface method selection logic
  @Test
  public void testDirectInvocation() {
      MyServiceImpl myService = new MyServiceImpl();
      assertEquals("doCompute", myService.doSomething());  // Always passes, no bug detected
  }
  
  // WRONG: Interface without a default method — not exercising the buggy path
  public interface MyService {
      String doSomething();  // no default implementation
  }
  ```
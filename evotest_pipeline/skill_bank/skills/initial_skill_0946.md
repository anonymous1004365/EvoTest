---
name: elasticsearch-stackoverflow-scanner-recursion
description: When a CtScanner visits an executable reference whose declaring type
  has type parameters that reference back to the executable, the scanner can cause
  infinite recursion and stack overflow. This skill teaches how to test that a scanner
  handles circular reference graphs safely.
code_tags:
- VALIDATION
- RECURSIVE_VISITOR_OVERFLOW
- CIRCULAR_REFERENCE_TRAVERSAL
test_pattern: EXCEPTION_TEST
---

# elasticsearch-stackoverflow-scanner-recursion

## Instructions

# Elasticsearch Stackoverflow: CtScanner Infinite Recursion on Reference Cycles

## Instructions

- WHEN the Test Generator (TG) encounters a `CtScanner` (or custom scanner subclass) that overrides `visitCtExecutableReference` and/or `visitCtTypeReference`, and the metamodel being scanned contains an `executable reference` whose `declaring type` can circularly reference back (via type parameters on the declaring type that refer to the executable), THEN the TG should write a test that:

  1. Creates or loads a model containing a class with a method whose return type is a parameterized type (e.g., `TransportBroadcastAction<Request, Response>`), where the method signature involves type parameters that create a reference cycle between `CtExecutableReference` → `CtTypeReference` → back to the same or related `CtExecutableReference`.
  2. Creates a `CtScanner` instance (or uses the default scanner) and scans the model element (e.g., calls `scanner.scan(element)` on a `CtType`, `CtExecutable`, or `CtPackage`).
  3. Asserts that the scan completes without throwing a `StackOverflowError`.
  4. Alternatively, if a specific method like `getActualClass()` on a `CtExecutableReference` is part of the traversal, test that method directly on an executable reference from such a circular model.

  - **Concrete example**: Load the test resource from the classpath (e.g., `src/test/resources/noclasspath/elasticsearch-stackoverflow/TransportBroadcastAction.java`) using the Spoon `Launcher` with `noClasspath(true)`, build the model, then create a scanner and scan the top-level type `TransportBroadcastAction`. Verify no `StackOverflowError` is thrown.

  - **Common pitfalls**:
    - **Testing only simple types**: The TG might test with a simple class that has no generics or type parameters. Without cyclic references, the bug won't reproduce. Ensure the test uses a class with generic type parameters in its method signatures that create a circular reference graph.
    - **Not using noClasspath mode**: If the test loads classes with full classpath resolution, the cycle may be resolved differently and the scanner might not enter the recursive path. Use `new Launcher().addInputResource("...").buildModel()` or `Launcher.parseClass(...)` with a no-classpath setup.
    - **Assuming only CtScanner is affected**: The TG might think only custom scanners are vulnerable. The bug can also manifest in the default `CtScanner` when visiting a model that contains this circular reference pattern. The test should use the default scanner (or a minimal subclass that calls `super.visitCtExecutableReference`) to confirm the baseline behavior.
    - **Only testing one visitor method**: The TG might only override `visitCtExecutableReference` without also verifying `visitCtTypeReference`. Since the recursion goes through both visitor methods, a test that isolates just one may not trigger the cycle. Use a full scan of the entire type.

- **Example of a correct test (JUnit 4)**:

```java
@Test
public void testNoStackOverflowOnScanner() {
    // contract: CtScanner should not throw StackOverflowError when scanning
    // a type whose executable references create a reference cycle via type parameters
    Launcher launcher = new Launcher();
    launcher.addInputResource("./src/test/resources/noclasspath/elasticsearch-stackoverflow/TransportBroadcastAction.java");
    launcher.getEnvironment().setNoClasspath(true);
    CtModel model = launcher.buildModel();

    CtType<?> transportBroadcastAction = model.getAllTypes().stream()
        .filter(t -> t.getSimpleName().equals("TransportBroadcastAction"))
        .findFirst().get();

    // Use the default scanner — it visits exec references and type references
    CtScanner scanner = new CtScanner() {};
    // This should not throw StackOverflowError
    scanner.scan(transportBroadcastAction);
}
```

- **Example of an incorrect test** (would NOT catch the bug):

```java
@Test
public void testSimpleScan() {
    // WRONG: scans a simple class without generics/circular references
    Launcher launcher = new Launcher();
    launcher.addInputResource("src/test/java/some/SimpleClass.java");
    launcher.getEnvironment().setNoClasspath(true);
    CtModel model = launcher.buildModel();
    CtScanner scanner = new CtScanner() {};
    scanner.scan(model.getAllTypes().iterator().next());
    // This passes even on the buggy version because SimpleClass has no reference cycles
}
```

- **What the test should verify**: On the buggy version, the scanner call throws `java.lang.StackOverflowError`. On the fixed version, the scanner call completes normally. If possible, use `@Test(expected = StackOverflowError.class)` on the buggy version or assert that no exception is thrown on the fixed version. Since you cannot know which version is under test in the TG's context, structure the test to either:
  - Catch the `StackOverflowError` and fail the test with a descriptive message if thrown, OR
  - Use a timeout (e.g., `@Test(timeout = 10000)`) to prevent hanging, and let the test fail if the scanner doesn't complete within the timeout.

- **Additional guidance**: This bug occurs because `CtExecutableReference.getActualClass()` (or similar methods invoked during scanning) triggers `visitCtTypeReference` on the declaring type, whose type parameters are themselves `CtTypeParameterReference` that can link back to the original `CtExecutableReference`, creating a cycle. The key is to have the generic method signature `void onShardFailure(ShardOperationRequest request, ActionListener<Response> listener, ...)` where `Response` is a type parameter of the class, and the scanner visits each of these references in turn, recursing infinitely.
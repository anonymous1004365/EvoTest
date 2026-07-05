---
name: super-inheritance-hierarchy-function-no-classpath
description: When analyzing how a code transformation tool handles type accessors
  (CtTypeReference) in the presence of superclass inheritance hierarchies without
  classpath resolution, this skill teaches the TG to test that the tool correctly
  resolves template parameters even when the constructor body is empty.
code_tags:
- CONSTRUCTOR_BODY_EMPTINESS
- DEFAULT_CONSTRUCTOR_GENERATION
test_pattern: STATE_TEST
---

# super-inheritance-hierarchy-function-no-classpath

## Instructions

# Super-Inheritance Hierarchy Function No Classpath

## Instructions

- WHEN the TG encounters a code analysis/generation tool (like Spoon) that processes Java source code without full classpath resolution, and the code involves: (1) classes that extend a superclass with a generic type parameter, (2) methods that reference the superclass's generic type in their return type or parameter types, (3) constructors with an empty body (i.e., `Constructor() { }` or `Constructor() { super(); }`)
- THEN the TG should write a test that:
  1. Creates a minimal inheritance hierarchy: a generic superclass `AbstractSuper<T>` with a method returning `T`, and a concrete subclass `ConcreteSub extends AbstractSuper<String>` with no explicit constructor body or an empty constructor body
  2. Uses the tool to process the concrete subclass source code without classpath resolution
  3. Verifies that the tool correctly resolves the return type of the concrete subclass's method to `String` (not `T` or `Object`)
  4. Expects that on the buggy version, the tool would incorrectly report the type as unresolved (e.g., a `CtTypeReference` pointing to a different type, or a `NullTypeAccess` or similar), while on the fixed version it correctly resolves to `String`

- Common pitfalls:
  - Testing only with single-class scenarios (no inheritance hierarchy)
  - Testing only with classpath resolution available (the bug manifests specifically without classpath)
  - Testing the return type resolution but not the type parameter binding through the inheritance chain
  - Assuming that empty constructor bodies are correctly handled — the bug is specifically about how empty constructors interact with type resolution in inheritance without classpath

- Type hierarchy example:
  ```java
  // Superclass
  public abstract class AbstractSuper<T> {
      public abstract T getValue();
  }
  
  // Concrete subclass - buggy tool may fail to resolve the return type
  public class ConcreteSub extends AbstractSuper<String> {
      @Override
      public String getValue() {
          return "hello";
      }
  }
  ```

- What the test should verify: The tool's type accessor (e.g., `CtTypeReference`) for the overridden method's return type should point to `String` (correct) rather than failing with a `NullTypeAccess`, `T`, or `Object`.
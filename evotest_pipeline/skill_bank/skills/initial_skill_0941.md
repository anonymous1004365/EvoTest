---
name: property-removal-validation
description: When a `removeProperty(String)` method or equivalent property removal
  API is invoked, validate that it throws a `RepositoryException` (or appropriate
  checked exception) when the property does not exist. Many implementations silently
  succeed, violating the JCR 2.0 spec.
code_tags:
- NULL_CHECK
- VALIDATION
- EXCEPTION_HANDLING
test_pattern: EXCEPTION_TEST
---

# property-removal-validation

## Instructions

# Property Removal Validation

## Instructions

- WHEN the TG encounters a method signature like `void removeProperty(String name)` or `Property removeProperty(String name)` in a JCR `Node` implementation (or similar property-removal API)
- THEN it MUST write a test that:
  1. Creates or accesses a node that has **no property** with a given name (e.g., `"missingProp"`)
  2. Calls `removeProperty("missingProp")` on that node
  3. Asserts that a `RepositoryException` is thrown with the message containing "remove" or "missing" (e.g. using JUnit's `assertThrows(RepositoryException.class, () -> node.removeProperty("missingProp"))`)
  4. If the API supports it, also verify alternative removal approaches (e.g. calling `node.setProperty("missingProp", (String) null)` which should succeed) — the key is that the **direct removal method** must fail for non-existent properties

- Common pitfalls:
  - **Testing only `setProperty(name, null)`**: Some implementations allow removing properties by setting them to null, but the direct `removeProperty(String)` API must still throw when the property doesn't exist — these are two different code paths
  - **Not checking the exception type**: The exception type is `javax.jcr.RepositoryException`, not a runtime exception
  - **Assuming the property already exists**: Be explicit about starting from a fresh node with no properties set, to ensure the property truly doesn't exist

- Example (correct):
  ```java
  @Test
  public void testRemoveMissingProperty() throws RepositoryException {
      Node node = session.getRootNode().addNode("testNode");
      session.save();
      assertThrows(RepositoryException.class, () -> {
          node.removeProperty("nonExistentProp");
      });
  }
  ```

- Example (incorrect — misses the bug):
  ```java
  @Test
  public void testRemoveProperty() throws RepositoryException {
      Node node = session.getRootNode().addNode("testNode");
      node.setProperty("someProp", "value");
      session.save();
      // Only tests removal of an existing property — doesn't catch the bug
      Property removed = node.removeProperty("someProp");
      assertNotNull(removed);
  }
  ```
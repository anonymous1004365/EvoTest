---
name: checked-in-node-mutation-guard
description: WHEN testing node mutation after checkin (specifically setProperty with
  null values on checked-in/read-only nodes) THEN validate that write operations throw
  a proper RepositoryException. This skill helps catch bugs where node write protection
  is bypassed for certain method signatures.
code_tags:
- NULL_CHECK
- STATE_MUTATION
- VALIDATION
test_pattern: EXCEPTION_TEST
---

# checked-in-node-mutation-guard

## Instructions

# Checked-In Node Mutation Guard

## Instructions

- WHEN the TG encounters a scenario where a JCR node's writable state changes (e.g., after `session.getNode("/...").checkin()`), and a test attempts to mutate that node using a method such as `setProperty(String, String)`, `setProperty(String, Value)`, or `setProperty(String, String[])` passing `null` as the value
- THEN the TG MUST write a test that:
  1. Checks in the target node using e.g. `node.checkin()` or `session.getWorkspace().getVersionManager().checkin(absPath)` — this transitions the node to a read-only/checked-in state where mutation is forbidden by JCR spec (throwing `RepositoryException` with a message like "checked-in" or requiring a checked-out node)
  2. After checkin, attempts to call `setProperty(propertyName, null)` (where the value is `null`) on the checked-in node
  3. Asserts that a `RepositoryException` (or more specific subclass like `VersionException`) is thrown — using `assertThrows(RepositoryException.class, () -> {...})` or similar JUnit mechanism
- Common pitfalls: Testing only non-null values on a checked-in node and missing the specific case where `null` is passed as the property value; testing only on a checked-out or fresh node where mutation is allowed; assuming the `setProperty(String, String)` overload behaves the same as other overloads; forgetting to call `session.save()` before checkin if session-local transient changes exist.
- Correct example:
  ```java
  @Test
  public void testSetPropertyNullOnCheckedInNode() throws Exception {
      Node node = session.getRootNode().addNode("testNode");
      session.save();
      
      String path = node.getPath();
      session.getWorkspace().getVersionManager().checkin(path);
      
      // This should throw a RepositoryException
      assertThrows(RepositoryException.class, () -> {
          session.getNode(path).setProperty("someProp", (String) null);
      });
  }
  ```
- Incorrect example (missing the null-value edge case):
  ```java
  @Test
  public void testSetPropertyOnCheckedInNode() throws Exception {
      Node node = session.getRootNode().addNode("testNode");
      node.setProperty("prop", "value");
      session.save();
      
      String path = node.getPath();
      session.getWorkspace().getVersionManager().checkin(path);
      
      // Only testing non-null — misses the bug with null values
      assertThrows(RepositoryException.class, () -> {
          session.getNode(path).setProperty("otherProp", "someValue");
      });
  }
  ```
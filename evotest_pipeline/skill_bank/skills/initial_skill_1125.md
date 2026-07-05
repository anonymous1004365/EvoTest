---
name: node-type-constraint-violation-npe
description: When testing addNode() with a restricted primary node type name (e.g.,
  "nt:folder"), verify that a ConstraintViolationException is raised rather than a
  NullPointerException. The TG should identify where node type validation occurs and
  test that invalid node type assignments produce proper JCR exceptions.
code_tags:
- NULL_CHECK
- VALIDATION
- EXCEPTION_HANDLING
test_pattern: EXCEPTION_TEST
---

# node-type-constraint-violation-npe

## Instructions

# Node Type Constraint Violation Should Not Produce NullPointerException

## Instructions

- WHEN the TG encounters a test that calls `addNode(String relPath, String primaryNodeTypeName)` with a node type that has restricted child node definitions (e.g., `addNode("myNode", "nt:folder")` which only allows child nodes of specific types like `nt:file`)
- THEN the TG should verify that the exception thrown is `javax.jcr.nodetype.ConstraintViolationException`, not a `NullPointerException` or any other unexpected exception type
- Use `@Test(expected = ConstraintViolationException.class)` or an equivalent assertion that specifically expects `javax.jcr.nodetype.ConstraintViolationException` 
- The TG should add a child node with a type that violates the parent node type's allowed child node definitions (e.g., adding an `nt:unstructured` child to an `nt:folder` node, or adding any named child where the parent's primary node type restricts child node types)
- Common pitfall: Writing a test that passes with a `NullPointerException` but the JCR specification mandates `ConstraintViolationException`. Always check both: (a) that an exception IS thrown, and (b) that it's the CORRECT exception type (specifically `javax.jcr.nodetype.ConstraintViolationException`)
- Another common pitfall: Only testing successful `addNode` calls and not testing the constraint violation path at all. The JCR spec requires that invalid child node type assignments produce `ConstraintViolationException`.
- When adding nodes in a test, always use `session.getRootNode().addNode(...)` to create a test node with the restrictive type, then attempt to add an invalid child node type under it. Save and check that the correct exception type is raised.

### Correct Example (using JUnit 4 style):
```java
@Test(expected = ConstraintViolationException.class)
public void nodeType() throws RepositoryException {
    Session session = getAdminSession();
    Node folder = session.getRootNode().addNode("folder", "nt:folder");
    folder.addNode("child", "nt:unstructured");
    session.save();
}
```

### Incorrect Example (catches wrong exception):
```java
// BAD: This test would pass even if a NullPointerException is thrown
// instead of the required ConstraintViolationException
@Test(expected = Exception.class)
public void nodeType() throws RepositoryException {
    Session session = getAdminSession();
    Node folder = session.getRootNode().addNode("folder", "nt:folder");
    folder.addNode("child", "nt:unstructured");
    session.save();
}
```
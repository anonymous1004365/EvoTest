---
name: child-node-constraint-violation-exception-type
description: WHEN testing node type constraints that reject child nodes (e.g., nt:query),
  THEN the test must verify that javax.jcr.nodetype.ConstraintViolationException is
  thrown rather than a generic javax.jcr.RepositoryException. This skill covers writing
  tests that correctly validate the exception type when adding child nodes to node
  types that do not accept children, even when properties are also set.
code_tags:
- CONSTRAINT_VIOLATION_TYPE
- VALIDATION
test_pattern: STATE_TEST
---

# child-node-constraint-violation-exception-type

## Instructions

# Child Node Constraint Violation Exception Type

## Instructions

- WHEN the TG encounters code that validates child node constraints for JCR node types (e.g., `nt:query` which does not accept child nodes)
- THEN the TG should write a test that:
  1. Creates a node with a primary type that does not accept child nodes (e.g., `"nt:query"`)
  2. Sets required properties on that node (e.g., `jcr:statement`, `jcr:language`)
  3. Attempts to add a child node under that node with the same restricted type
  4. Calls `session.save()` and expects `javax.jcr.nodetype.ConstraintViolationException`
  5. Uses `@Test(expected = ConstraintViolationException.class)` annotation on the test method

- Common pitfalls to avoid:
  - **Wrong exception class**: Do NOT expect `javax.jcr.RepositoryException` — the bug causes this generic exception to be thrown instead of the specific `ConstraintViolationException`. The test MUST assert `ConstraintViolationException.class`.
  - **Missing property setup**: Simply adding a child node to `nt:query` (without setting properties) works for `illegalAddNode()`, but the bug triggering test `illegalAddNodeWithProps()` additionally sets `jcr:statement` and `jcr:language` properties on both the parent and child node. Without these properties, the bug might not be triggered.
  - **Not calling save**: The constraint violation is only detected on `session.save()`, not during the `addNode()` call itself.
  - **Assuming fix location**: The root cause may be in the validation layer (e.g., `TypeEditor` in the OAK core) rather than in the JCR session layer. Write integration-level tests that exercise the full commit pipeline.

### Correct example (Java/JUnit):
```java
@Test(expected = ConstraintViolationException.class)
public void illegalAddNodeWithProps() throws Exception {
    Session session = getAdminSession();
    Node root = session.getRootNode();
    ValueFactory vf = session.getValueFactory();

    Node n = root.addNode("q1", "nt:query");
    n.setProperty("jcr:statement", vf.createValue("statement"));
    n.setProperty("jcr:language", vf.createValue("language"));

    Node n2 = n.addNode("q2", "nt:query");
    n2.setProperty("jcr:statement", vf.createValue("statement"));
    n2.setProperty("jcr:language", vf.createValue("language"));

    session.save(); // Must throw ConstraintViolationException
}
```

### Incorrect example (would miss the bug):
```java
@Test(expected = RepositoryException.class) // WRONG! Too generic
public void illegalAddNodeWithProps() throws Exception {
    Session session = getAdminSession();
    Node root = session.getRootNode();
    Node n = root.addNode("q1", "nt:query");
    n.addNode("q2", "nt:query"); // Missing property setup
    session.save();
}
```
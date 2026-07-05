---
name: child-node-access-control-validation
description: When testing access control for child node retrieval in a JCR repository,
  this skill teaches how to verify that inaccessible child nodes are properly excluded
  from the children list, catching boundary bugs where the access check is bypassed
  for certain node types.
code_tags:
- VALIDATION
- NULL_CHECK
- BOUNDARY_CHECK
test_pattern: STATE_TEST
---

# child-node-access-control-validation

## Instructions

# Child Node Access Control Validation

## Instructions

- WHEN the TG encounters code that retrieves child nodes of a JCR node, especially when the code calls methods like `getNodes()`, `getChildNodes()`, or iterates over child items
- THEN the TG should test that child nodes to which the test user has NO READ access are properly excluded from the returned children collection. The test should:
  1. Set up a test user (e.g., a user with `rep:write` or specific access rights on a parent node but NOT on certain child nodes)
  2. Apply deny access control entries (e.g., `javax.jcr.security.Privilege.JCR_READ` denied) on one or more specific child paths
  3. Save and refresh the session to ensure permissions take effect
  4. Retrieve child nodes via `session.getNode(parentPath).getNodes()` or similar
  5. Iterate through the NodeIterator and collect the child node names
  6. Assert that the inaccessible child node(s) are NOT present in the returned list
  7. Assert that accessible child nodes ARE present in the returned list

- Common pitfalls to avoid:
  - Testing only with access-allowed scenarios and missing the denied-access case
  - Forgetting to call `session.save()` after setting up access control entries
  - Assuming the deny ACE applies without creating a proper test user session (use `getTestSession()` or similar helper)
  - Only testing with a single test user who has full privileges — use a limited-privilege test user
  - Not verifying BOTH that accessible nodes appear AND inaccessible nodes are absent from the result

### Correct example (Java):
```java
public void testChildNodesWithAccessCheck() throws Exception {
    // Setup: create child nodes
    Node parent = testSession.getNode("/test");
    Node childA = parent.addNode("accessible");
    Node childB = parent.addNode("inaccessible");
    testSession.save();

    // Deny read on childB
    AccessControlManager acMgr = adminSession.getAccessControlManager();
    String path = childB.getPath();
    AccessControlList acl = acMgr.getApplicablePolicies(path).nextAccessControlPolicy();
    Principal testPrincipal = testSession.getPrincipal();
    // deny read privilege
    acl.addAccessControlEntry(testPrincipal, new Privilege[]{Privilege.JCR_READ}, false);
    acMgr.setPolicy(path, acl);
    adminSession.save();

    // Test: get child nodes from test session
    NodeIterator iter = testSession.getNode("/test").getNodes();
    List<String> names = new ArrayList<>();
    while (iter.hasNext()) {
        names.add(iter.nextNode().getName());
    }

    // Verify
    assertTrue("Accessible child should be returned", names.contains("accessible"));
    assertFalse("Inaccessible child should NOT be returned", names.contains("inaccessible"));
}
```

### Incorrect example (misses the boundary bug):
```java
public void testChildNodes() throws Exception {
    // Only tests with full-access admin session — misses the bug
    NodeIterator iter = adminSession.getNode("/test").getNodes();
    assertTrue(iter.hasNext());
}
```
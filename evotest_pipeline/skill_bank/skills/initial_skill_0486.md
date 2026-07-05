---
name: sns-path-index-validation
description: When testing path resolution for same-name sibling (SNS) nodes, the TG
  should verify that indices like [1] and [2] are correctly handled for both node
  resolution and property access. This skill applies to path-based lookups where node
  indices must map to the correct child node among siblings.
code_tags:
- VALIDATION
- STATE_MUTATION
- BOUNDARY_CHECK
test_pattern: STATE_TEST
---

# sns-path-index-validation

## Instructions

# Same-Name Sibling (SNS) Path Index Validation

## Instructions

- WHEN the TG encounters code that resolves paths with same-name sibling indices (e.g., `/foo[1]/bar[2]`) or creates child nodes with identical names under the same parent
- THEN the TG should write a test that:
  1. Creates multiple child nodes with the same name under a parent (e.g., two nodes called "bar" under "/foo")
  2. Verifies that accessing `/foo[1]/bar[2]` resolves to the second child node
  3. Verifies that property access via SNS path works correctly (e.g., `/foo[1]/bar[2]/jcr:primaryType`)
  4. After removing one sibling, verifies the remaining node's index shifts correctly (e.g., after removing `bar[1]`, the former `bar[2]` should be accessible via `/foo/bar`)
  5. Asserts that removed nodes no longer exist via Session.nodeExists() and Session.propertyExists()
  6. Catches `RepositoryException` when accessing a non-existent SNS index path
- Common pitfalls:
  - Testing only single-node paths without SNS indices
  - Assuming node indices don't change after sibling removal
  - Only testing node existence, not property access through indexed paths
  - Forgetting to test that after removal, the SNS path that previously pointed to the removed node now throws or returns false

### Correct Example (Java/JCR API):
```java
// Create SNS nodes
Node parent = getAdminSession().getNode("/");
parent.addNode("foo");
Node foo = parent.getNode("foo");
foo.addNode("bar");
foo.addNode("bar");
getAdminSession().save();

// Verify SNS path resolution
assertTrue(getAdminSession().nodeExists("/foo[1]/bar[2]"));
assertNotNull(getAdminSession().getNode("/foo[1]/bar[2]"));
assertNotNull(getAdminSession().getProperty("/foo[1]/bar[2]/jcr:primaryType"));

// Remove first sibling and verify index shift
getAdminSession().getNode("/foo[1]/bar[1]").remove();
getAdminSession().save();
assertFalse(getAdminSession().nodeExists("/foo[1]/bar[1]"));
assertFalse(getAdminSession().propertyExists("/foo[1]/bar[1]/jcr:primaryType"));
assertTrue(getAdminSession().nodeExists("/foo/bar"));
assertNotNull(getAdminSession().getNode("/foo/bar"));
```

### Incorrect Example (too narrow — tests without SNS indices):
```java
// Only tests simple paths — misses the bug
Node foo = getAdminSession().getNode("/");
foo.addNode("bar");
// skips testing multiple same-name children and indexed paths
```
---
name: default-cluster-protection
description: Use when a service method should reject operations (especially DELETE)
  on a predefined or default resource. Test by invoking the forbidden operation and
  asserting an exception is thrown.
code_tags:
- VALIDATION
- STATE_MUTATION
test_pattern: EXCEPTION_TEST
---

# default-cluster-protection

## Instructions

# Default Cluster Protection

## Instructions

- WHEN the TG encounters a method that deletes a cluster/resource and there exists a predefined default value (e.g., a constant like `CLUSTER_NAME_DEFAULT` or `"default"`)
- THEN the TG should write a test that:
  1. Calls the delete method with the default cluster name/identifier
  2. Asserts that the operation fails by catching or expecting a runtime exception (e.g., `BadRequestException`, `IllegalArgumentException`, `BadRequestException`)
  3. Verifies that the deletion is NOT performed (e.g., the underlying service's delete method is never called, or the resource still exists)
  4. Checks the exception message contains relevant context (e.g., "default", "cannot be deleted")
- Common pitfalls:
  - Testing only with valid/non-default identifiers, missing the forbidden-default case
  - Expecting success instead of failure for the default resource
  - Not checking that the system state remains unchanged after the failed operation
  - Forgetting to verify the exception type or message, relying only on "no exception thrown"

### Correct Example (Analogous to ClusterControllerTest.testDeleteDefaultFail)
```java
@Test(expected = BadRequestException.class)
public void testDeleteDefaultClusterFails() {
    // Arrange: set up controller with a real or mock service
    String defaultClusterName = "default";
    
    // Act: attempt to delete the default cluster
    controller.delete(defaultClusterName);
    
    // Assert: @Test(expected = ...) handles the expected exception
    // Also verify: service.delete() was never called
}
```

### Incorrect Example
```java
@Test
public void testDeleteDefaultCluster() {
    String defaultClusterName = "default";
    
    // BUG: This test passes on the buggy version because no 
    // validation exists, but should fail — the default cluster
    // must never be deletable
    controller.delete(defaultClusterName);
    
    // No assertion — silently passes even on buggy code
}
```
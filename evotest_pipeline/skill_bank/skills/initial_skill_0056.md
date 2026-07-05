---
name: cluster-repository-id-creation-validation
description: When testing a method that lazily creates a cluster repository ID (e.g.,
  getOrCreateId) which reads a property from a node store and falls back to generating
  a UUID, test that it works correctly when no prior cluster ID exists. Use STATE_TEST
  pattern to verify both the initial creation path and the read-existing path.
code_tags:
- CLUSTER_ID_INITIALIZATION
- CONCURRENCY
- STATE_MUTATION
test_pattern: STATE_TEST
---

# cluster-repository-id-creation-validation

## Instructions

# Cluster Repository ID Creation Validation

## Instructions

- WHEN the TG encounters a method that reads a cluster/repository ID property from a node store and falls back to generating a new ID (e.g., `UUID.randomUUID().toString()`) if none exists
- THEN the TG should test the scenario where no cluster ID has been previously persisted. Specifically:
  - Create a NodeStore (e.g., `MemoryDocumentStore` + `DocumentNodeStore`) WITHOUT setting any cluster ID in the repository
  - Call the ID creation method (e.g., `ClusterRepositoryInfo.getOrCreateId(ds1)`)
  - Verify that the method returns a non-null String (since it generates a new UUID on first invocation)
  - Verify that the returned value matches the expected format of a UUID (e.g., 36 characters with hyphens)
  - Call the method again on the same store and assert that the same ID is returned on subsequent calls, verifying idempotent behavior

- WHEN the TG is testing a `getOrCreateId`-style method that uses `NodeStore.merge()` and handles `CommitFailedException`
- THEN the TG should also test the read-after-write path:
  - Manually set a clusterId property via `NodeBuilder` (e.g., `builder.child(":clusterConfig").setProperty(":clusterId", "yyyyyyy")`)
  - Call the ID creation method and verify it reads and returns the custom value instead of generating a new one
  - This confirms the "read existing" code path works correctly

- Common pitfalls to avoid:
  - Testing only the "happy path" where the cluster ID already exists, without testing the initial creation path
  - Not verifying that the first return value is non-null when no prior ID exists
  - Assuming the method returns null when no cluster ID is registered — the bug was that the method previously returned null (see the commented-out test `checkGetIdWhenNotRegistered`), but the fix changed it to always generate and persist an ID, so it should never return null now
  - Not calling `runBackgroundOperations()` on the DocumentNodeStore before reading, as changes may not be visible otherwise

- Correct example:
  ```java
  // Test that getOrCreateId creates a new ID when none exists
  MemoryDocumentStore store = new MemoryDocumentStore();
  DocumentNodeStore ds1 = builderProvider.newBuilder()
      .setAsyncDelay(0)
      .setDocumentStore(store)
      .setClusterId(1)
      .getNodeStore();
  String id = ClusterRepositoryInfo.getOrCreateId(ds1);
  Assert.assertNotNull(id);  // should NOT be null - creates a new UUID
  Assert.assertEquals(36, id.length());  // standard UUID length
  
  // Call again - should return same ID
  String id2 = ClusterRepositoryInfo.getOrCreateId(ds1);
  Assert.assertEquals(id, id2);  // idempotent
  ```

- Incorrect example (would miss the bug):
  ```java
  // WRONG: Only tests reading an existing ID
  MemoryDocumentStore store = new MemoryDocumentStore();
  DocumentNodeStore ds1 = ...;
  // Pre-set the cluster ID
  // ... then call getOrCreateId, missing the initial creation path entirely
  ```
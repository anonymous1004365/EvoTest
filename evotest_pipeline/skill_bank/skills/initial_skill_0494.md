---
name: node-type-mutation-during-upgrade
description: When testing repository upgrade logic that mutates node types (e.g.,
  splitting groups by changing primary type), verify that upgrade operations correctly
  transform node type and that post-upgrade type checks pass. This skill catches bugs
  where the upgrade process sets intermediate or wrong node types.
code_tags:
- NODE_TYPE_CONVERSION
- STATE_MUTATION
test_pattern: STATE_TEST
---

# node-type-mutation-during-upgrade

## Instructions

# Node Type Mutation During Upgrade

## Instructions

- WHEN the TG encounters a repository upgrade process that mutates node primary types (e.g., changing `rep:MemberReferencesList` nodes or splitting `rep:Group` nodes during upgrade), and the test involves:
  - Building a source repository with specific node content (e.g., groups with members, member reference lists)
  - Running a repository copy/upgrade (e.g., `RepositoryUpgrade.copy(source, target)`)
  - Verifying the structure and types of nodes in the target repository after upgrade
  
- THEN the TG should write a test that:
  1. Creates a source repository (e.g., via `ContentRepositoryBuilder` or similar builder pattern) with the relevant nodes, including the specific node types in use (e.g., `rep:Group`, `rep:MemberReferences`, `rep:MemberReferencesList`).
  2. Runs the upgrade process (e.g., `RepositoryUpgrade.copy(source, target)`).
  3. After upgrade, reads back the migrated nodes from the target repository and asserts that they have the **expected final primary type** (e.g., `rep:MemberReferencesList`), not an intermediate or incorrect type.
  4. The test should fail on the buggy version (e.g., with message "Migrated group needs to be new node type" or similar) because the node type was not properly updated during upgrade.
  5. Includes a separate test method specifically for verifying the node types of migrated content (e.g., named `verifyGroupNodeTypes`).

- Common pitfalls to avoid:
  - Do NOT test only that the upgrade runs without exceptions — also verify the **resulting state** of individual nodes.
  - Do NOT assume that because content is present after upgrade, its node type is correct — the bug may leave nodes with the **old/original** primary type instead of the **new** expected type.
  - Do NOT forget to run the upgrade process between setup and verification — the bug manifests only after the upgrade transformation.
  - Do NOT test only a single presence/absence check — explicitly call `getNodeState().getProperty(...)` and compare the `Value` of `jcr:primaryType` against the expected node type name.
  - Do NOT rely on `toString()` or logging to verify types — use explicit assertions on node state properties.

- Example of correct test structure:
  ```java
  @Test
  public void verifyGroupNodeTypes() throws Exception {
      // Setup: create source repository with group nodes
      // Run upgrade: RepositoryUpgrade.copy(source, target)
      // Verify: check primary type of migrated nodes
      assertEquals("rep:MemberReferencesList", 
          targetTree.getChild("group").getProperty("jcr:primaryType").getValue().getString());
  }
  ```

- Example of incorrect/insufficient test:
  ```java
  @Test
  public void testUpgradeRuns() throws Exception {
      RepositoryUpgrade.copy(source, target);  // No assertions about node types!
  }
  ```
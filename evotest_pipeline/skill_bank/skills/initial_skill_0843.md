---
name: version-history-upgrade-order-dependency
description: WHEN testing repository upgrade code that manages version histories or
  version storage nodes, THEN verify that version history entries are correctly preserved
  and ordered after the upgrade. This skill prevents bugs where version history node
  ordering is lost or altered during upgrade due to state mutation and order dependency
  issues.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- NULL_CHECK
test_pattern: STATE_TEST
---

# version-history-upgrade-order-dependency

## Instructions

# Version History Upgrade Order Preservation

## Instructions

- WHEN the TG encounters code that upgrades a repository's version storage (e.g., version histories, version nodes, `jcr:frozenNode` children), or code that copies/migrates version history nodes from a source repository to a target repository
- THEN the TG should write a test that:
  1. Creates version histories with multiple versions in a source repository
  2. Performs the upgrade/migration operation
  3. Verifies that ALL version history entries from the source are present in the target
  4. Verifies that the version history entries appear in the CORRECT ORDER (the same order as in the source)
  5. Uses child node name/identifier comparison rather than just checking presence — specifically verify that the *identifiers* or *names* of version history children match expected values in order

- Common pitfalls to avoid:
  - Testing only that version history nodes exist after upgrade, without checking their ORDER
  - Testing with only a single version entry (which cannot reveal ordering bugs)
  - Testing with version histories that have no child entries
  - Assuming node iteration order is preserved without explicit verification
  - Checking only content properties but not the structural ordering of child nodes

- Example of a CORRECT test approach:
```java
// Create version histories with multiple entries before upgrade
Node versionable = session.getRootNode().addNode("test");
versionable.addMixin("mix:versionable");
session.save();
Version v1 = versionable.checkin();
VersionManager vm = session.getWorkspace().getVersionManager();
VersionHistory vh = vm.getVersionHistory(versionable.getPath());

// After upgrade operation:
Node upgradedVh = ... // get the upgraded version history
NodeIterator children = upgradedVh.getNodes();
List<String> childIds = new ArrayList<>();
while (children.hasNext()) {
    childIds.add(children.nextNode().getIdentifier());
}
// Verify specific identifiers exist in expected order
assertEquals("Version history child nodes missing or out-of-order",
    Arrays.asList("expected-id-1", "expected-id-2", "expected-id-3"), childIds);
```

- Example of an INCORRECT test (would miss the bug):
```java
// Only checking that something exists, not what or in what order
assertTrue(upgradedVh.hasNodes()); // WRONG: doesn't verify content or order
```
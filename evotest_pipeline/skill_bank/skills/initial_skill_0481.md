---
name: index-definition-child-removal-during-reindex
description: When reindexing an index node, child nodes of the index definition may
  be removed. The TG should test that removing a child property/index-definition node
  does NOT interfere with the ongoing reindex traversal (e.g., ConcurrentModificationException
  or missed reindex). This skill teaches verifying iteration stability when performing
  structural changes to index definition subtrees during reindex.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- STATE_MUTATION
- VALIDATION
test_pattern: STATE_TEST
---

# index-definition-child-removal-during-reindex

## Instructions

# Index Definition Child Removal During Reindex

## Instructions

WHEN the TG encounters code that performs **reindex** of an index node where child nodes of the index definition (e.g., property index definitions, configuration nodes) are being added or removed as part of the reindex logic,
THEN the TG should write a **state test** that:
1. Creates an index definition node with multiple child property/index-definition nodes.
2. Triggers a reindex operation that iterates over those child nodes (e.g., via `NodeState.getChildNodeNames()` or `getChildNodeEntries()`) and removes one or more of them during iteration.
3. Verifies that the reindex completes successfully without throwing a `ConcurrentModificationException`, missing any child nodes, or leaving the index definition in an inconsistent state.
4. Specifically test that after removal, the reindex has correctly processed the remaining child nodes and the removed node's state is properly reflected in the updated index state.

Common pitfalls to avoid:
- Testing only the happy path where no structural changes occur during reindex.
- Assuming that all child iteration uses fail-fast iterators — some internal Oak iterators do NOT throw `ConcurrentModificationException` on concurrent modification but silently skip or duplicate entries.
- Forgetting to check both: (a) that the removed child is properly gone from the result, AND (b) that remaining children are still correctly indexed/reindexed.
- Only testing removal without also testing what happens to the reindex state for the removed node (it should not be reindexed if removed mid-iteration).

**Correct example (conceptual):**
```java
// Setup: index definition with two property definitions
Tree indexDef = root.getTree("/oak:index/testIndex");
Tree prop1 = indexDef.addChild("prop1");
prop1.setProperty("propertyNames", "foo");
Tree prop2 = indexDef.addChild("prop2");
prop2.setProperty("propertyNames", "bar");

// Trigger reindex which iterates children and removes one
// Verify no exception and correct state
indexDef.setProperty("reindex", true);
root.commit();

// After commit, assert the removed child is gone
assertFalse(indexDef.hasChild("prop1"));
// Assert remaining child is still present
assertTrue(indexDef.hasChild("prop2"));
```

**Incorrect example (too simplistic):**
```java
// Only tests reindex without removal
Tree indexDef = root.getTree("/oak:index/testIndex");
indexDef.setProperty("reindex", true);
root.commit();
// Does not test what happens when child nodes are removed during reindex
```
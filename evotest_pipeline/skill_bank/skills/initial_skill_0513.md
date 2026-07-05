---
name: content-mirror-index-pruning
description: When testing a content-mirror index store strategy that prunes orphaned
  intermediate nodes after removing paths, write tests that verify the pruning logic
  correctly keeps shared subtrees when siblings still exist and correctly removes
  subtrees only when the last leaf is removed.
code_tags:
- TREE_PRUNING_AFTER_REMOVAL
test_pattern: STATE_TEST
---

# content-mirror-index-pruning

## Instructions

# Content Mirror Index Pruning

## Instructions

WHEN the TG encounters a `ContentMirrorStoreStrategy` (or similar index strategy) that has a `prune()` method that removes empty intermediate nodes from a tree after a `remove` operation, THEN the TG should write a state-based test that simulates inserting and removing multiple paths under the same key and asserts the exact tree state after each removal.

- Use a `NodeBuilder` and `EMPTY_NODE` as the starting root. Create a `ContentMirrorStoreStrategy` instance via the no-arg constructor (which defaults index content node name to `:index`).
- Insert paths like `"a/b/c"`, `"a/b/d"`, `"d/e/f"` under a common key (e.g., `"key"`) using `store.update(index, path, null, null, EMPTY, KEY)`.
- After insertion, verify each path's child node (e.g., `"key/a/b/c"`) exists and has a `"match"` property set to `true`.
- After removal of a path (e.g., `store.update(index, "a/b/c", null, null, KEY, EMPTY)`), verify:
  1. That the leaf node no longer has the `"match"` property.
  2. That sibling paths under the same intermediate parent (e.g., `"a/b/d"`) still exist and still have `"match"` property.
  3. That the intermediate parent (e.g., `"a/b"`) is NOT removed as long as it has at least one child with a `"match"` property.
- After removing the LAST remaining leaf under a subtree (e.g., remove `"a/b/d"` after `"a/b/c"` was already removed), verify that the entire intermediate subtree (e.g., `"key/a"`, `"key/a/b"`) is pruned away — the parent should NOT have the intermediate child node anymore.
- After removing all paths including the root (e.g., `"/"`), verify that the key node itself is removed entirely and the builder has zero children: `Assert.assertEquals(0, builder.getChildNodeCount(1))`.
- Common pitfalls to avoid:
  - Testing only single-path insertion/removal without verifying sibling retention.
  - Forgetting that intermediate nodes are shared — removing one leaf should NOT remove siblings.
  - Assuming the key node is removed when only some children are removed — the key node should only disappear when ALL paths under it (including root `""`) are removed.
  - Not checking that the `"match"` property removal happens before the `prune()` call — the `prune()` logic checks for nodes without children that have `"match"` set.

## Correct Example

```java
IndexStoreStrategy store = new ContentMirrorStoreStrategy();
NodeState root = EMPTY_NODE;
NodeBuilder builder = root.builder();
Supplier<NodeBuilder> index = () -> builder;

// Insert multiple paths under same key
store.update(index, "a/b/c", null, null, EMPTY, KEY);
store.update(index, "a/b/d", null, null, EMPTY, KEY);

// Both exist
Assert.assertTrue(builder.child("key").child("a").child("b").child("c").hasProperty("match"));
Assert.assertTrue(builder.child("key").child("a").child("b").child("d").hasProperty("match"));

// Remove one leaf — sibling must survive
store.update(index, "a/b/c", null, null, KEY, EMPTY);
Assert.assertFalse(builder.child("key").child("a").child("b").child("c").hasProperty("match"));
Assert.assertTrue(builder.child("key").child("a").child("b").child("d").hasProperty("match"));
// Intermediate nodes "key/a/b" must still exist (they have another child with match)
Assert.assertTrue(builder.child("key").child("a").hasChildNode("b"));

// Remove last leaf — entire subtree must be pruned
store.update(index, "a/b/d", null, null, KEY, EMPTY);
Assert.assertFalse(builder.child("key").hasChildNode("a"));  // "a" is entirely removed
```

## Incorrect Example (Missing Sibling Retention Check)

```java
// BAD: Only tests that removal worked for the specific path
store.update(index, "a/b/c", null, null, EMPTY, KEY);
store.update(index, "a/b/d", null, null, EMPTY, KEY);
store.update(index, "a/b/c", null, null, KEY, EMPTY);
// ❌ Missing assertion that "a/b/d" still exists untouched
// ❌ Missing assertion that intermediate nodes are kept when siblings remain
```
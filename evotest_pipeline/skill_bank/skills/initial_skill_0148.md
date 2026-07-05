---
{}
---

---
name: node-state-diff-comparison-contract
description: WHEN testing NodeState.compareAgainstBaseState interactions, THEN verify the implementation correctly reports childNodeAdded, childNodeDeleted, and childNodeChanged events for MapRecord nodes with many children, especially when the base node has mulitple levels of subtree modifications. Common pitfall: writing a test that only checks top-level property differences without exercising map-level tree diffing.
code_tags: ['NODE_STATE_DIFF_COMPARISON']
test_pattern: INTERACTION_TEST
---

# node-state-diff-comparison-contract

## Instructions

# NodeState Diff Comparison Contract

## Instructions

- WHEN testing a `NodeState.compareAgainstBaseState(NodeState base, NodeStateDiff diff)` implementation that delegates to `AbstractNodeState.compareAgainstBaseState(this, base, diff)`:
  - THEN verify the implementation correctly reports all three diff event types: `childNodeAdded`, `childNodeDeleted`, and `childNodeChanged`.
  - The test must exercise map-level tree diffing by constructing a `before` NodeState with multiple child nodes (e.g., 8+ children) and an `after` NodeState where some children are added, some removed, and some modified at deeper levels (subtree changes inside child nodes).
  - Create a custom `NodeStateDiff` implementation that records which events were invoked, and assert the expected counts and properties of each event type.
  - Use a `ChildNodeStateDiff` (inner diff) to verify that `childNodeChanged` on a node correctly descends into that node's children to report add/delete/change events within the subtree.
  - Concrete example: Create 8 child nodes (e.g., "a" through "h"), build a base state with properties on some children, build a modified state where one child is added ("i"), one child is removed (e.g., "g"), and one child's subtree is modified (e.g., change a property on child "c"), then assert that `childNodeAdded("i", ...)`, `childNodeDeleted("g", ...)`, and `childNodeChanged("c", ..., ..., innerDiff)` are all called, and the inner diff captures the property change.
  - Common pitfalls: (1) Testing only property-level diffs (propertyAdded/propertyChanged/propertyDeleted) while ignoring child node events — the bug is specifically in the map/tree-diffing code path. (2) Using too few children (e.g., 2-3) which may not trigger the buggy code path — use 8+ children to ensure the segment map's internal structure is exercised. (3) Not providing a custom `NodeStateDiff` to capture the actual invocation — the test must verify which methods of the diff were called, not just that no exception was thrown. (4) Assuming `compareAgainstBaseState` on a single-node setup (only one child) exercises the same code path as a multi-child map — the `MapRecord` code specifically has branching logic for maps with many entries that can diverge from the fixed version.

  Correct example pattern:
  ```java
  // Build 8+ children
  Set<String> children = new HashSet<>(Arrays.asList("a","b","c","d","e","f","g","h"));
  // Add properties/content to each child
  Map<String, NodeState> childMap = new HashMap<>();
  for (String name : children) {
      childMap.put(name, new NodeState(...));
  }
  // Build base state with these children
  NodeState base = new SegmentNodeState(..., mapWithChildren(childMap));

  // Modify: remove "g", add "i", change property on "c"
  Map<String, NodeState> modifiedMap = new HashMap<>(childMap);
  modifiedMap.remove("g");
  modifiedMap.put("i", new NodeState(...));
  // Change "c" — add a new property to it
  modifiedMap.put("c", new NodeStateBuilder(childMap.get("c")).setProperty("x", "y").getNodeState());

  NodeState after = new SegmentNodeState(..., mapWithChildren(modifiedMap));

  // Custom diff to record events
  CollectingNodeStateDiff diff = new CollectingNodeStateDiff();
  after.compareAgainstBaseState(base, diff);

  assertTrue(diff.added.contains("i"));
  assertTrue(diff.deleted.contains("g"));
  assertTrue(diff.changed.containsKey("c"));
  ```

  Incorrect example pattern:
  ```java
  // Only 2 children, only tests property difference at top level
  NodeState base = new NodeStateBuilder().setProperty("p", "v1").getNodeState();
  NodeState after = new NodeStateBuilder().setProperty("p", "v2").getNodeState();
  // This only tests property level, NOT child node level
  // The bug lives specifically in the child-node map traversal code
  ```
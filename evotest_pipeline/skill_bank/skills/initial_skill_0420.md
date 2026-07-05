---
name: child-node-reordering-after-remove
description: When testing node ordering operations like `orderBefore` after removing
  and re-adding child nodes, verify that the internal child order tracking correctly
  reflects the re-added node's position. The TG should test adding nodes with specific
  names, removing them, re-adding them with the same name, then calling orderBefore
  to reorder — expecting the order to work correctly without throwing IndexOutOfBoundsException
  or returning unexpected iteration order.
code_tags:
- COLLECTION_ITERATION
- STATE_MUTATION
- ORDER_DEPENDENCY
test_pattern: STATE_TEST
---

# child-node-reordering-after-remove

## Instructions

# Child Node Reordering After Remove-and-Readd

## Instructions

- WHEN the TG encounters a `NodeBuilder` that creates child nodes with `setChildNode(name)` or `addNode(name)` and then orders them with `orderBefore(name1, name2)` — especially when nodes are removed and later re-added with the same name
- THEN the TG should write a test that:
  1. Creates a root builder (e.g., `MemoryNodeBuilder` from `oak-store-spi`)
  2. Adds at least two child nodes with distinct names (e.g., "a" and "b")
  3. Removes one of them (e.g., `builder.getChildNode("b").remove()`)
  4. Re-adds a child node with the same name (e.g., `builder.setChildNode("b")`)
  5. Calls `orderBefore("b", "a")` to move "b" before "a"
  6. Verifies the order by checking `builder.getChildNodeNames()` returns `["b", "a"]` (not `["a", "b"]`)
- The test should verify that the order before removal and after re-add-and-reorder are consistent — specifically that the re-added node can be ordered before existing siblings without throwing an exception
- **Common pitfalls to avoid:**
  - Testing only the initial order without testing reordering after remove-and-readd
  - Assuming `orderBefore` on a freshly re-added node silently succeeds — it may throw `IndexOutOfBoundsException` due to stale internal state
  - Not checking `getChildNodeNames()` after the reorder to confirm the actual iteration order changed
  - Testing only with a single child node (reordering requires at least two children)

### Correct example (what the TG should write):
```java
NodeBuilder builder = new MemoryNodeBuilder(rootState);
builder.setChildNode("a");
builder.setChildNode("b");

// Remove and re-add "b"
builder.getChildNode("b").remove();
builder.setChildNode("b");

// Reorder: "b" should come before "a"
builder.getChildNode("b").orderBefore("a");

Iterable<String> names = builder.getChildNodeNames();
List<String> list = new ArrayList<>();
for (String n : names) {
    list.add(n);
}
assertEquals("b should be before a after reorder", "b", list.get(0));
assertEquals("a should be after b after reorder", "a", list.get(1));
```

### Incorrect example (what the TG might write without this skill):
```java
NodeBuilder builder = new MemoryNodeBuilder(rootState);
builder.setChildNode("a");
builder.setChildNode("b");

// Only tests initial order without remove/readd — passes even with the bug
builder.getChildNode("b").orderBefore("a");
Iterable<String> names = builder.getChildNodeNames();
// This doesn't catch the bug because it doesn't remove and re-add "b" first
```
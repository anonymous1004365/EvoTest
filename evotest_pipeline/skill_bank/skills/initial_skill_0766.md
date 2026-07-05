---
name: parse-tree-node-range-correction
description: When building a parse tree node that wraps a single child node inside
  parentheses, ensure the parent node's range end index is set correctly after removing
  the child from the result list. The parent node should span from its start index
  to the position just before the closing parenthesis.
code_tags:
- VALIDATION
- NULL_CHECK
- BOUNDARY_CHECK
test_pattern: PARAMETRIC_TEST
---

# parse-tree-node-range-correction

## Instructions

# Parse Tree Node Range Correction

## Instructions

- WHEN the TG encounters a method that builds a parse tree by processing tokens and constructing nodes with `start` and `end` position indices (e.g., `ColumnVisibility.Node` with fields `start`, `end`, `children`, `type`)
- THEN the TG should write a test that constructs a visibility expression containing a term wrapped in parentheses (e.g., `(ONE)`) and verifies that the resulting parse tree node (of type `NodeType.OR` or `NodeType.AND` or `NodeType.EMPTY`) has its `end` field correctly set, not just its `start` and `children` fields
  - Specifically: when a parenthesized group reduces to a single child (the parentheses are removed and the child is kept), the parent node's `end` should be set to `index - 1` (position of the closing parenthesis), NOT left as a stale default value
  - Verify by calling `getParseTree()` on the expression and checking that the returned `Node` has `end >= start` and that the `start`/`end` range covers the entire original expression including parentheses
- Include what mistakes to avoid (common pitfalls):
  - Do **not** test only with simple terms like `"ONE"` that lack parentheses — these don't exercise the bug
  - Do **not** test only with compound expressions like `(ONE|TWO)` that have multiple children — these may take a different code path
  - Do **not** forget to verify the `end` field of the top-level node returned by `getParseTree()`; the bug leaves `end` unset (default 0) when a parenthesized expression wraps a single term
- Concrete examples:

**Correct test (catches the bug):**
```java
@Test
public void testParseTreeAfterParentheses() {
    ColumnVisibility.ColumnVisibility c = new ColumnVisibility.ColumnVisibility("(ONE)");
    ColumnVisibility.Node node = c.getParseTree();
    Assert.assertEquals(ColumnVisibility.NodeType.EMPTY, node.type);
    Assert.assertEquals(0, node.start);
    Assert.assertEquals(4, node.end);  // "(ONE)" has length 5, end should be 4 (index - 1)
    Assert.assertEquals(1, node.children.size());
    ColumnVisibility.Node child = node.children.get(0);
    Assert.assertEquals(ColumnVisibility.NodeType.TERM, child.type);
    Assert.assertEquals(1, child.start);
    Assert.assertEquals(3, child.end);
}
```

**Incorrect test (misses the bug):**
```java
@Test
public void testParseTreeAfterParentheses() {
    ColumnVisibility.ColumnVisibility c = new ColumnVisibility.ColumnVisibility("(ONE)");
    ColumnVisibility.Node node = c.getParseTree();
    Assert.assertEquals(ColumnVisibility.NodeType.EMPTY, node.type);
    Assert.assertEquals(0, node.start);
    // Missing: assertion on node.end — this won't catch the bug
    Assert.assertEquals(1, node.children.size());
    // Only checks children, not the parent node's end index
}
```
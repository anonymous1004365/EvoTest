---
name: jsop-diff-depth-limitation
description: When computing JSON diffs with a depth parameter, the diff algorithm
  must stop recursing into child nodes that exceed the specified depth. Without proper
  depth enforcement, the diff incorrectly includes nested children beyond the requested
  depth, causing test assertions about excluded subtrees to fail.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
- STATE_MUTATION
test_pattern: PARAMETRIC_TEST
---

# jsop-diff-depth-limitation

## Instructions

# Jsop Diff Depth Limitation

## Instructions

WHEN the TG encounters code that generates a JSON diff (JsopDiff) between two node states with a `depth` parameter that limits how deep the diff should traverse:

- THEN the TG should create a test that verifies the diff result only contains nodes up to the specified depth, and that nodes at depth > the specified limit are excluded from the output.

- The test must set up a tree with at least 3 levels of nesting (e.g., root → child → grandchild), compute a diff with `depth=1` (root level only), and assert that the grandchild content is NOT present in the diff output.

- Use concrete values: if the diff is computed via `new JsopDiff(path, depth)` or `JsopDiff.diffToJsop(before, after, path, depth)`, verify that setting `depth=1` on a 3-level tree produces output that does NOT include the grandchild's properties.

- The test should compare the actual diff string against an expected string that excludes the deep content. For example, if the root has a child `/b` with a grandchild `x`, a depth-limited diff should not include `"x":{"l":2,"y":{}}`.

- Common pitfall #1: Testing only with depth=0 or depth=-1 (unlimited), which does not exercise the depth-limiting logic in production.
- Common pitfall #2: Assuming the depth parameter applies only to the initial root traversal — in fact, it must stop further recursion at each level.
- Common pitfall #3: Only testing that the diff includes expected nodes at the given depth, without also testing that deeper nodes are excluded.

### Example (Correct)

```java
// Given a tree with structure: root → /b → /b/x (with property l=2)
// When diffing with depth=1 (only root level)
String diff = JsopDiff.diffToJsop(before, after, "/", 1);
// Then deep children should NOT appear
assertTrue("Diff should not contain grandchild x", !diff.contains("\"x\""));
// Expected: "+ \"/b\":{\"l\":1}" (no x)
```

### Example (Incorrect)

```java
// WRONG: Only tests diff at root level without depth limit
String diff = JsopDiff.diffToJsop(before, after, "/", -1);
// This passes but does not verify depth enforcement
assertEquals("+\"/b\":{\"l\":1,\"x\":{\"l\":2,\"y\":{}}}", diff);
// This test would pass on the BUGGY version too, missing the bug entirely
```
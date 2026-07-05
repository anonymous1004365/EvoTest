---
name: plugin-execution-ordering-preservation
description: When merging plugin executions from parent to child, the original insertion
  order of both parent and child executions must be preserved, not sorted alphabetically
  by ID. This skill teaches how to test that mergePluginDefinitions preserves execution
  ordering.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- STATE_MUTATION
- ORDER_DEPENDENCY
test_pattern: STATE_TEST
---

# plugin-execution-ordering-preservation

## Instructions

# Plugin Execution Ordering Preservation

## Instructions

- WHEN the TG encounters code that merges PluginExecution lists from a parent Plugin into a child Plugin via `mergePluginDefinitions(child, parent, ...)` or similar methods
- THEN the TG should write a test that:
  1. Creates a parent Plugin with at least two PluginExecutions whose IDs sort in reverse alphabetical or non-intuitive order (e.g., `"zzz"` first, `"yyy"` second)
  2. Creates a child Plugin with at least two PluginExecutions whose IDs also sort in a different order (e.g., `"bbb"` first, `"aaa"` second)
  3. Calls the merge method with `handleAsInheritance=false`
  4. Verifies that `child.getExecutions().size()` equals the sum of parent and child execution counts (e.g., `assertEquals(4, child.getExecutions().size())`)
  5. Verifies that the merged list preserves the parent executions first in their original insertion order, followed by child executions in their original insertion order — NOT sorted alphabetically by ID
  6. Uses `assertSame()` (or identity check) for each execution object to verify that the exact same objects appear in the expected positions: `assertSame(parentExecution1, child.getExecutions().get(0))`, `assertSame(parentExecution2, child.getExecutions().get(1))`, `assertSame(childExecution1, child.getExecutions().get(2))`, `assertSame(childExecution2, child.getExecutions().get(3))`

- Common pitfalls to avoid:
  - ❌ Testing execution ordering with execution IDs that are already in alphabetical order (e.g., `"aaa"` then `"bbb"`) — this hides the bug because the sorted map happens to produce the same order
  - ❌ Using only one execution per plugin — the ordering bug only manifests with multiple executions
  - ❌ Only checking the size of the merged list without verifying the actual order and identity of each element
  - ❌ Using `assertEquals()` instead of `assertSame()` — the bug is about which specific PluginExecution objects end up in which positions

### Correct Example

```java
Plugin parent = new Plugin();
parent.setArtifactId("testArtifact");
parent.setGroupId("testGroup");
parent.setVersion("1.0");

PluginExecution parentExecution1 = new PluginExecution();
parentExecution1.setId("zzz");  // Would sort last alphabetically
PluginExecution parentExecution2 = new PluginExecution();
parentExecution2.setId("yyy");  // Would sort last alphabetically

parent.addExecution(parentExecution1);
parent.addExecution(parentExecution2);

Plugin child = new Plugin();
child.setArtifactId("testArtifact");
child.setGroupId("testGroup");
child.setVersion("1.0");

PluginExecution childExecution1 = new PluginExecution();
childExecution1.setId("bbb");
PluginExecution childExecution2 = new PluginExecution();
childExecution2.setId("aaa");

child.addExecution(childExecution1);
child.addExecution(childExecution2);

ModelUtils.mergePluginDefinitions(child, parent, false);

assertEquals(4, child.getExecutions().size());
assertSame(parentExecution1, child.getExecutions().get(0));
assertSame(parentExecution2, child.getExecutions().get(1));
assertSame(childExecution1, child.getExecutions().get(2));
assertSame(childExecution2, child.getExecutions().get(3));
```

### Incorrect Example

```java
// BAD: IDs are already in alphabetical order — won't catch sorting bug
PluginExecution e1 = new PluginExecution(); e1.setId("aaa");
PluginExecution e2 = new PluginExecution(); e2.setId("bbb");
parent.addExecution(e1);
parent.addExecution(e2);

// BAD: Only checking size, not order
assertEquals(2, child.getExecutions().size());

// BAD: Using assertEquals instead of assertSame — doesn't verify identity
assertEquals(parentExecution1, child.getExecutions().get(0));
```
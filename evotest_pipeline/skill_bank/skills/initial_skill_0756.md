---
name: multi-valued-property-index-update
description: When an indexed property changes from multi-valued to single-valued (or
  vice versa), the TG should test that the index correctly removes old entries and
  stops returning stale results. This skill covers verifying that property type changes
  in indexed nodes are properly handled.
code_tags:
- VALIDATION
- STATE_MUTATION
test_pattern: STATE_TEST
---

# multi-valued-property-index-update

## Instructions

# Multi-Valued Property Index Update Handling

## Instructions

- WHEN the TG encounters code that indexes node properties (especially in a Lucene-based index editor) and the indexed property can be set as either multi-valued (array/Collection) or single-valued (String/Long/etc)
- THEN the TG should write a state test that:
  1. Creates a node with a multi-valued indexed property (e.g., `jcr:title` with values `["foo", "bar"]`)
  2. Asserts that a query for the property value (`"foo"`) returns the node (result set size > 0)
  3. Updates the same property to a single value (e.g., `jcr:title` set to `"baz"`)
  4. Asserts that a query for the **old** multi-valued entry (`"foo"` or `"bar"`) returns 0 results
  5. Asserts that a query for the new single value (`"baz"`) returns the node
  6. Asserts that the result set size is exactly as expected (e.g., `expected:<0> but was:<1>` indicates the bug — old entries were not removed)

- The test MUST verify that updating a multi-valued property to a single value (or vice versa) properly removes all old index entries. A common bug is that the index retains stale entries for previously indexed values after the property type changes.

- Common pitfalls:
  - ❌ Testing only the update of a single-valued to another single-valued (same type) — this misses the type-change bug
  - ❌ Only testing that adding values works, without testing that removing/updating values also cleans up old entries
  - ❌ Checking the new value exists without verifying old values are gone
  - ❌ Using only String type properties — consider other property types (Long, Double, Boolean) that could also be multi-valued

- Correct example:
  ```java
  // Create node with multi-valued property
  Node n = tree.addChild("testNode");
  n.setProperty("jcr:title", new String[]{"foo", "bar"});
  
  // Query for old value — should find it
  assertQuery("//*[jcr:title='foo']", resultSetSize > 0);
  
  // Change to single value
  n.setProperty("jcr:title", "baz");
  
  // Query for OLD value — should return 0 results
  assertQuery("//*[jcr:title='foo']", resultSetSize == 0);
  
  // Query for NEW value — should find it
  assertQuery("//*[jcr:title='baz']", resultSetSize > 0);
  ```

- Incorrect example (would miss the bug):
  ```java
  // Only tests single-valued update
  n.setProperty("jcr:title", "foo");
  n.setProperty("jcr:title", "bar");
  assertQuery("//*[jcr:title='bar']", resultSetSize > 0);
  // Never checks that 'foo' is gone, never tested multi-valued
  ```
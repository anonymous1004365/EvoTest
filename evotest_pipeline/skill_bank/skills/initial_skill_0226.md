---
{}
---

---
name: merge-plugin-list-results-duplication
description: WHEN testing collection merge operations that call setPlugins() repeatedly in a loop, THEN verify the resulting collection has no duplicate elements and the expected size. Common mistake: assuming merge operations only add to the list, when they may overwrite the entire list each iteration causing duplicates.
code_tags: ['NULL_CHECK', 'BOUNDARY_CHECK', 'STATE_MUTATION', 'PLUGIN_MERGE_DUPLICATION']
test_pattern: STATE_TEST
---

# merge-plugin-list-results-duplication

## Instructions

# Merge Plugin List Results Duplication

## Instructions

- WHEN the TG encounters a method that merges Plugin elements from a parent container into a child container (like `ModelUtils.mergePluginLists`) where the child already contains a Plugin that matches a parent Plugin by key, and the merge method calls `childContainer.setPlugins(results)` followed by `childContainer.flushPluginMap()` inside each iteration of a for-loop over parent plugins
- THEN the TG should write a test that:
  1. Creates a parent `PluginContainer` (or `Build`) with a Plugin that has a PluginExecution (e.g., execution with id "testExecution")
  2. Creates a child `PluginContainer` with the **same** Plugin (same groupId:artifactId key) but **without** any PluginExecution initially
  3. Calls `ModelUtils.mergePluginLists(child, parent, handleAsInheritance)` where `handleAsInheritance` matches the code path (use `false` for managed plugins, `true` for inheritance)
  4. Asserts that `child.getPlugins().size()` is exactly 1 (the plugin should not be duplicated)
  5. Asserts that the plugin in the result has the execution(s) merged correctly (e.g., `child.getPlugins().get(0).getExecutions().size()` is 1)
- The test should expect `expected:<1> but was:<2>` if the bug is present — i.e., the plugin appears duplicated in the list instead of appearing only once with merged content
- Common pitfall: Testing only `mergePluginDefinitions` in isolation without going through `mergePluginLists`, which misses the bug because `mergePluginLists` is what manages the actual list on `childContainer` and can produce duplicates by calling `setPlugins` and `flushPluginMap` in each loop iteration

### Example (correct test):

```java
public void testShouldMergeOnePluginWithInheritExecutionWithoutDuplicatingPluginInList()
{
    Plugin parent = new Plugin();
    parent.setArtifactId( "testArtifact" );
    parent.setGroupId( "testGroup" );
    parent.setVersion( "1.0" );

    PluginExecution parentExecution = new PluginExecution();
    parentExecution.setId( "testExecution" );
    parent.addExecution( parentExecution );

    Build parentContainer = new Build();
    parentContainer.addPlugin( parent );

    Build childContainer = new Build();
    // child has same plugin (same key) but no execution
    Plugin childPlugin = new Plugin();
    childPlugin.setArtifactId( "testArtifact" );
    childPlugin.setGroupId( "testGroup" );
    childPlugin.setVersion( "1.0" );
    childContainer.addPlugin( childPlugin );

    ModelUtils.mergePluginLists( childContainer, parentContainer, false );

    assertEquals( 1, childContainer.getPlugins().size() ); // Fails on buggy version: expected:<1> but was:<2>
    assertEquals( 1, ((Plugin) childContainer.getPlugins().get( 0 )).getExecutions().size() );
}
```

### Example (incorrect test — misses the bug):

```java
// Testing only mergePluginDefinitions — this does NOT trigger the list duplication bug
Plugin child = new Plugin(...);
Plugin parent = new Plugin(...);
parent.addExecution(new PluginExecution());
ModelUtils.mergePluginDefinitions(child, parent, false);
assertEquals(1, child.getExecutions().size());  // Passes on both buggy and fixed — irrelevant
```
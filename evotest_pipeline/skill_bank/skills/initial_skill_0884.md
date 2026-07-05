---
name: default-type-for-nodetype-child-paths
description: When testing tree type classification for paths that are children of
  JCR node types definitions, the type should be DEFAULT rather than inheriting a
  parent type. Use this skill when testing TreeTypeProvider.getType() with paths like
  /jcr:system/jcr:nodeTypes/...
code_tags:
- HIERARCHY_TREE_TYPE_RESOLUTION
- PATH_PREFIX_MATCHING
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# default-type-for-nodetype-child-paths

## Instructions

# Default Type for NodeType Child Paths

## Instructions

- WHEN the TG encounters code that determines a tree type based on path matching (e.g., `TreeTypeProvider.getType()`)
- THEN it should test paths that are children of node types definitions (under `NodeTypeConstants.NODE_TYPES_PATH` which equals `/jcr:system/jcr:nodeTypes`) to verify they return `TreeType.DEFAULT` and NOT `TreeType.VERSION`
- Specifically test paths like:
  - `/jcr:system/jcr:nodeTypes/rep:system/rep:namedChildNodeDefinitions/jcr:versionStorage` (child of a node type definition)
  - Any path that starts with `/jcr:system/jcr:nodeTypes/` followed by additional segments
- The bug occurs when a path like `/jcr:system/jcr:nodeTypes/rep:system/rep:namedChildNodeDefinitions/jcr:versionStorage` incorrectly returns `TreeType.VERSION` (value 2) instead of `TreeType.DEFAULT` (value 1)
- WHEN building test cases, use `TreeTypeProvider.getType(Path)` and assert the result against the expected `TreeType` enum value
- Common pitfalls:
  - Testing only the exact `NODE_TYPES_PATH` itself but not its children — the node types root returns DEFAULT correctly, but its descendants may be misclassified
  - Assuming parent path type determines child type (e.g., assuming a `jcr:versionStorage` node anywhere is always a VERSION type)
  - Not including child paths under `/jcr:system/jcr:nodeTypes/` in parametric tests

### Correct Example (detects the bug)

```java
// This test catches the bug: child paths under NODE_TYPES_PATH must be DEFAULT
import org.apache.jackrabbit.oak.plugins.tree.TreeTypeProvider;
import org.apache.jackrabbit.oak.plugins.tree.TreeType;
import org.apache.jackrabbit.oak.spi.nodetype.NodeTypeConstants;

@Test
public void testGetTypeWithDefaultParentType() {
    TreeTypeProvider typeProvider = new TreeTypeProvider();
    
    // This path is a child of a node type definition, should be DEFAULT
    Path nodeTypeChildPath = Path.fromString(
        NodeTypeConstants.NODE_TYPES_PATH + "/rep:system/rep:namedChildNodeDefinitions/jcr:versionStorage"
    );
    
    int actualType = typeProvider.getType(nodeTypeChildPath);
    assertEquals("Child of node type path should be DEFAULT, not VERSION", 
        TreeType.DEFAULT, actualType);
}
```

### Correction to the Incorrect Approach (misses the bug)

```java
// INCORRECT: Only tests the root NODE_TYPES_PATH itself, not its children
@Test
public void testGetTypeForNodeTypes() {
    TreeTypeProvider typeProvider = new TreeTypeProvider();
    
    // Only testing the root path — this works correctly
    Path rootPath = Path.fromString(NodeTypeConstants.NODE_TYPES_PATH);
    assertEquals(TreeType.DEFAULT, typeProvider.getType(rootPath));
    
    // MISSING: does NOT test a child path under NODE_TYPES_PATH
    // The bug only manifests for descendants like:
    // /jcr:system/jcr:nodeTypes/rep:system/rep:namedChildNodeDefinitions/jcr:versionStorage
}
```
---
name: node-state-conversion-missing-default
description: When testing NodeState-to-Map conversion methods that filter out jcr:primaryType,
  ensure child nodes (not just properties) are also correctly excluded if not part
  of the argument map. Use a node with both properties and a child node to verify
  the method correctly omits jcr:primaryType but includes other properties.
code_tags:
- NODE_STATE_CONVERSION
- CONFIG_PARSING
- RESOURCE_LOADING
test_pattern: PARAMETRIC_TEST
---

# node-state-conversion-missing-default

## Instructions

# NodeState to Map Conversion — Hidden Children Cause Mismatch

## Instructions

WHEN the TG encounters a method named `convertNodeState` (or similar) in `NodeStateAnalyzerFactory` that converts a `NodeState` to a `Map<String, String>`, and the method is intended to return only string properties from the node while excluding certain property names (e.g., `JcrConstants.JCR_PRIMARYTYPE`, `ANL_CLASS`, `ANL_NAME`),

THEN the TG should write a test that:
1. Creates a `NodeBuilder` from `EMPTY_NODE.builder()`
2. Adds a **string property** (e.g., `setProperty("foo", "bar")`) directly on the builder
3. Adds a **child node** (e.g., `.child("someChildNode")`) **without** setting any properties on it — to mimic the bug pattern where child nodes with no `jcr:primaryType` property are invisible or cause misbehavior
4. Calls `factory.convertNodeState(nb.getNodeState())` (where `factory` is an instance of `NodeStateAnalyzerFactory`)
5. Verifies that the returned `Map<String, String>` contains the expected property key-value pairs
6. Verifies that the map does NOT contain entries for the child node (since children are not string properties)
7. Verifies that the map does NOT contain entries for excluded property names like `jcr:primaryType` if that property was set

**Common pitfalls to avoid:**
- Testing only by creating a node and setting its `jcr:primaryType` to `nt:unstructured` — this masks the bug because the type is then set and filtering occurs
- Assuming that calling `.child("name")` on a `NodeBuilder` always produces a visible entry — some child nodes without explicit content may not appear in certain iteration order or may be missed
- Not testing the case where no properties exist on the node at all beyond the child node — the map should be empty or contain only excluded properties
- Testing with `NodeStateUtils` to walk the tree but not calling `convertNodeState` directly

**Example of a correct test (fixed version behavior):**
```java
@Test
public void nodeStateAsMap() throws Exception{
    NodeBuilder nb = EMPTY_NODE.builder();
    nb.setProperty("foo", "bar");
    nb.child("testChild"); // child node without any properties
    
    Map<String, String> result = factory.convertNodeState(nb.getNodeState());
    
    // Should contain the string property
    assertEquals("bar", result.get("foo"));
    
    // Should NOT contain the child node as a property
    assertNull("Child node should not appear in property map", result.get("testChild"));
}
```

**Example of a test that would miss the bug:**
```java
@Test
public void nodeStateAsMap_incorrect() throws Exception{
    NodeBuilder nb = EMPTY_NODE.builder();
    nb.setProperty(JCR_PRIMARYTYPE, "nt:unstructured");
    nb.setProperty("foo", "bar");
    
    Map<String, String> result = factory.convertNodeState(nb.getNodeState());
    
    // This would pass even on buggy code because it only tests with properties
    assertEquals("bar", result.get("foo"));
    // But fails to detect that child nodes are being incorrectly included/mishandled
}
```

**What the buggy code does wrong:**
The buggy `convertNodeState` method iterates over `NodeState.getProperties()` and filters out `IGNORE_PROP_NAMES`, but when child nodes are present (especially without explicit `jcr:primaryType`), the method may misinterpret them or fail to render them correctly. The fix ensures child nodes are properly excluded from the returned argument map so that only actual string property values are passed to Lucene analysis factories.
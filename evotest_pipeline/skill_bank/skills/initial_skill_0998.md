---
name: context-defines-root-for-item-definitions
description: When validating whether an OAK Tree is a context root (via definesContextRoot),
  nodes that are item definitions (e.g., rep:namedChildNodeDefinitions children) should
  not be considered context roots even if their name matches a policy node name. Test
  with trees having names like "rep:policy" or "rep:repoPolicy" but primary types
  like "rep:NamedChildNodeDefinitions" to assert false.
code_tags:
- VALIDATION
- STATE_MUTATION
- ORDER_DEPENDENCY
test_pattern: STATE_TEST
---

# context-defines-root-for-item-definitions

## Instructions

# Context definesContextRoot Must Exclude Item Definitions

## Instructions

**WHEN** the TG encounters a `Context.definesContextRoot(@Nonnull Tree tree)` implementation that checks node names against `POLICY_NODE_NAMES` (e.g., `rep:policy`, `rep:repoPolicy`) and then validates the primary type against `NT_REP_ACL`:

- **THEN** the TG should test that nodes whose **name** matches a policy node name but whose **primary type** is a node type definition (e.g., `NodeTypeConstants.NT_REP_NAMED_CHILD_NODE_DEFINITIONS`) return `false` from `definesContextRoot()`.
- **THEN** the TG should construct test trees that exist in the repository under paths like `/jcr:system/jcr:nodeTypes/rep:AccessControllable/rep:namedChildNodeDefinitions/rep:policy` and `/jcr:system/jcr:nodeTypes/rep:RepoAccessControllable/rep:namedChildNodeDefinitions/rep:repoPolicy`.
- **THEN** the TG should verify `assertFalse(ctx.definesContextRoot(tree))` for such trees — they are node type item definitions, not actual ACL instances.
- **Common Pitfall**: Testing only with existing ACL trees (where the primary type IS `rep:ACL`) and verifying `assertTrue(...)`, but forgetting to test with non-ACL trees that happen to share the same node name. The `definesContextRoot` method must differentiate between a `rep:ACL` node (primary type `rep:ACL`) and an item definition node (primary type `rep:NamedChildNodeDefinitions`) even though both have name `rep:policy`.

### Correct Example (Catches the Bug)

```java
@Test
public void testItemDefinitionsDefinesContextRoot() throws Exception {
    List<String> paths = Lists.newArrayList(
            "/jcr:system/jcr:nodeTypes/rep:AccessControllable/rep:namedChildNodeDefinitions/rep:policy",
            "/jcr:system/jcr:nodeTypes/rep:RepoAccessControllable/rep:namedChildNodeDefinitions/rep:repoPolicy");

    for (String defPath : paths) {
        Tree tree = root.getTree(defPath);
        assertFalse(AuthorizationContext.getInstance().definesContextRoot(tree));
    }
}
```

### Incorrect Example (Misses the Bug)

```java
// Only testing actual ACLs — does not detect the item definition bug
@Test
public void testPolicyDefinesContextRoot() throws Exception {
    createAcl("/", PrivilegeConstants.JCR_READ);
    Tree aclTree = root.getTree("/").getChild(AccessControlConstants.REP_POLICY);
    assertTrue(aclTree.exists());
    assertTrue(AuthorizationContext.getInstance().definesContextRoot(aclTree));
}
```

### What the Bug Was

The buggy `definesContextRoot` method in `AuthorizationContext` checked `isNodeName(name)` (which returns `true` for names like `rep:policy` and `rep:repoPolicy`) and then returned `NT_REP_ACL.equals(TreeUtil.getPrimaryTypeName(tree))`. However, for nodes with name `rep:policy` inside the nodetype definition tree at paths like `.../rep:namedChildNodeDefinitions/rep:policy`, the primary type name returned was `rep:NamedChildNodeDefinitions` (not `rep:ACL`), so `definesContextRoot` returned `false` correctly. But the bug was that in some cases, the code path was incorrect or the implementation needed to be hardened against such false positives. The test ensures that item definition nodes are explicitly excluded from being treated as context roots.
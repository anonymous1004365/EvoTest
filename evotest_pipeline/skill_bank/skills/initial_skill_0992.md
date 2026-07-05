---
name: rootless-tree-node-insertion-dom-invalidation
description: When testing AbstractTree.setRootLess(true) behavior, test that treeNodesInserted
  adds new items to dirtyItemsCreateDOM so they appear in AJAX responses. Without
  this invalidation, newly inserted child nodes on the hidden root of a rootless tree
  are missing from the response.
code_tags:
- NULL_CHECK
- STATE_MUTATION
test_pattern: INTERACTION_TEST
---

# rootless-tree-node-insertion-dom-invalidation

## Instructions

# Rootless Tree Node Insertion DOM Invalidation

## Instructions

- WHEN the TG encounters `AbstractTree` (or a subclass like `Tree`, `LinkTree`) with `setRootLess(true)` and a `TreeModel` where a child is inserted into the root node via `treeModel.insertNodeInto(child, rootNode, ...)`, followed by `tree.updateTree(target)`
  - THEN the TG should verify that the response from the AJAX request contains the markup for the newly inserted child node
  - Use `tester.clickLink(linkId, true)` to trigger the AJAX event, then call `assertTrue(tester.getLastResponseAsString().contains("childNodeName"))`
  - If the bug is present, the AJAX response will NOT contain the new child node's markup because the root node acts as a placeholder in rootless mode (hidden `<div>`) and the new item is not added to `dirtyItemsCreateDOM` set
  - The fix ensures that when `treeNodesInserted(TreeModelEvent)` processes an insertion and the parent is the hidden root (`isRootLess()`), the new `TreeItem` is added to `dirtyItemsCreateDOM`
  - Common pitfall: Only testing that no exception is thrown, not verifying the actual response content for the new node's markup. Also, avoid testing node insertion on non-root nodes without also checking the root-less scenario — the bug is specific to inserting a direct child of the hidden root.

- WHEN the TG tests AJAX responses from `AbstractTree` subclasses where nodes are programmatically added to the tree model
  - THEN the TG should use `WicketTester.clickLink()` with `true` for the AJAX request parameter and assert on the response string using `tester.getLastResponseAsString().contains("expectedNodeId")`
  - The test should set up a `DefaultMutableTreeNode` as root, create a `DefaultTreeModel`, and add the tree to a page with a link that triggers `treeModel.insertNodeInto()`

- Common pitfalls:
  - Forgetting to call `tree.setRootLess(true)` before starting the page
  - Using `tester.startPage()` before setting rootLess, or after modifying the tree model (model changes before page start may behave differently)
  - Testing only that the AJAX request succeeds (no exceptions) rather than checking the response body for the newly inserted child's markup
  - Not checking that the child node's display name (e.g., `"rootChild"`) appears in the response string

### Example (correct test)

```java
public void testAddChildOnRootAtAnOnRootLessTree()
{
    TestPage testPage = new TestPage();
    testPage.tree.setRootLess(true);
    tester.startPage(testPage);
    tester.clickLink("addToRoot", true);
    assertTrue(tester.getLastResponseAsString().contains("rootChild"));
}
```

### Example (incorrect test — doesn't check response content)

```java
public void testAddChildOnRootAtAnOnRootLessTree()
{
    TestPage testPage = new TestPage();
    testPage.tree.setRootLess(true);
    tester.startPage(testPage);
    tester.clickLink("addToRoot", true);
    // BUG: Only checks no exception, but doesn't verify the new node appears in response
    // The buggy version would pass this test even though the child is missing from the DOM
}
```
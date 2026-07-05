---
name: read-only-builder-mutation-on-construction
description: When constructing an OakDirectory with a ReadOnlyBuilder, the constructor
  must use builder.getChildNode() instead of builder.child() to avoid an UnsupportedOperationException.
  This skill teaches how to test that read-only directory construction works without
  mutation.
code_tags:
- READONLY_BUILDER_MUTATION
- STATE_MUTATION
test_pattern: EXCEPTION_TEST
---

# read-only-builder-mutation-on-construction

## Instructions

# ReadOnlyBuilder Mutation on Construction

## Instructions

- WHEN the TG encounters code that constructs an `OakDirectory` (or any class taking a `NodeBuilder`) and passes a `ReadOnlyBuilder` instance with `readOnly=true` as the builder parameter
- THEN it should verify that the constructor does NOT call any mutating method on the `ReadOnlyBuilder`, specifically `builder.child(String name)`. The fix in `OakDirectory` constructor changed `builder.child(dataNodeName)` to `readOnly ? builder.getChildNode(dataNodeName) : builder.child(dataNodeName)`. The test must verify that constructing an `OakDirectory` with:
  1. A `ReadOnlyBuilder` wrapping a real `NodeState` (e.g., `new ReadOnlyBuilder(builder.getNodeState())`)
  2. `readOnly=true`
  
  ...succeeds without throwing an `UnsupportedOperationException`.

- WHEN testing, use `ReadOnlyBuilder` imported from `org.apache.jackrabbit.oak.spi.state.ReadOnlyBuilder`. Construct it with a non-empty `NodeState` that already has the expected child node (e.g., `INDEX_DATA_CHILD_NAME`), so that `getChildNode()` returns an existing node. Do NOT pass an empty `NodeState` — the child node must exist because `getChildNode` on ReadOnlyBuilder only works for existing children.

- The test should verify that:
  - The `OakDirectory` instance is created without exception
  - Read operations like `listAll()`, `fileExists()`, `openInput()` work on the constructed instance
  - Write operations like `createOutput()` throw `IllegalArgumentException` (due to `checkArgument(!readOnly, ...)` in `OakDirectory.createOutput()`)

- Common pitfalls:
  - Testing with a plain mutable `NodeBuilder` and `readOnly=true` will succeed but does NOT test the bug — the bug only manifests when the constructor receives a `ReadOnlyBuilder` as the builder.
  - Passing a `ReadOnlyBuilder` wrapping an empty `NodeState` will cause `getChildNode()` to return a non-existent node (which `ReadOnlyBuilder.child()` throws on), so the test must set up the initial state properly with the `INDEX_DATA_CHILD_NAME` child node already present.
  - Not using `@Test(expected=...)` or `fail()` + `catch` for the exception — if the constructor throws `UnsupportedOperationException`, the test should catch it explicitly and fail.

### Correct example (testing successful construction with ReadOnlyBuilder):

```java
import org.apache.jackrabbit.oak.spi.state.ReadOnlyBuilder;

@Test
public void readOnlyDirectory() throws Exception {
    // Pre-populate the builder with a child node under INDEX_DATA_CHILD_NAME
    builder.child(LuceneIndexConstants.INDEX_DATA_CHILD_NAME)
           .child("existingFile.txt")
           .setProperty("jcr:data", createBlobData(), Type.BINARIES);
    builder.child(LuceneIndexConstants.INDEX_DATA_CHILD_NAME)
           .child("anotherFile.bin")
           .setProperty("jcr:data", createBlobData(), Type.BINARIES);
    
    // Wrap the final NodeState in a ReadOnlyBuilder
    NodeBuilder readOnlyBuilder = new ReadOnlyBuilder(builder.getNodeState());
    
    // This must NOT throw UnsupportedOperationException
    Directory dir = new OakDirectory(readOnlyBuilder, 
        new IndexDefinition(root, readOnlyBuilder.getNodeState()), true);
    
    // Read operations should work
    assertTrue(dir.fileExists("existingFile.txt"));
    assertEquals(2, dir.listAll().length);
    
    // Write operations should fail with IllegalArgumentException (from checkArgument)
    try {
        dir.createOutput("newFile", IOContext.DEFAULT);
        fail("Should have thrown IllegalArgumentException");
    } catch (IllegalArgumentException e) {
        // expected
    }
    
    dir.close();
}
```

### Incorrect example (will NOT catch the bug):

```java
// This test uses a plain mutable builder with readOnly=true
// The bug only triggers with ReadOnlyBuilder, so this passes on both buggy and fixed
@Test
public void readOnlyDirectory_incorrect() throws Exception {
    // Using a regular builder (not ReadOnlyBuilder) — this does not test the bug
    Directory dir = new OakDirectory(builder, 
        new IndexDefinition(root, builder.getNodeState()), true);
    
    // This will pass even on the buggy version
    assertNotNull(dir);
}
```
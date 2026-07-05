---
name: long-path-document-split-gc
description: When testing version garbage collection for MongoDB document store with
  split documents at long paths, verify that GC correctly handles documents whose
  path length exceeds 512 bytes and requires split doc detection. Apply when validating
  GC logic for split documents under long path conditions.
code_tags:
- VALIDATION
- BOUNDARY_CHECK
- STATE_MUTATION
- ORDER_DEPENDENCY
test_pattern: PARAMETRIC_TEST
---

# long-path-document-split-gc

## Instructions

# Long Path Document Split GC

## Instructions

WHEN the TG encounters code that performs version garbage collection on split documents (e.g., `VersionGarbageCollector.collectGarbage()` or `VersionGCSupport` methods that iterate over candidate documents), especially involving paths that may exceed typical length limits:

- THEN the TG should write a parametric test (e.g., using `@ParameterizedTest` or `@Test` with different inputs via `@ParameterizedTest(name = "{0}")` or a simple parameterized runner) that tests GC behavior with both:
  1. A **short path** (e.g., `"foo"`) — the baseline/normal case
  2. A **very long path** that is at least 360+ characters long, but still a valid document path (e.g., 360-character string created via `String.repeat("sub", 120)` where each `"sub"` is 3 chars, totaling 360 chars)
- The test should verify that after performing the same operations (e.g., addNode, setProperty, commit, wait for background ops, trigger GC), the **same count or type of garbage-collected documents** is collected for both the short and long path cases.
- Specifically, for the `org.apache.jackrabbit.oak.plugins.document.VersionGarbageCollector` class, the TG should test that the number of split documents collected by `gcSplitDocsInternal()` is the same regardless of path length.
- WHEN testing GC behavior, the TG should:
  - Create a cluster node and a DocumentNodeStore
  - Add nodes and properties, commit changes, wait for background operations to split documents
  - Call the GC method and assert on the number of garbage-collected documents (e.g., `assertEquals(4, gc.getSplitDocGCCount())`)
  - Repeat the same test with a long path (e.g., `String.repeat("sub", 120)`)
- Common pitfalls to avoid:
  - **Testing only with short/normal paths** — this misses bugs that only manifest with long paths (e.g., paths longer than 512 bytes affecting MongoDB document keys or splitting behavior)
  - **Using different operations** between the short path and long path test — the operations must be identical, only the path length differs
  - **Not waiting for background operations** — split document generation requires async background processes to complete before GC can detect them
  - **Hardcoding expected values** based only on the short-path behavior — the fix ensures both cases produce the same result

## Examples

### Correct Test (detects the long path split GC bug)

```java
@ParameterizedTest(name = "{0}")
@ValueSource(strings = {"foo", Strings.repeat("sub", 120)})
public void gcLongPathSplitDocs(String subNodeName) throws Exception {
    gcSplitDocsInternal(subNodeName);
}

private void gcSplitDocsInternal(String subNodeName) throws Exception {
    final Cluster c = new Cluster(createDfs(0), createDfs(1));
    try {
        c.cluster1.disconnect().await();
        c.cluster2.disconnect().await();
        // 1. create nodes and revisions
        DocumentNodeStore cluster1 = c.cluster1.await();
        String path = "/" + subNodeName + "/" + subNodeName + "/" + subNodeName;
        addNodes(cluster1, path, 10);
        setProps(cluster1, path, 10);

        // 2. wait for split docs
        c.cluster1.reconnect().await();
        c.cluster2.reconnect().await();
        c.cluster1.await();
        c.cluster2.await();

        // 3. GC and check
        VersionGarbageCollector gc = c.cluster2.getVersionGarbageCollector();
        gc.collectGarbage();
        assertEquals(4, gc.getSplitDocGCCount());
    } finally {
        c.disconnect().await();
    }
}
```

### Incorrect Test (misses the bug)

```java
// Only tests with a short path — does NOT detect the long path issue
@Test
public void gcShortPathSplitDocs() throws Exception {
    gcSplitDocsInternal("foo");
}

private void gcSplitDocsInternal(String subNodeName) throws Exception {
    // ... same setup as above but only called with "foo"
    // Bug only manifests when subNodeName is long (e.g., Strings.repeat("sub", 120))
    assertEquals(4, gc.getSplitDocGCCount()); // passes for "foo", would fail for long path
}
```

### Key Assertions

The test should assert that:
- `gc.getSplitDocGCCount()` returns the **same value** for both the short and long path variants
- The fix ensures that split document detection works correctly even when the document path exceeds typical length limits (e.g., leading to MongoDB document key hashing issues)
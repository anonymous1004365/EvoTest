---
name: thread-safe-xpath-expression-pooling
description: When testing XPathBuilder or similar thread-safe expression builders
  that use a ConcurrentLinkedQueue pool of XPathExpression objects, test concurrent
  access to verify no expressions are lost due to race conditions in pool offer/poll
  operations.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- NULL_CHECK
- CONCURRENCY
test_pattern: PARAMETRIC_TEST
---

# thread-safe-xpath-expression-pooling

## Instructions

# Thread-Safe XPath Expression Pooling

## Instructions

WHEN the TG encounters an XPathBuilder (or similar expression builder) that uses a ConcurrentLinkedQueue-based pool (e.g., `Queue<XPathExpression> pool = new ConcurrentLinkedQueue<>()`) with `pool.poll()` and `pool.offer()` for reusing compiled XPath expressions across multiple evaluations,

THEN the TG should write a concurrent test that:
1. Creates a single `XPathBuilder` instance with an XPath expression that splits XML elements (e.g., `xpath("/foo/bar").stringResult()`)
2. Submits the same evaluation expression (e.g., splitting an XML string like `<foo><bar>1</bar><bar>2</bar></foo>` or similar) concurrently from multiple threads — use at least 10 threads and at least 100 total invocations
3. Uses `ExecutorService`, `CountDownLatch`, and `Callable` to synchronize thread start and collect results
4. Asserts that the **total number of results** equals the **expected count** (e.g., 100)
5. Verifies that **no evaluation returns null** and **no exception is thrown** during concurrent access

The key failure mode: due to a race condition in `XPathExpression` pool management (between `pool.poll()` returning null and subsequent creation of a new expression), concurrent evaluations can silently lose results — e.g., expected 100 split parts but observed only 99.

Common pitfalls to avoid:
- **Do NOT** create separate XPathBuilder instances per thread — the bug is in sharing a single builder's pool
- **Do NOT** test only sequential evaluation — that will never reproduce the race condition
- **Do NOT** forget to await termination of the executor service before asserting results
- **Do NOT** mistake the test for a performance test — it is a correctness test for thread safety
- **Do NOT** use `synchronized` blocks in the test; the test itself should be simple concurrent submission

### Correct Example (detects the bug):
```java
public void testXPathSplitConcurrent() throws Exception {
    final XPathBuilder builder = XPathBuilder.xpath("/foo/bar/text()");
    final String xml = "<foo><bar>1</bar><bar>2</bar></foo>";
    // ... creates a fixed XML with many <bar> elements
    
    int total = 100;
    final CountDownLatch latch = new CountDownLatch(1);
    ExecutorService exec = Executors.newFixedThreadPool(10);
    Set<String> results = new HashSet<>();
    
    for (int i = 0; i < total; i++) {
        exec.submit(new Callable<String>() {
            public String call() throws Exception {
                latch.await();
                return builder.evaluate(context, xml, String.class);
            }
        });
    }
    
    latch.countDown();
    exec.shutdown();
    exec.awaitTermination(10, TimeUnit.SECONDS);
    
    assertEquals(total, results.size());  // On buggy version: expected <100> but was <99>
}
```

### Incorrect Example (misses the bug):
```java
// BAD: sequential test - won't trigger race condition
public void testXPathSplit() throws Exception {
    XPathBuilder builder = XPathBuilder.xpath("/foo/bar/text()");
    String result = builder.evaluate(context, "<foo><bar>1</bar><bar>2</bar></foo>", String.class);
    assertEquals("12", result);
}
```
---
name: priority-header-item-bundle-ordering
description: When rendering PriorityHeaderItems that get bundled, the bundling and
  priority unwrapping must work together so that priority semantics survive the bundling
  process. Teaches how to test that priority items are not rendered as individual
  unbundled components when a bundle replaces them.
code_tags:
- ORDER_DEPENDENCY
- STATE_MUTATION
test_pattern: STATE_TEST
---

# priority-header-item-bundle-ordering

## Instructions

# Priority Header Item Bundle Ordering

## Instructions

WHEN the TG encounters code where a `ResourceAggregator` wraps header items with `PriorityHeaderItem` and those items can be replaced by a resource bundle (via `ResourceBundles.addJavaScriptBundle()`), THEN the TG should test that priority semantics are preserved in the final rendered output. Specifically:

- WHEN rendering a `PriorityHeaderItem` wrapping a resource reference that belongs to a bundle (e.g., `new PriorityHeaderItem(forReference(new ResourceReferenceB()))`)
- AND also rendering other resources that depend on the same dependencies as the priority item (e.g., `forReference(new ResourceReferenceD())`)
- THEN the test MUST verify that the bundle replaces the individual priority item correctly, producing a `PriorityHeaderItem` wrapping the bundle (e.g., `new PriorityHeaderItem(bundleAB)`) rather than the individual priority items plus the bundle separately.

Concrete types and values:
- The `ResourceAggregator` is created as `new ResourceAggregator(responseStub)` where `responseStub` is a `TestHeaderResponse`
- Bundles are created via `Application.get().getResourceBundles().addJavaScriptBundle(Application.class, "name.js", ref1, ref2, ...)`
- Priority wrapping is done via `new PriorityHeaderItem(forReference(someResourceReference))`
- Render priority items and regular items using `aggregator.render(...)`
- Assert the final output after calling `aggregator.close()` by checking `responseStub.getItems()`
- The expected output should be a list where the bundle (wrapped in `PriorityHeaderItem` if the original was priority) is in the correct position

Common pitfalls:
- Testing only individual `PriorityHeaderItem` rendering without bundles (the bug only manifests when bundles combine resources that include the priority item)
- Testing only bundle replacement without priority wrapping (both mechanisms must interact)
- Forgetting to call `aggregator.close()` before asserting — the aggregation only happens on `close()`
- Assuming `assertEquals` on the full list of `HeaderItem`s will detect the issue; it will, but only if the expected list includes the `PriorityHeaderItem` wrapping the bundle rather than the individual items

**Correct example** (tests for the bug):
```java
@Test
public void testTwoBundlesWithDependenciesAndPriority()
{
    HeaderItem bundleAB = Application.get()
        .getResourceBundles()
        .addJavaScriptBundle(Application.class, "ab.js", new ResourceReferenceA(),
            new ResourceReferenceB());
    HeaderItem bundleCD = Application.get()
        .getResourceBundles()
        .addJavaScriptBundle(Application.class, "cd.js", new ResourceReferenceC(),
            new ResourceReferenceD());
    aggregator.render(new PriorityHeaderItem(forReference(new ResourceReferenceB())));
    aggregator.render(forReference(new ResourceReferenceD()));
    assertItems(new PriorityHeaderItem(bundleAB), bundleCD);
}
```

**Incorrect approach** (would miss the bug):
```java
// Would pass on buggy code because it doesn't verify priority wrapping on bundles
@Test
public void testTwoBundlesWithDependencies()
{
    HeaderItem bundleAB = ...;
    HeaderItem bundleCD = ...;
    aggregator.render(forReference(new ResourceReferenceD()));
    assertItems(bundleAB, bundleCD);
}
```

**What the test should detect on the buggy version**: The buggy version renders `[PriorityHeaderItem(a.js), PriorityHeaderItem(b.js), bundleAB, bundleCD]` instead of the correct `[PriorityHeaderItem(bundleAB), bundleCD]`. The test should fail on the buggy version because the individual priority items `a.js` and `b.js` appear separately instead of being replaced by the single `PriorityHeaderItem(bundleAB)`.
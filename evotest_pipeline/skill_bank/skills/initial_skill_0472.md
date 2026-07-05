---
name: resource-aggregator-render-order-state
description: When testing resource aggregation logic, ensure that newly added header
  resources from aggregated bundles are properly rendered even if the resource aggregator
  has already processed some header contributions. Tests must verify both the initial
  rendering pass and re-rendering after dynamic component additions.
code_tags:
- ORDER_DEPENDENCY
- STATE_MUTATION
test_pattern: STATE_TEST
---

# resource-aggregator-render-order-state

## Instructions

# Resource Aggregator Render Order and State Mutation

## Instructions

- WHEN the test encounters code that adds header contributions (JavaScript/CSS resources) to a page through `ResourceAggregator` while using rendered/bucket-based aggregation
- THEN it should verify that resources added to page components AFTER the aggregator has already started rendering are still properly emitted in the final output, AND verify the exact number of rendered script/style elements
- Include concrete checks:
  - Compare rendered output against an expected HTML results file
  - Verify that script elements for `HeaderResponseItem` classes appear in the output for resources contributed by components like `Panel`, not just inline resources
  - Use `executeTest()` or equivalent render testing method that renders the full page and compares with a baseline
- Common pitfalls to avoid:
  - Testing only inline resource contributions without verifying aggregated bundle resources from child components
  - Assuming that all header contributions are captured before the aggregator's `renderHead()` is called
  - Not including component trees where panels/components add resources dynamically during rendering
  - Testing resource ordering without also testing that resources are not silently lost

Examples:
```java
// CORRECT: Verifies both inline resources AND aggregated resources from components
@Test
public void testPage1()
{
    executeTest(ResourceAggregatorTest1Page.class, "ResourceAggregatorTest1Page_result.html");
}
```

```java
// INCORRECT: Only tests that no exception is thrown, doesn't verify output
@Test
public void testPage1()
{
    // Missing: verifies that resources from panels are rendered
    tester.startPage(ResourceAggregatorTest1Page.class);
    // Missing: output comparison
}
```
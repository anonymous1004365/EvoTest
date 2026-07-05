---
name: index-based-segment-removal-off-by-one
description: When a URL object segments list is manipulated by removing an element
  at an index derived from mountSegments.length, the removal shifts subsequent elements.
  Tests must verify that the resulting segments list contains the expected page parameters
  after the removal.
code_tags:
- ORDER_DEPENDENCY
- STATE_MUTATION
- ARGUMENT_VALIDATION
test_pattern: STATE_TEST
---

# index-based-segment-removal-off-by-one

## Instructions

# Index-Based Segment Removal Off-by-One

## Instructions

- WHEN the TG encounters code that calls `getSegments().remove(index)` on a `Url` object's segments list, where `index` is derived from `mountSegments.length` (e.g., `url.getSegments().remove(mountSegments.length)`),
- THEN the TG should write a test that: (1) constructs a `Url` with more segments than the mount segments length, (2) clones it via `new Url(url)`, (3) calls `remove(index)` on the clone's segments, and (4) verifies that the segments list after removal contains the correct page-relevant segments.
- Specifically, when `mountSegments.length` is e.g. 0 (mount path has no segments, i.e. mounted at root ""), removing `url.getSegments().remove(0)` removes the first segment of the URL instead of nothing. The test must verify that all original URL segments are preserved when `mountSegments` is empty.
- The test should assert on the size and contents of `url.getSegments()` after the removal operation.
- Common pitfall: testing only with non-empty mount paths (mountSegments.length > 0) where the removal index is correct, and missing the edge case of an empty mount path (mountSegments.length == 0).
- Example correct test (empty mount path case):
```java
// Given: mount segments are empty (mount path = "")
int[] mountSegments = new int[0];
Url url = new Url();
url.getSegments().add("a");
url.getSegments().add("b");
// When: remove at index = mountSegments.length (= 0)
Url urlClone = new Url(url);
urlClone.getSegments().remove(mountSegments.length);
// Then: the first segment "a" should NOT have been removed
assertEquals(2, urlClone.getSegments().size());
assertEquals("a", urlClone.getSegments().get(0));
assertEquals("b", urlClone.getSegments().get(1));
```
- Example incorrect test (missing empty mount path case):
```java
// BAD: only tests with non-empty mount path where index > 0
int[] mountSegments = new int[]{0};
Url url = new Url();
url.getSegments().add("page");
url.getSegments().add("param");
url.getSegments().remove(mountSegments.length); // removes at index 1
assertEquals(1, url.getSegments().size()); // passes but misses the bug
// The bug only manifests when mountSegments.length == 0
```
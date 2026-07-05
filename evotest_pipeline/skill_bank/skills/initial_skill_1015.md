---
name: path-compatibility-score-accuracy
description: WHEN testing mappers that return compatibility scores for request path
  ranking, THEN verify the scoring logic returns correct values for both exact matches
  (highest score) and various path lengths. FOR EXAMPLE, for PackageMapper, test that
  getCompatibilityScore returns the correct score by checking that a path with the
  right number of segments relative to the page class package depth scores properly,
  catching bugs where the score is miscalculated (e.g., returning 2 instead of 4).
code_tags:
- ARGUMENT_VALIDATION
- NULL_CHECK
- BOUNDARY_CHECK
- PATH_COMPATIBILITY_SCORE
test_pattern: PARAMETRIC_TEST
---

# path-compatibility-score-accuracy

## Instructions

# Path Compatibility Score Accuracy

## Instructions

- WHEN the TG encounters a mapper class that overrides `getCompatibilityScore(Request)` to compute a ranking score for request path matching (e.g., `PackageMapper`, `HomePageMapper`), THEN the TG should write parametric tests that verify the returned integer score for different request path inputs, including:
  - Exact path matches that should yield the highest score
  - Paths with different numbers of segments (URL path depth)
  - Boundary cases where the path has zero or one segment
- WHEN testing `PackageMapper.getCompatibilityScore()`, THEN the TG must verify the score reflects the number of path segments that successfully resolve against the page class's package structure. Specifically:
  - For the bug in `PackageMapper`, `getCompatibilityScore()` returned a score based only on how many path segments matched the mapped package name, but FAILED to also count the extra segment for the page class name itself. The correct score should be `number_of_matching_package_segments + 1` (for the page class), not just `number_of_matching_package_segments`.
  - THE TG should test with a `Request` object whose URL has exactly enough segments to match both the package path and the page class name, and assert that the score equals the total number of path segments (package depth + 1), not just the package depth.
- WHEN verifying score correctness, THEN the TG should use real `Request` objects constructed with an appropriate `Url` (e.g., via `RequestCycle` or `Request` builder utilities available in the test framework) and mock the `MapperContext` if needed to resolve the page class. Common pitfalls:
  - ❌ Testing only with null or empty requests, missing the specific path-length-based scoring bug
  - ❌ Asserting the score is merely non-zero or positive instead of asserting the exact expected integer value
  - ❌ Not accounting for the "page class name" segment in the score computation

## Examples

Correct test pattern:
```java
@Test
public void getCompatibilityScore()
{
    PackageMapper mapper = new PackageMapper("org.apache.wicket.examples.cheesr",
        CheesrPage.class);
    
    // A request URL that matches: /org/apache/wicket/examples/cheesr/CheesrPage
    // That's 4 segments: org, apache, wicked, examples — wait, let's use the actual test:
    
    // The mapped package is "org.apache.wicket.examples.cheesr" = 5 segments
    // The page class is CheesrPage → total expected = 5 + 1 = 6 segments that match
    
    // Create a request whose URL path has exactly those 6 segments
    Request request = createRequest("/org/apache/wicket/examples/cheesr/CheesrPage");
    int score = mapper.getCompatibilityScore(request);
    assertEquals("Score must count all package segments + page class segment", 6, score);
}
```

Incorrect test pattern (that wouldn't catch the bug):
```java
@Test
public void getCompatibilityScore()
{
    PackageMapper mapper = new PackageMapper("some.package", SomePage.class);
    Request request = createRequest("/some/package/SomePage");
    int score = mapper.getCompatibilityScore(request);
    assertTrue("Score should be positive", score > 0); // TOO VAGUE - won't detect off-by-one errors
}
```
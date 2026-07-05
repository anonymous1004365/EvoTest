---
name: alternative-protocol-decoding-fallback
description: When a protocol decoder has a primary parsing path and a fallback/alternative
  path, test both paths separately, especially when the fallback may incorrectly parse
  or default when primary fails. The alternative path is a common source of bugs because
  it is tested less thoroughly.
code_tags:
- NULL_CHECK
- VALIDATION
- STATE_MUTATION
test_pattern: PARAMETRIC_TEST
---

# alternative-protocol-decoding-fallback

## Instructions

# Alternative Protocol Decoding Fallback

## Instructions

- WHEN the TG encounters a protocol decoder that has multiple parsing branches (e.g., a `try-catch` where the primary parsing can fail and fall back to an alternative decoding method), THEN it should write **separate test cases** for each distinct decoding path.
- WHEN the TG sees that the primary decoding path parses one protocol message format (e.g., a specific token count, specific delimiters, specific field positions), THEN it should specifically test the **alternative/fallback path** with messages that are intentionally incompatible with the primary path (e.g., wrong token count, missing fields, different delimiters) to force the fallback to execute.
- WHEN a fallback decoding path uses `try-catch` and silently falls back on any exception, THEN the TG should verify that the fallback correctly parses messages that **look structurally similar** to the primary format but have subtle differences (e.g., an odd number of tokens instead of an even number, or a different field being empty).
- The TG should include assertions that compare the decoded result (e.g., device position, timestamp, speed, location) between the two paths to ensure they produce consistent/convergent results.
- Common pitfall: testing only the primary/standard message format (which succeeds on both buggy and fixed versions), missing the bug that only manifests when the alternative path is exercised.
- Common pitfall: assuming that because a message passes primary parsing, the alternative path is never used — write explicit inputs that force the fallback.
- Common pitfall: writing a single test that covers only one path; include at least one test case per distinct decoding branch.

Example of a correct test (parametrized with both paths — adjust to match actual message format):
```java
@Test
public void testAlternativeDecodingPath() {
    // This message intentionally fails primary parsing (odd number of tokens, or missing a delimiter)
    String msg = "XX123456789012345,123456,123456,1,3,100.0,200.0,0,0,0,0,0,0";
    Position position = decoder.decode(msg);
    assertNotNull(position);
    assertNotNull(position.getFixTime());
    assertEquals(100.0, position.getLatitude(), 0.001);
    assertEquals(200.0, position.getLongitude(), 0.001);
}
```

Example of an incorrect test (only covers primary path, misses the bug):
```java
@Test
public void testStandardMessage() {
    // Only tests the primary parsing path — the bug is in the fallback
    String msg = "XX123456789012345,123456,123456,1,3,100.0,200.0,0,0,0,0,0,0,0,0,0";
    Position position = decoder.decode(msg);
    assertNotNull(position);
    assertEquals(100.0, position.getLatitude(), 0.001);
}
```
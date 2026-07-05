---
name: meta-pattern-optional-group-matching
description: Teaches how to test MetaPattern-based parsers that use Group objects
  wrapped with OptionalMetaPattern, by checking that optional sub-patterns like ':subname'
  are correctly captured. Apply this when parsers build patterns from Group, MetaPattern.VARIABLE_NAME,
  MetaPattern.COLON, and OptionalMetaPattern arrays.
code_tags:
- VALIDATION
- META_PATTERN_GROUP_MATCHING
test_pattern: PARAMETRIC_TEST
---

# meta-pattern-optional-group-matching

## Instructions

# MetaPattern Optional Group Matching

## Instructions

WHEN the TG encounters a parser class (extending `MetaPatternParser`) that constructs patterns using `Group`, `MetaPattern.VARIABLE_NAME`, `MetaPattern.COLON`, and `OptionalMetaPattern` (e.g., `new OptionalMetaPattern(new MetaPattern[] { ... })`) to parse compound attribute names like `namespace:name` or `namespace:name:subname`,

THEN the TG should write a parameterized test that exercises `matcher()` (from `MetaPatternParser`) against both variations of the input string — with and without the optional part — and then verifies that each `Group`'s matched text (via `Group.matcher()`) is correct.

Specifically:
- When the input is `"namespace:name"`, the test must verify that the key group captures `"name"` and that no subname group is matched.
- When the input is `"namespace:name:subname"`, the test must verify that the key group captures `"name"` AND the optional subname group captures `":subname"` (or `"subname"` depending on how the group is constructed).
- The test should call `parser.matcher(input)` and then call `group.matcher()` on each `Group` object, asserting `group.matches()` is true and `group.group()` returns the expected captured string.
- Common Mistake to avoid: Testing only the string presence of `":subname"` in output without calling the `Group.matcher()` method on individual groups. The bug occurs when groups don't properly re-match after the overall pattern matches — always call `.matcher()` separately on each `Group` after the parser-level match, and verify their individual `matches()` and `group()` results.

**Correct Example (detects the bug):**
```java
@Test
public void parseAttributeName()
{
    String input = "myPrefix:myName:mySubname";

    VariableAssignmentParser parser = new VariableAssignmentParser(input);
    assertThat(parser.matches(), is(true));

    // key group must match the attribute name part
    Group key = parser.getKey();
    assertThat(key.matches(), is(true));
    assertThat(key.group(), is("myName"));

    // subname group must match the optional part  
    Group subnameGroup = ...; // obtain via parser.get...()
    assertThat(subnameGroup.matches(), is(true));
    assertThat(subnameGroup.group(), is(":mySubname"));
}
```

**Incorrect Example (misses the bug):**
```java
@Test
public void parseAttributeName()
{
    // Only checks that the whole expression matches
    VariableAssignmentParser parser = new VariableAssignmentParser("myPrefix:myName:mySubname");
    assertThat(parser.matches(), is(true));
    // Does NOT call group.matcher() on individual groups
    // Does NOT verify group.group() output
    // Would NOT catch that the optional group fails to capture ":subname"
}
```

When composing the test input strings:
- Use a test input with no optional part: `"namespace:name"` — verify only the key group matches.
- Use a test input with the optional part present: `"namespace:name:subname"` — verify both key and subname groups match with correct captured text.
- The failure mode in the bug was that `group()` on the subname group returned `":name"` instead of `":name:subname"` — so asserting the exact captured string is essential.
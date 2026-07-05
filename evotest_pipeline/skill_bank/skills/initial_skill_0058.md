---
name: boosted-field-must-be-analyzed
description: When a property definition has a boost value set, the 'analyzed' flag
  must be forced to true. Test both explicitly-analyzed and non-analyzed boosted properties
  to verify analyzed=true is correctly enforced at the property level, regardless
  of the indexing rule level.
code_tags:
- NULL_CHECK
- STATE_MUTATION
test_pattern: STATE_TEST
---

# boosted-field-must-be-analyzed

## Instructions

# Boosted Field Must Be Analyzed

## Instructions

- WHEN the TG encounters code that constructs or initializes a `PropertyDefinition` object and checks if a `FIELD_BOOST` (the constant `"boost"`) property exists on the definition node to force `analyzed = true`
- THEN the TG should write a test that:
  1. Creates an index definition with an indexing rule containing a property definition that sets `boost` (e.g., `LuceneIndexConstants.FIELD_BOOST` with value `3.0`) but does NOT set `LuceneIndexConstants.PROP_ANALYZED` (the constant `"analyzed"`) explicitly.
  2. Obtains the `IndexingRule` from the `IndexDefinition` via `getApplicableIndexingRule(nodeType)`.
  3. Gets the `PropertyDefinition` for the boosted property via `rule.getConfig("propertyName")`.
  4. Asserts that `pd.analyzed` is `true` — because the presence of a `boost` value forces the field to be analyzed.
  5. Adds a second property definition that sets `boost` AND explicitly sets `analyzed = false`. Asserts that `pd.analyzed` is still `true` — because boost overrides the explicit `analyzed` setting.
  6. Verifies that a property definition with NO boost and NO explicit `analyzed` has `analyzed = false`.

- This skill targets the logic in `PropertyDefinition` constructor:
  ```java
  //If boost is specified then that field MUST be analyzed
  if (defn.hasProperty(FIELD_BOOST)){
      this.analyzed = true;
  } else {
      this.analyzed = getOptionalValue(defn, LuceneIndexConstants.PROP_ANALYZED, false);
  }
  ```
  The bug manifests when the `analyzed` field is `false` for a boosted property, which causes `skipTokenization` to return `true`, breaking fulltext search on that property. The triggering test expected 2 property definitions with `analyzed=true` but only got 1 — because the buggy code used `getOptionalValue(defn, FIELD_BOOST, DEFAULT_BOOST)` (defaulting boost) instead of `defn.hasProperty(FIELD_BOOST)` to decide if boost was set, never detecting the boost on nodes where the boost default was not overridden.

- Common pitfalls to avoid:
  - **Pitfall**: Testing only that the `IndexingRule` level boost forces `analyzed = true`, but failing to test at the individual `PropertyDefinition` level within a rule.
  - **Pitfall**: Assuming that if boost is set to its default value (e.g., `1.0f`), the code treats it as "no boost." The fix checks `defn.hasProperty(FIELD_BOOST)` — i.e., whether the property *node* literally has the `"boost"` property set, regardless of its value.
  - **Pitfall**: Not testing the case where `analyzed` is explicitly set to `false` alongside a boost — this is the exact scenario that would regress if someone refactors the `if` block ordering.
  - **Pitfall**: Using `getOptionalValue(defn, FIELD_BOOST, DEFAULT_BOOST) != DEFAULT_BOOST` to detect boost presence — this is exactly the buggy pattern. Always prefer `defn.hasProperty(FIELD_BOOST)` to detect whether a property exists on the node state.

### Correct test approach (pseudocode):
```java
@Test
public void analyzedEnabledForBoostedField() throws Exception {
    // Build index definition with two property definitions under an indexing rule
    NodeBuilder rules = builder.child(INDEX_RULES);
    NodeBuilder rule1 = rules.child("nt:base");
    NodeBuilder boostedAnalyzed = rule1.child("prop1");
    boostedAnalyzed.setProperty(LuceneIndexConstants.FIELD_BOOST, 3.0);

    NodeBuilder boostedNotAnalyzed = rule1.child("prop2");
    boostedNotAnalyzed.setProperty(LuceneIndexConstants.FIELD_BOOST, 3.0);
    boostedNotAnalyzed.setProperty(LuceneIndexConstants.PROP_ANALYZED, false);

    NodeBuilder noBoost = rule1.child("prop3");

    IndexDefinition idxDefn = new IndexDefinition(root, builder.getNodeState());
    IndexingRule rule = idxDefn.getApplicableIndexingRule(JcrConstants.NT_BASE);

    PropertyDefinition pd1 = rule.getConfig("prop1");
    assertTrue("Analyzed should be true for boosted property", pd1.analyzed);

    PropertyDefinition pd2 = rule.getConfig("prop2");
    assertTrue("Analyzed should still be true even if explicitly false with boost", pd2.analyzed);

    PropertyDefinition pd3 = rule.getConfig("prop3");
    assertFalse("Analyzed should be false for non-boosted property without explicit analyzed", pd3.analyzed);
}
```

### Incorrect approach (would miss the bug):
```java
// Only tests one scenario without covering the boost-overrides-analyzed=false case
PropertyDefinition pd = rule.getConfig("prop1");
assertTrue(pd.analyzed);
// Missing: second property definition that explicitly sets analyzed=false but has boost
```
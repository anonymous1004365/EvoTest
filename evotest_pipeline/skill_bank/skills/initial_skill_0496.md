---
name: index-cost-per-entry-by-version
description: When defining default cost-per-entry that depends on index version, tests
  must verify that older versions of Lucene indexes get different cost values than
  the latest. This skill detects bugs where version-aware defaults collapse to the
  same value due to early evaluation.
code_tags:
- ARGUMENT_VALIDATION
- NULL_CHECK
test_pattern: PARAMETRIC_TEST
---

# index-cost-per-entry-by-version

## Instructions

# Index Cost-Per-Entry by Version

## Instructions

- WHEN the TG encounters `IndexDefinition` (or similar class) where `getDefaultCostPerEntry(IndexFormatVersion version)` defines different cost values per version (e.g., `V1 -> 1.5`, `V2 -> 1.0`), and `costPerEntry` is initialized from `getDefaultCostPerEntry(version)` where `version` is a field of `IndexFormatVersion` type that may be resolved **before** being passed to the cost method

- THEN the TG should write a **parametric test** that:
  1. Creates the object under test with **each distinct `IndexFormatVersion` value** (e.g., `V1`, `V2`)
  2. Calls the method that exposes the computed cost (e.g., `getCostPerEntry()`)
  3. Asserts that **older versions produce a higher cost** than newer ones (e.g., `assertTrue(v1Cost > v2Cost)`)
  4. Uses `assertEquals(double, double, delta)` to verify each version's specific expected cost (e.g., `assertEquals(1.5, v1Cost, 0.0)`)

- **Common pitfalls to avoid:**
  - ❌ Testing only the *default* version (e.g., `V2`) — this misses the regression entirely
  - ❌ Reading the `version` field from the test fixture and then calling the helper directly — the bug is that the `version` used in the constructor may be evaluated **statically** before the method runs
  - ❌ Assuming `IndexFormatVersion.V1` is tested implicitly because it's an enum — the fix may involve ensuring the version is passed dynamically, so each version must be exercised explicitly
  - ❌ Using `assertTrue` without a delta on double comparisons when checking exact values

### Example: Correct test pattern

```java
@Test
public void costPerEntryForOlderVersion() throws Exception {
    // Version V1 should have higher costPerEntry than V2
    IndexDefinition defnV1 = createIndexDefinition(IndexFormatVersion.V1);
    IndexDefinition defnV2 = createIndexDefinition(IndexFormatVersion.V2);

    assertEquals(1.5, defnV1.getCostPerEntry(), 0.0);
    assertEquals(1.0, defnV2.getCostPerEntry(), 0.0);

    assertTrue("Old format must have higher costPerEntry",
        defnV1.getCostPerEntry() > defnV2.getCostPerEntry());
}
```

### Example: Incorrect test pattern (missing version variation)

```java
// BAD: Only tests default version
@Test
public void costPerEntryDefault() throws Exception {
    IndexDefinition defn = createIndexDefinition(IndexFormatVersion.V2);
    assertEquals(1.0, defn.getCostPerEntry(), 0.0);
    // V1 cost is never checked — bug stays hidden
}
```
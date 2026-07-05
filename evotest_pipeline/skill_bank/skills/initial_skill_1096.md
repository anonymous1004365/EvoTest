---
name: property-excludes-indexing-validation
description: When property definitions in index rules have 'excludes' configuration,
  the TG should verify that the exclusion actually prevents indexing of those properties.
  Tests must check that isIndexed() returns false for properties that should be excluded
  but could be falsely indexed due to incomplete exclusion logic.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
test_pattern: STATE_TEST
---

# property-excludes-indexing-validation

## Instructions

# Property Excludes Indexing Validation

## Instructions

- WHEN the TG encounters code that builds index property definitions with exclusion/excludes configuration (e.g., a `PROP_NODE` child node `"foo"` with property type set and no `INCLUDE_PROPERTY_NAMES` or `INCLUDE_PROPERTY_TYPES` specified), THEN the TG should test that properties defined under `PROP_NODE` are still indexed even without explicit include lists, AND that the `isIndexed()` method on the resulting `IndexingRule` correctly returns `true` for those properties. However, the TG should ALSO test scenarios where the property definition should NOT be indexed due to excludes — specifically, the TG should verify the exact expected behavior of `isIndexed()` for both included and non-included property names.

- WHEN testing `IndexDefinition` with property definitions that have a `PROP_TYPE` set (e.g., `PropertyType.TYPENAME_DATE`) but no `INCLUDE_PROPERTY_NAMES` or `INCLUDE_PROPERTY_TYPES` configured on the index definition node itself, THEN the TG should verify that ALL property names still return `true` from `isIndexed()` (since without explicit include/exclude lists, all properties of the matching type are indexed). For example: `rule.isIndexed("foo")` and `rule.isIndexed("bar")` should both be `true`.

- WHEN the TG writes tests for `propertyDefinitionWithExcludes` style scenarios, THEN it should verify that:
  - `rule.isIndexed("foo")` returns `true` for the property that has a `PROP_NODE` definition
  - `rule.isIndexed("bar")` returns `true` for properties without explicit `PROP_NODE` definitions (since no include/exclude filter list is specified)
  - `rule.getConfig("foo").getType()` returns the expected `PropertyType` (e.g., `PropertyType.DATE`)
  
- Common pitfalls to avoid:
  - Do NOT assume that a property defined under `PROP_NODE` automatically excludes all other properties — without `INCLUDE_PROPERTY_NAMES`, all property names are still indexed.
  - Do NOT confuse `PROP_NODE` property definitions (which define type/analyzer for specific properties) with `INCLUDE_PROPERTY_NAMES` (which restricts which properties are indexed at all) — they operate at different levels.
  - Do NOT test exclusion without also setting `INCLUDE_PROPERTY_NAMES` or `INCLUDE_PROPERTY_TYPES` — excludes only make sense when there is an explicit inclusion list to exclude from.
  - Do NOT forget to configure `PROP_NODE.child("foo").setProperty(PROP_TYPE, ...)` before creating the `IndexDefinition` to test per-property type configuration.

### Correct Test Pattern

```java
@Test
public void propertyDefinitionWithExcludes() throws Exception{
    builder.child(PROP_NODE).child("foo").setProperty(LuceneIndexConstants.PROP_TYPE, PropertyType.TYPENAME_DATE);
    IndexDefinition idxDefn = new IndexDefinition(root, builder.getNodeState(), "/foo");
    IndexingRule rule = idxDefn.getApplicableIndexingRule(NT_BASE);
    assertTrue(rule.isIndexed("foo"));
    assertTrue(rule.isIndexed("bar"));
    assertEquals(PropertyType.DATE, rule.getConfig("foo").getType());
}
```

### Incorrect Test Pattern

```java
@Test
public void propertyDefinitionWithExcludes_WRONG() throws Exception{
    // WRONG: Setting PROP_NODE without PROP_TYPE but expecting type to be inferred
    builder.child(PROP_NODE).child("foo");
    IndexDefinition idxDefn = new IndexDefinition(root, builder.getNodeState(), "/foo");
    IndexingRule rule = idxDefn.getApplicableIndexingRule(NT_BASE);
    assertFalse(rule.isIndexed("foo")); // WRONG: isIndexed returns true even without PROP_TYPE
    assertNull(rule.getConfig("foo")); // WRONG: config exists for "foo"
}
```
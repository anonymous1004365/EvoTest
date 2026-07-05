---
name: mixin-index-rule-node-type-resolution
description: When defining index rules with mixin types, the TG should verify that
  the same rule applies correctly for both the mixin type name (String) and the resolved
  node type (CtTypeReference). This catches bugs where the mixin type is stored internally
  as a String but NodeType resolution logic expects a different type.
code_tags:
- VALIDATION
- TYPE_CONVERSION
test_pattern: STATE_TEST
---

# mixin-index-rule-node-type-resolution

## Instructions

# Mixin Index Rule Node Type Resolution

## Instructions

- WHEN the TG encounters code that adds a mixin node type name (as a String) to an index rule definition, and the same code later resolves that mixin to a `CtTypeReference` for node type inheritance checking
- THEN the TG should write a test that:
  1. Creates an index definition that includes a mixin type (e.g., `"mix:language"`) via the index rules configuration
  2. Verifies that the index rule correctly matches nodes that have that mixin type applied
  3. The test should verify that the index definition is **not** empty/unset when the mixin type is used — i.e., `assertNotNull(indexDef.getApplicableRules())` or that the aggregate node type resolution includes the mixin's primary types
- Common pitfalls to avoid:
  - Testing only with primary node types (e.g., `"nt:base"`, `"oak:Resource"`) without mixin types
  - Testing only that the mixin type is stored as a String without verifying it resolves to a `CtTypeReference` for inheritance lookups
  - Assuming that if a mixin type name is added to a set, it automatically gets resolved for node type inheritance without explicit logic
  - Forgetting that the bug manifests when an aggregate node type list contains the mixin type as a String but the resolution code compares against `CtTypeReference` objects, causing a mismatch

### Correct Example

```java
@Test
public void indexRuleMixin() throws Exception {
    IndexDefinition idxDef = createIndexDefinition("test-index", "/oak:index/test-index",
        createIndexRulesDefinition(
            createRule(
                "nt:base",
                Collections.singletonList(createPropertyDefinition("jcr:title", false)),
                Collections.singletonList("mix:language")
            )
        ),
        true
    );
    
    // Verify the mixin type was properly resolved in the index definition
    assertNotNull("IndexDefinition should have applicable rules for mixin", 
        idxDef.getApplicableRules());
    
    // The aggregate definition should resolve mix:language to its node type
    assertNotNull("Aggregate for mix:language should be present",
        idxDef.getAggregateForNodeType("mix:language"));
}
```

### Incorrect Example

```java
// BAD: Only tests with primary node types, no mixin types
@Test
public void indexRulePrimaryOnly() throws Exception {
    IndexDefinition idxDef = createIndexDefinition("test-index", "/oak:index/test-index",
        createIndexRulesDefinition(
            createRule("nt:base", 
                Collections.singletonList(createPropertyDefinition("jcr:title", false)),
                Collections.emptyList()
            )
        ),
        true
    );
    
    // This test passes even when the mixin bug exists
    assertNotNull(idxDef.getApplicableRules());
}
```
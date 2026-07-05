---
name: creator-collector-property-conflict-validation
description: When a CreatorCollector or similar constructor/creator resolution system
  aggregates properties from multiple sources (e.g., fields vs constructors), tests
  must verify that a property defined in one source (like a field) is correctly matched
  and combined with the same property from another source (like a constructor parameter)
  instead of being treated as separate conflicting entries. Use this skill when examining
  deserialization or object construction code that merges property definitions.
code_tags:
- NULL_CHECK
- VALIDATION
- ALTERNATIVE_PROTOCOL_DECODING
- STATE_MUTATION
test_pattern: STATE_TEST
---

# creator-collector-property-conflict-validation

## Instructions

# CreatorCollector Property Conflict Validation

## Instructions

- WHEN the TG encounters code that collects/aggregates `SettableBeanProperty` instances from multiple origins (e.g., creator constructor parameters vs. fields), and these properties may refer to the same logical property (same name) defined in different ways (e.g., one has a `String` type from a constructor parameter, another has a `CtTypeReference` type from a field annotation)
- THEN the TG should write a test that creates a scenario where the **same property name** is contributed by two different sources with **different property type representations** (e.g., `String` from one source, `CtTypeReference` from another), and verify that the code correctly matches them as the same property (returning the merged/combined result) rather than treating them as conflicting duplicates (which would throw an exception like `IllegalArgumentException`).
- Specifically, the test should:
  1. Construct or mock `SettableBeanProperty` instances with the same name but different type representations.
  2. Pass them into the property aggregation logic (e.g., `_addCreators`, `addProperty`, or similar collection methods).
  3. Verify that no exception is thrown and the property collection contains exactly one entry for that name (not two separate entries with the same name).
- Common pitfalls:
  - Testing only with properties from a single source (e.g., only constructor parameters) — this misses the conflict path entirely.
  - Using identical property type representations for both sources — this would not trigger the bug.
  - Simply validating that no exception is thrown without also checking that the final collection size is correct (1 entry, not 2).
  - Assuming that constructor-based properties always take precedence over field-based ones without verifying correct deduplication.

### Example (Correct Test)
```java
// Given a CreatorCollector or similar class that merges properties from different sources
SettableBeanProperty prop1 = new SettableBeanProperty("name", String.class, ...); // from constructor
SettableBeanProperty prop2 = new SettableBeanProperty("name", new CtTypeReference(...), ...); // from field

CreatorCollector collector = new CreatorCollector(...);
collector.addProperty(prop1);  // e.g., _addCreators
collector.addProperty(prop2);  // same property name, different type representation

// Verify no exception and correct aggregation
assertNotNull(collector.getProperty("name"));
assertEquals(1, collector.getPropertyCount());
```

### Example (Incorrect Test — would miss the bug)
```java
// Only testing a single source — won't expose the conflict
SettableBeanProperty prop1 = new SettableBeanProperty("name", String.class, ...);
CreatorCollector collector = new CreatorCollector(...);
collector.addProperty(prop1);
// Never adds the conflicting property from the other source
assertNotNull(collector.getProperty("name"));
```
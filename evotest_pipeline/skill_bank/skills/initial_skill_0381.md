---
name: index-lookup-fallback-validation
description: When a Property2IndexLookup.find() method silently falls back to a full
  tree scan for properties not found in the index, the TG should test that the method
  throws an IllegalArgumentException instead of performing expensive fallback logic.
  This skill applies when testing index lookup for property names that have no matching
  index definition.
code_tags:
- VALIDATION
- INDEX_LOOKUP_FALLBACK
test_pattern: EXCEPTION_TEST
---

# index-lookup-fallback-validation

## Instructions

# Index Lookup Fallback Validation

## Instructions

WHEN the TG encounters a `Property2IndexLookup.find(String name, PropertyValue value)` method that:
- Looks up an index definition node via `getIndexDefinitionNode(name)` 
- Falls back to a full tree traversal (recursive scanning of all child nodes) when the index definition is missing

THEN the TG should test that:
1. Calling `find("someProperty", someValue)` where `"someProperty"` is NOT listed in any index definition's `propertyNames` should throw an **`IllegalArgumentException`** with message `"No index for someProperty"` (or similar)
2. The test must verify the exception is thrown (e.g., using `try { ... fail(); } catch (IllegalArgumentException e) { /* expected */ }` or JUnit's `@Test(expected = IllegalArgumentException.class)`)
3. The test must create an index definition that indexes different properties than the one being queried — for example, index `"foo"` and `"extrafoo"` but query `"pqr"` (a property name that exists on nodes but has no index definition)

Common pitfalls to avoid:
- Testing only with properties that DO have an index definition (this would not trigger the bug)
- Assuming that a property existing on content nodes is sufficient to be indexable — the property must be listed in the index definition's `propertyNames`
- Forgetting to build and apply the index (using `Property2IndexDiff`) before querying — without this, the `:index` child node won't exist
- Relying solely on `assertEquals(ImmutableSet.of(), lookup.find("pqr", "foo"))` — the old buggy code returned an empty set silently, but the fixed code correctly throws an exception

Correct example (Java with JUnit 4):

```java
// Setup: index definition for "foo" and "extrafoo" only
NodeBuilder builder = root.builder();
builder.child("oak:index").child("fooIndex")
    .setProperty("jcr:primaryType", "oak:queryIndexDefinition", Type.NAME)
    .setProperty("type", "p2")
    .setProperty("propertyNames", Arrays.asList("foo", "extrafoo"), Type.STRINGS);
NodeState before = builder.getNodeState();

// Add content
builder = before.builder();
builder.child("a").setProperty("foo", "abc").setProperty("extrafoo", "pqr");
NodeState after = builder.getNodeState();

// Build index
IndexHook p = new Property2IndexDiff(builder);
after.compareAgainstBaseState(before, p);
p.apply();
p.close();

// Query for a property NOT in the index definition
Property2IndexLookup lookup = new Property2IndexLookup(builder.getNodeState());
try {
    lookup.find("pqr", "foo");
    fail("Expected IllegalArgumentException for unindexed property 'pqr'");
} catch (IllegalArgumentException e) {
    // expected: "No index for pqr"
}
```

Incorrect example (would pass with the buggy version but should NOT pass after the fix):

```java
// BAD: silently accepts a non-indexed property and returns empty set
Property2IndexLookup lookup = new Property2IndexLookup(builder.getNodeState());
assertEquals(ImmutableSet.of(), lookup.find("pqr", "foo")); // BUGGY! This will fail on the fixed version
```
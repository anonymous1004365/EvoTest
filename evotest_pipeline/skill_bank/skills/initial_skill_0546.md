---
name: index-tag-and-name-disambiguation
description: Teaches how to write tests that verify index planning correctly filters
  indexes by tag AND name options, ensuring multi-index resolution returns the correct
  index and not a wrong one based solely on partial matching.
code_tags:
- ARGUMENT_VALIDATION
- BOUNDARY_CHECK
- NULL_CHECK
test_pattern: STATE_TEST
---

# index-tag-and-name-disambiguation

## Instructions

# Index Tag and Name Disambiguation

## Instructions

WHEN the TG encounters code that selects an index from multiple candidate indexes based on property restrictions like `INDEX_TAG_OPTION` ("indexTag") or `INDEX_NAME_OPTION` ("indexName") in a `QueryEngine` or `IndexPlanner` context,

THEN the TG should write a test that:
1. Registers at least **two distinct indexes** with **different index definitions** (e.g., one property index for "jcr:title" and another for "jcr:description") so that the planner has multiple candidates to choose from.
2. One index must have a **tag** set (via `IndexConstants.INDEX_TAG_OPTION`) and the other must have a **different tag** (or none), creating a scenario where tag-based filtering is necessary to pick the correct index.
3. The query must include a filter restriction on the **tag** property (e.g., `filter.getPropertyRestriction("indexTag")`) to force the planner to disambiguate using the tag value.
4. **Verify** that the query returns results from the **correct** index (the one matching both the tag and the indexed property), and does **not** accidentally return results from the wrong index that would otherwise match only on the indexed property name without checking the tag.
5. Expect that without correct tag filtering, the buggy planner returns 0 results (because the wrong index is selected and its index data does not contain the queried property), while the fixed planner returns the expected number of results (e.g., 2).

**Common pitfalls to avoid:**
- Testing with only a single index — this hides tag-disambiguation bugs because there is no wrong index to accidentally select.
- Testing with indexes that have identical indexed property names — the bug is about selecting the WRONG index (by name/tag), not about the index content itself.
- Forgetting to include the tag restriction in the query filter — without it, the planner never exercises the tag-matching code path.
- Assuming that index selection is purely name-based — the bug shows that a name-only match on `indexName` can override a tag-based match on `indexTag`, leading to the wrong index.

### Example (Correct Test)

```java
// Setup two property indexes with different tags
NodeBuilder indexDefs = root.builder().child("oak:index");

// Index1: tags = "tagA", indexes "jcr:title"
IndexUtils.createIndexDefinition(
    indexDefs.child("index1"),
    "index1", false, false,
    ImmutableList.of("jcr:title"), null, 
    ImmutableMap.of("tags", "tagA")
);

// Index2: tags = "tagB", indexes "jcr:description"  
IndexUtils.createIndexDefinition(
    indexDefs.child("index2"),
    "index2", false, false,
    ImmutableList.of("jcr:description"), null,
    ImmutableMap.of("tags", "tagB")
);

// Add content nodes
root.child("content1").setProperty("jcr:title", "Hello");
root.child("content2").setProperty("jcr:title", "World");

Tree indexTree = root.getTree("/oak:index");
Planner planner = new Planner(indexTree, ...);

// Query with filter that includes indexTag restriction
PropertyRestriction tagRestriction = new PropertyRestriction();
tagRestriction.propertyName = "indexTag";
tagRestriction.first = "tagA";
Filter filter = new Filter(...);
filter.addPropertyRestriction(tagRestriction);

// Execute query
List<String> result = planner.query(filter);

// Verify: should return 2 results because index1 (tagA, jcr:title) is selected
assertEquals("Should find 2 nodes via correct index", 2, result.size());
```

### Example (Incorrect Test)

```java
// BAD: Only one index registered — no disambiguation needed
NodeBuilder indexDefs = root.builder().child("oak:index");
IndexUtils.createIndexDefinition(
    indexDefs.child("myIndex"),
    "myIndex", false, false,
    ImmutableList.of("jcr:title"), null, 
    ImmutableMap.of("tags", "tagA")
);

// BAD: No tag restriction in filter
Filter filter = new Filter(...);
// No restriction on "indexTag" added

List<String> result = planner.query(filter);

// BAD: This passes even on buggy code because there's only one index to choose
assertEquals("Should find nodes", 2, result.size());
```
---
name: fulltext-term-name-parsing
description: When testing full-text search with property name syntax like [propName]=[value],
  ensure the parser correctly handles terms that contain dots (e.g. 'file.txt') by
  preserving the dot as part of the value rather than treating it as a property-name
  delimiter.
code_tags:
- NULL_CHECK
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# fulltext-term-name-parsing

## Instructions

# Full-Text Term Name Parsing with Dots

## Instructions

WHEN the code under test is a full-text parser (e.g., `FullTextParser`) that supports `[propertyName]=[termValue]` syntax in full-text search queries (e.g., `jcr:contains(@prop, 'name=file.txt')`) and the format allows a property name followed by `=` followed by a term value,

THEN the TG should:

1. **Test with term values that contain dots**: Create test queries where the value after `=` contains a period/dot (e.g., `name=file.txt` or `name=my.file.name`). This targets the bug where the parser incorrectly splits on the dot, treating part of the value as a property name.

2. **Assert the correct parsing**: Verify that `FullTextParser.parse(...)` produces a `FullTextTerm` (or equivalent) where:
   - The `getPropertyName()` returns the full property name before the `=` (e.g., `"name"`)
   - The `getText()` or `getValue()` returns the full value including the dot (e.g., `"file.txt"`)
   - NOT a `FullTextContains` expression with only the portion before the dot

3. **Test with simple (dot-free) values too**: Include tests with simple values (e.g., `name=simpleValue`) to ensure backward compatibility — the parser must handle both cases correctly.

4. **Expect the buggy version to return wrong results**: When querying with the TraversingIndex or executing a SQL2/XPath query with `jcr:contains()`, the buggy version will fail to match nodes when the term value contains dots. Assert the query returns the correct result count (e.g., 1 instead of 0).

**Common pitfalls to avoid:**

- Testing only property-name syntax without dots — this will not catch the bug.
- Testing only `FullTextParser.parse(...)` on strings without dots — the bug manifests only when dots are present in the value part of a `[prop]=[value]` pattern.
- Assuming validation of the input string happens before parsing — the bug is in the parsing logic itself.
- Using only a single node with a simple name — the test must verify that a node with a dotted name (e.g., `testFullTextTermNameFile.txt`) is queryable by its full name.

**Example (correct):**

```java
// Test with a term value containing a dot in a property-name query
FullTextExpression exp = FullTextParser.parse("name", "name=file.txt");
assertNotNull(exp);
assertTrue("Expected FullTextTerm", exp instanceof FullTextTerm);
FullTextTerm term = (FullTextTerm) exp;
assertEquals("name", term.getPropertyName());
assertEquals("file.txt", term.getText());
```

**Example (incorrect — would miss the bug):**

```java
// Only tests simple values without dots — won't catch the parsing bug!
FullTextExpression exp = FullTextParser.parse("name", "name=simpleValue");
assertNotNull(exp);
assertTrue(exp instanceof FullTextTerm);
assertEquals("simpleValue", ((FullTextTerm) exp).getText());
```
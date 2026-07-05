---
name: xpath-to-sql2-or-to-in-optimization
description: WHEN converting XPath queries with multiple OR conditions on the same
  property to SQL2, THEN verify the converter produces an optimized IN clause. Use
  this skill to test that XPath OR chains on identical properties are collapsed into
  a single SQL IN expression.
code_tags:
- NULL_CHECK
- STATE_MUTATION
- VALIDATION
- XPATH_TO_SQL2_IN_OPTIMIZATION
test_pattern: PARAMETRIC_TEST
---

# xpath-to-sql2-or-to-in-optimization

## Instructions

# XPath OR-to-IN Optimization

## Instructions

WHEN the TG encounters XPath-to-SQL2 conversion logic (e.g., `XPathToSQL2Converter`) that processes XPath queries containing multiple OR conditions on the **same property** (e.g., `@type='t1' or @type='t2' or @type='t3'`):

THEN it should test that the converter produces an optimized `IN` clause instead of keeping the OR chain. Write a parametric test that:

1. Constructs XPath queries with **3 or more OR conditions on the same property** (e.g., `[@prop='a' or @prop='b' or @prop='c']` — note: at least 3 values triggers the optimization).
2. Passes the XPath through `XPathToSQL2Converter().convert(query)`.
3. Asserts that the resulting SQL2 string contains a single `IN` clause like `[prop] IN('a', 'b', 'c')`.
4. Tests with various property names and value counts (minimum 3, also try 2 to verify boundary).

Key verification points:
- The `IN` clause must use **parentheses and single quotes**: `IN('value1', 'value2')`
- The property must be wrapped in brackets: `[propertyName]`
- All property values from the OR conditions must appear in the `IN` list
- The test uses `String.contains()` to verify the expected `IN` clause token is present

**Common pitfalls to avoid:**
- The TG might test with only 2 OR conditions — the optimization may only trigger with 3+ values, so test both 2-value and 3+ value cases.
- The TG might check the entire output string; instead, verify only that the `IN` clause pattern is present somewhere in the result using `assertTrue(q.contains(token))`.
- The TG might forget to wrap property values in single quotes inside the IN clause.
- The TG might test an incorrect property name — use the exact property name from the XPath expression.

**Example (correct test):**
```java
@Test
public void testUnwrappedOr() throws ParseException {
    String q = new XPathToSQL2Converter()
            .convert("/jcr:root/home//test/* [@type='t1' or @type='t2' or @type='t3']");
    String token = "and b.[type] in('t1', 't2', 't3')";
    assertTrue(q.contains(token));
}
```

**Example (incorrect test — 2 values only, may not trigger optimization):**
```java
// This may not trigger the IN optimization (only 2 values)
@Test
public void testOrToIn_TwoValues() throws ParseException {
    String q = new XPathToSQL2Converter()
            .convert("/jcr:root/test/* [@type='a' or @type='b']");
    // This assertion might fail if 2 values are kept as OR
    assertTrue(q.contains("in('a', 'b')"));
}
```
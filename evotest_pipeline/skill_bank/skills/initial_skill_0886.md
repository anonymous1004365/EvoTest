---
name: xpath-to-sql2-conversion-coverage
description: When converting XPath queries to SQL-2 format, the test must cover a
  comprehensive set of XPath syntax variants including edge cases like multiple predicates,
  namespace wildcards, and complex path expressions, not just simple queries. Use
  the test resource file pattern to ensure all conversion paths are exercised.
code_tags:
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# xpath-to-sql2-conversion-coverage

## Instructions

# Comprehensive XPath to SQL-2 Conversion Testing

## Instructions

- WHEN the TG encounters XPath-to-SQL2 conversion logic (e.g., `XPathToSQL2Converter`) that processes XPath query strings and transforms them into SQL-2 format
- THEN the TG should verify the conversion produces correct SQL-2 output for a **comprehensive set of XPath syntax variants**, including:
  - **Simple element paths**: `/jcr:root/content//element(*, nt:unstructured)`
  - **Multiple predicates**: `/jcr:root//element(*, nt:unstructured)[@a = '1' and @b = '2']`
  - **Order-by clauses**: `/jcr:root/* order by @jcr:path`
  - **Explain queries**: `explain /jcr:root//element(*, nt:unstructured)[@x=1]`
  - **Namespace wildcards**: `/jcr:root//*[@foo]`
  - **Complex path filters**: paths with `//` (descendant-or-self) and `/*` (child wildcard)
  - **Function calls in predicates**: `fn:name()` etc.
  - **Comparison edge cases**: `@property = ''` (empty string), `@property != 'value'` (not-equals)
  - **Union expressions**: `(/a | /b)`
- Use a **parametric/example-driven test approach** modeled after the `AbstractQueryTest` pattern: read test cases from a resource file (e.g., `xpath.txt` or an equivalently structured file), where each line contains an XPath expression and its expected SQL-2 conversion, separated by a delimiter.
- Compare **actual output** (converted SQL-2) against **expected output** for each test case. Report mismatches with line numbers or identifiers so the developer can locate the failing case.
- **Common pitfalls to avoid**:
  - Testing only a single XPath query — this misses edge cases in predicate parsing, ordering, namespaces, and wildcards.
  - Manually asserting each conversion in code (brittle, hard to extend). Use a data-driven approach with resource files.
  - Forgetting to test `explain` prefix handling or union expressions.
  - Assuming all XPath features are supported — the test should verify both supported and unsupported (expected to throw) syntaxes.
  - Not cleaning up test resources (temporary index definitions, nodes created for query testing) between test runs.

- **Correct example** (data-driven approach):
  ```java
  // In test resource file xpath.txt:
  // /jcr:root//element(*, nt:unstructured) -> SELECT * FROM [nt:unstructured]
  // /jcr:root//element(*, nt:unstructured)[@a='1'] -> SELECT * FROM [nt:unstructured] WHERE [a] = '1'
  
  // In test:
  @Test
  public void testXPathConversions() throws Exception {
      test("xpath.txt");  // reads all cases from resource file
  }
  ```

- **Incorrect example** (insufficient coverage):
  ```java
  // BAD: Only tests one simple path
  @Test
  public void testXPath() throws Exception {
      String sql2 = converter.convert("/jcr:root//element(*, nt:unstructured)");
      assertEquals("SELECT * FROM [nt:unstructured]", sql2);
  }
  ```
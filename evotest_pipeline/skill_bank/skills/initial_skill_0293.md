---
name: query-result-values-on-mvp-selective-columns
description: When writing tests for JCR query results that use `Row.getValues()` on
  multi-valued properties (MVPs), the TG should test selective column retrieval to
  catch `ArrayIndexOutOfBoundsException` or `NullPointerException` caused by incorrect
  column index mapping when not all columns are selected.
code_tags:
- NULL_CHECK
- STATE_MUTATION
- BOUNDARY_CHECK
test_pattern: PARAMETRIC_TEST
---

# query-result-values-on-mvp-selective-columns

## Instructions

# Query Result Values on Multi-Valued Properties (MVPs)

## Instructions

- WHEN the TG encounters a test that executes a JCR query (via `javax.jcr.query.Query`, `QueryManager`, `QueryResult`, `RowIterator`, `Row`) and calls `Row.getValues()` on results that include multi-valued properties (MVPs) — i.e., properties with multiple values set via `Node.setProperty("propName", new String[]{"val1", "val2"})` or similar array/set values
- THEN the TG should write tests that call `Row.getValues()` and verify the returned `Value[]` array has the correct length matching the number of *selected* columns, not the total number of properties in the result. On the buggy version, calling `getValues()` on a result with selective columns (e.g., not using `SELECT *`) may throw an `ArrayIndexOutOfBoundsException` or return incorrect values when MVP columns are present.
- Include concrete test data: create a node with at least one single-valued property (e.g., `setProperty("text", "hello")`) and one multi-valued property (e.g., `setProperty("mvp", new String[]{"a", "b"})`) under the same node, execute a JCR_SQL2 query that selects specific columns (e.g., `SELECT text, mvp FROM [nt:base] WHERE ...`), call `Row.getValues()`, and verify the array length and the values.
- WHEN writing the assertion, verify that `row.getValues().length` equals the number of selected columns (e.g., 2 for `SELECT text, mvp`). On the buggy version, the length may be incorrect or an exception may be thrown.
- Common pitfall to avoid: testing only with `SELECT *` queries or testing only with single-valued properties. Without testing selective column retrieval on multi-valued properties, the `ArrayIndexOutOfBoundsException` in the column index mapping code will not be triggered. Also avoid using only `Row.getValue("columnName")` — that API may work while `Row.getValues()` breaks.

**Correct example (bug-triggering test):**
```java
@Test
public void testGetValuesOnMvp() throws RepositoryException {
    Session session = getAdminSession();
    Node n = session.getRootNode().addNode("testNode");
    n.setProperty("text", "hello");
    n.setProperty("mvp", new String[]{"a", "b"});
    session.save();

    Query q = session.getWorkspace().getQueryManager().createQuery(
        "SELECT text, mvp FROM [nt:base] WHERE [jcr:path] LIKE '/testNode%'",
        Query.JCR_SQL2);
    QueryResult r = q.execute();
    RowIterator it = r.getRows();
    assertTrue(it.hasNext());
    Row row = it.nextRow();
    Value[] values = row.getValues();
    assertEquals(2, values.length);
    assertEquals("hello", values[0].getString());
    // On buggy version, this may throw ArrayIndexOutOfBoundsException
}
```

**Incorrect example (will not catch the bug):**
```java
@Test
public void testGetValuesOnMvp() throws RepositoryException {
    Session session = getAdminSession();
    Node n = session.getRootNode().addNode("testNode");
    n.setProperty("text", "hello");
    n.setProperty("mvp", new String[]{"a", "b"});
    session.save();

    // Using SELECT * will not trigger the bug
    Query q = session.getWorkspace().getQueryManager().createQuery(
        "SELECT * FROM [nt:base] WHERE [jcr:path] LIKE '/testNode%'",
        Query.JCR_SQL2);
    QueryResult r = q.execute();
    RowIterator it = r.getRows();
    assertTrue(it.hasNext());
    Row row = it.nextRow();
    // This call may work fine with SELECT *
    Value[] values = row.getValues();
    // Missing assertion on length and selective column correctness
}
```
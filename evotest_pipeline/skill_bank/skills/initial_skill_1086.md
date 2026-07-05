---
name: import-handling-null-safe-visitor-collection
description: When collecting imports for code generation, the visitor must handle
  null return values from child visits gracefully, adding only non-null results. This
  skill applies to any code that traverses a tree structure and accumulates results
  from child node visitors.
code_tags:
- VALIDATION
- NULL_CHECK
test_pattern: STATE_TEST
---

# import-handling-null-safe-visitor-collection

## Instructions

# Null-Safe Visitor Collection for Import Handling

## Instructions

- WHEN the TG encounters code that traverses an AST or tree structure and collects results from child node visitors (e.g., scanning for imports, types, or declarations by visiting children and accumulating results into a collection)
- THEN it should test that null return values from child visits are handled correctly — specifically that a null returned by a child visitor does not cause a NullPointerException when added to a collection, and that only non-null results are added
- Concrete example: When collecting imports by recursively visiting children (e.g., via `scan()` or `accept()` methods on AST nodes), the test should:
  1. Create a scenario where importing a class (e.g., from a package like `com.foo`) is expected to produce import references
  2. Verify that the import collection process does not throw a NullPointerException
  3. Verify that the resulting collection contains the expected number of import entries (not missing any due to null filtering)
- Common pitfalls to avoid:
  - Testing only with imports that produce non-null return values, missing the null case entirely
  - Writing tests that pass with the buggy version because they don't exercise paths that return null from child visitors
  - Assuming that all child visitor calls return a valid object — always test with AST structures where intermediate nodes may return null from their visitor methods

## Correct Test Example

```java
// Test that import collection works even when some nodes return null from visits
@Test
public void testImportCollectionHandlesNullChildResults() {
    // Arrange: create code with imports where some intermediate AST nodes
    // might return null from their accept/scan methods
    String code = "import com.foo.Bar; class A extends Bar {}";
    
    // Act & Assert: the import collection should not NPE
    assertDoesNotThrow(() -> {
        Collection<Import> imports = collector.scan(code);
        // Verify the expected import was collected
        assertEquals(1, imports.size());
    });
}
```

## Incorrect Test Example (would not catch the bug)

```java
// BAD: Only tests with simple imports that always return non-null
@Test
public void testSimpleImport() {
    String code = "import java.util.List;";
    Collection<Import> imports = collector.scan(code);
    assertEquals(1, imports.size());
    // This passes even with the bug because no null returns are triggered
}
```
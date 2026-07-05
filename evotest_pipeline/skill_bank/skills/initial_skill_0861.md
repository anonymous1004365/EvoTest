---
name: pageable-listview-empty-page-count
description: When testing PageableListView or similar pageable components with zero
  items (empty list), the TG should verify division operations that use itemsPerPage
  as a denominator do not cause ArithmeticException. Also test edge cases where itemsPerPage
  is zero to ensure getPageCount() and getCurrentPage() handle division safely.
code_tags:
- BOUNDARY_CHECK
- STATE_MUTATION
- VALIDATION
- DIVISION_BY_ZERO
- ARITHMETIC_OVERFLOW
test_pattern: PARAMETRIC_TEST
---

# pageable-listview-empty-page-count

## Instructions

# PageableListView Empty List Division Safety

## Instructions

- WHEN the TG encounters a method that computes page counts using a formula like `((itemCount + itemsPerPage) - 1) / itemsPerPage` (e.g., `PageableListView.getPageCount()`)
- THEN the TG should create a test where the underlying list is empty (size=0) AND itemsPerPage is any positive value, and verify that `getPageCount()` returns 0 without throwing an ArithmeticException
- ALSO test the edge case where itemsPerPage is set to 0 (via `setItemsPerPage(0)`) with a non-empty list, and verify that `getPageCount()` does not throw an ArithmeticException from division by zero — the method returns a `long` and the division `(itemCount + 0 - 1) / 0` will throw an `ArithmeticException` on the buggy version
- ALSO test the `setCurrentPage(0)` behavior with an empty list: `getCurrentPage()` should return 0 without looping infinitely or throwing an exception

- Common mistakes to avoid:
  - Testing only with non-empty lists — the bug manifests specifically with empty lists (itemCount == 0)
  - Testing only with positive itemsPerPage values — the setters clamp negative values to 0, so itemsPerPage==0 is reachable via setItemsPerPage(-1) or setItemsPerPage(0)
  - Assuming `getPageCount()` returns correctly without checking for the ArithmeticException on the buggy version — the fix likely changes the formula to handle itemsPerPage==0

### Correct example:
```java
// Empty list with positive itemsPerPage
PageableListView<?> table = createTable(0, 4);
assertEquals(0, table.getPageCount()); // No exception, returns 0

// Non-empty list with itemsPerPage set to 0 (from negative clamp)
table = createTable(10, 4);
table.setItemsPerPage(-1); // clamps to 0
// On buggy version: ArithmeticException: / by zero in getPageCount()
// On fixed version: should handle gracefully (e.g., return 0 or 1)
```

### Incorrect example:
```java
// Only testing non-empty lists
PageableListView<?> table = createTable(20, 4);
assertEquals(5, table.getPageCount()); // Works fine, but misses the bug

// Not testing itemsPerPage=0 edge case
table.setItemsPerPage(0);
table.getPageCount(); // Never called in test — the bug remains hidden
```
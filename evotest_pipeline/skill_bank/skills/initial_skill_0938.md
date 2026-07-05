---
name: duplicate-sheet-header-validation
description: When iterating over Excel sheets that might have duplicate headers, verify
  that the implementation properly warns or throws on duplicate column names instead
  of silently returning duplicate columns.
code_tags:
- VALIDATION
test_pattern: EXCEPTION_TEST
---

# duplicate-sheet-header-validation

## Instructions

# Duplicate Sheet Header Validation

## Instructions

- WHEN the TG encounters code that parses Excel sheet headers and maps column names to column indices (e.g., building a header-to-index map from the first row of an Excel sheet)
- THEN the TG should write a test that provides an Excel sheet with duplicate column header names (e.g., two columns both named "header") and verify that:
  - The parsing logic correctly detects the duplicate
  - Either an exception is thrown (e.g., `DuplicateHeaderException`) or a warning is logged, depending on the implementation's contract
  - The test expects the EXACT exception type/message that the implementation should produce
- Common pitfalls to avoid:
  - Testing only with unique headers and assuming duplicate handling works
  - Verifying that an exception is thrown but not checking the EXCEPTION TYPE and MESSAGE
  - Testing with duplicate values in data rows instead of duplicate HEADERS (first row/column names)
  - Using a mock Excel workbook that doesn't faithfully reproduce the real library's behavior

### Correct Example (detecting the bug):
```java
@Test(expectedExceptions = DuplicateHeaderException.class) 
public void iteratorDuplicateSheetHeader() {
    // Create an Excel sheet with duplicate column headers "header" and "header"
    // Expect specific DuplicateHeaderException to be thrown
    ExcelRepository excelRepository = ...;
    for (Tuple tuple : excelRepository) {
        // Should throw before entering the loop
    }
}
```

### Incorrect Example (missing the bug):
```java
@Test
public void iteratorSheetHeader() {
    // Only testing with unique headers - misses the duplicate bug entirely
    ExcelRepository excelRepository = ...;
    for (Tuple tuple : excelRepository) {
        // Works fine with unique headers, but silently fails with duplicates
    }
}
```
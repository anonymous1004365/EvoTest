---
name: excel-cell-type-conversion-validation
description: When testing Excel cell set/get operations that involve type conversions
  (e.g., String to Date, CtTypeReference to String), the TG should verify that values
  written to cells can be correctly read back and that parsing handles edge cases
  like invalid date strings without crashing.
code_tags:
- ARGUMENT_VALIDATION
- BOUNDARY_CHECK
- EDGE_CASE_INPUT
- TYPE_CONVERSION
- STATE_MUTATION
- VALIDATION
test_pattern: STATE_TEST
---

# excel-cell-type-conversion-validation

## Instructions

# Excel Cell Type Conversion Validation

## Instructions

- **WHEN** testing Excel cell operations that set values of one type (e.g., `String`) with a format that implies another type (e.g., a time pattern like `HH:mm`),
  - **THEN** the test should:
    1. Write a value using `setCellValue()` (e.g., with a `String` parameter representing a time like `"12:00"`)
    2. Apply cell formatting/style that implies a time/date format
    3. Read back the cell value using `getDateCellValue()` (or the appropriate type-getter)
    4. **Verify** that the read-back value is not `null` and represents the expected time/date correctly
  - **Common pitfall**: Only testing string-based read-back (`getStringCellValue()`) while ignoring that the underlying Excel API might store the value as a `Date` internally, causing `getDateCellValue()` to return `null` or throw an exception on the buggy version.
  - **Example (correct)**: 
    ```java
    HSSFWorkbook wb = new HSSFWorkbook();
    HSSFSheet sheet = wb.createSheet();
    HSSFRow row = sheet.createRow(0);
    HSSFCell cell = row.createCell(0);
    CellStyle style = wb.createCellStyle();
    style.setDataFormat(wb.createDataFormat().getFormat("HH:mm"));
    cell.setCellStyle(style);
    cell.setCellValue("12:00");
    // Verify both string and date read-back
    assertNotNull(cell.getStringCellValue());
    // This next assertion may fail in the buggy version if type conversion is broken
    assertNotNull("getDateCellValue() should not return null after setCellValue with time string", cell.getDateCellValue());
    ```
  - **Example (incorrect)** — only checks string value, missing the date conversion bug:
    ```java
    // BAD: Only checks getStringCellValue(), misses the type conversion issue
    assertEquals("12:00", cell.getStringCellValue());
    // BUGGY version may have null getDateCellValue() — not tested here
    ```
  - **Mistakes to avoid**:
    - Do NOT assume `setCellValue(String)` only stores the string as-is — it may perform type inference/conversion based on cell style.
    - Do NOT skip assertions on alternate getters (`getDateCellValue()`, `getNumericCellValue()`) when the cell style implies a different data type.
    - Do NOT assume that just because `setCellValue` doesn't throw, the cell's internal state is consistent across all type accessors.
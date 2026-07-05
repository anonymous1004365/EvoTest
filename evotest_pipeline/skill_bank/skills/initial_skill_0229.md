---
name: csv-iterator-header-value-mismatch
description: When iterating over CSV data where headers and row values may be misaligned,
  test that iterator correctly throws an exception when row has fewer non-empty values
  than expected from headers — specifically when non-empty row values are fewer than
  header columns.
code_tags:
- VALIDATION
- EDGE_CASE_INPUT
- STATE_MUTATION
test_pattern: EXCEPTION_TEST
---

# csv-iterator-header-value-mismatch

## Instructions

# CSV Iterator Header-Value Mismatch Detection

## Instructions

- WHEN the TG encounters a CSV reading utility/iterator that is responsible for mapping header columns to row values (e.g., a class like `CsvIterator` that reads CSV files and creates a map from header names to cell values)
- THEN the TG should test the scenario where a data row contains some **empty string values**, and the number of **non-empty** values in the row is **less** than the number of header columns. The test must verify that the iterator throws an appropriate exception (e.g., `RuntimeException`, `IllegalStateException`, or `NoSuchElementException`) indicating a value/header mismatch.
- Specifically: create a CSV with, for example, three header columns `["header1", "header2", "header3"]` but a data row like `",,nonempty"` or `",,value"` — where only **one** cell contains non-empty content, the other two are empty. The iterator should detect that the non-empty value count (1) does not match the header count (3) and throw an exception.
- Make sure to test with different numbers of non-empty values (0, 1, 2, etc.) relative to header column count to ensure the validation is consistent.
- **Common pitfall**: Testing only with completely empty rows or rows with the exact correct number of values. The bug is specifically about **non-empty** cell count vs header count, not cell count vs header count. Do not test with rows that have the right number of values but are all non-empty — those would pass. The iterator might incorrectly check `rowValues.length != headers.length` instead of checking non-empty value count.
- **Correct test example**: A row with values `["", "", "value"]` (length 3) and headers `["h1", "h2", "h3"]` (length 3) — the array lengths match but non-empty value count (1) mismatches, so an exception should be thrown.
- **Incorrect test example**: Only testing `["a", "b"]` with 3 headers — this also raises an exception but doesn't exercise the specific non-empty count logic.
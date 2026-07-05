---
name: quoted-csv-string-escaping
description: When parsing CSV with quoted strings, test that escaped quote characters
  inside quoted fields (e.g., \" or "") are handled correctly. Also test that field
  delimiters inside quoted strings are not treated as record separators. This is particularly
  important for GenericCsvInputFormat and similar CSV/TSV parsers.
code_tags:
- STRING_PARSING_ESCAPING
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# quoted-csv-string-escaping

## Instructions

# Quoted CSV String Escape Handling

## Instructions

- WHEN the TG encounters a CSV or delimited input format class (e.g., `GenericCsvInputFormat`, `CsvInputFormat`, or similar formats that support `enableQuotedStringParsing(char quoteCharacter)`)
- THEN it MUST test that escaped quote characters inside quoted string fields are parsed correctly. Specifically:
  1. Create a test input file containing a line such as `"ab\"c"|"def"` (using backslash escaping inside quoted fields) when quoted string parsing is enabled with `enableQuotedStringParsing('"')`.
  2. Configure the format with `setFieldDelimiter("|")`, set appropriate field types (e.g., `String.class` or `StringValue.class`), and enable quoted string parsing.
  3. Parse the record and verify that the field values are extracted correctly — the first quoted field value should be `ab"c` (i.e., the escaped quote `\"` resolves to a literal quote character `"`), and the second should be `def`.
  4. Verify that field delimiters (`|`) inside a quoted string are NOT treated as column separators (e.g., `"a|b"` should parse as a single field with value `a|b`).
  
- WHEN writing such tests, the TG MUST also test edge cases:
  - Unclosed quoted strings (line should fail or be handled leniently depending on `setLenient(true/false)`)
  - Quoted fields at the start, middle, and end of a record
  - Escape sequences that are not quotes (e.g., `\\n`, `\\t`) — verify they pass through literally
  - Multiple quoted fields in a single record

- **Common pitfalls to avoid:**
  - Testing only unquoted CSV parsing and assuming quoted parsing works the same way — they have different code paths.
  - Testing only with plain quoted strings `"abc"` without escape characters inside them.
  - Forgetting to call `enableQuotedStringParsing(char)` before parsing — without it, quotes are treated as literal characters.
  - Using `String.class` as the field type (which maps to `StringParser`) vs `StringValue.class` (which maps to `StringValueParser`) — both should be tested as they have separate parser implementations.

- **Example (correct):**
```java
@Test
public void testReadWithQuotedStringsAndEscapedQuotes() throws IOException {
    try {
        String fileContent = "\"ab\\\"c\"|\"def\"";
        FileInputSplit split = createTempFile(fileContent);
        Configuration params = new Configuration();

        format.setFieldDelimiter("|");
        format.setFieldTypesGeneric(String.class, String.class);
        format.enableQuotedStringParsing('"');

        format.configure(params);
        format.open(split);

        // Use String[] as reuse array
        String[] values = format.nextRecord(new String[2]);
        assertNotNull(values);
        assertEquals("ab\"c", values[0]);  // escaped quote resolved
        assertEquals("def", values[1]);

        assertNull(format.nextRecord(values));
        assertTrue(format.reachedEnd());
    } catch (Exception ex) {
        fail("Test failed due to " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
    }
}
```

- **Example (incorrect — missing escape character test):**
```java
@Test
public void testReadWithQuotedStrings_OnlySimple() throws IOException {
    // BUG: Only tests simple quoted strings without escape characters
    String fileContent = "\"abc\"|\"def\"";
    // This does NOT test the escape-handling code path, so the bug where
    // \" inside a quoted string causes parse failure would go undetected.
    ...
}
```
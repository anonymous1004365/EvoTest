---
name: double-parser-invalid-input-rejection
description: When a numeric parser accepts malformed input like "1." as valid, the
  test must verify that such inputs are correctly rejected with parsing errors. This
  skill teaches how to test parser edge cases where incomplete numeric strings are
  accepted by the default parsing logic.
code_tags:
- VALIDATION
test_pattern: EXCEPTION_TEST
---

# double-parser-invalid-input-rejection

## Instructions

# Double Parser Invalid Input Rejection

## Instructions

- WHEN the TG encounters a numeric parser (e.g., `DoubleParser`, `IntParser`, `FloatParser`) that uses `Double.parseDouble()`, `Float.parseFloat()`, or similar standard library parsing methods — and the code is supposed to reject invalid/malformed numeric strings
- THEN the TG should create a test that:
  1. Constructs an instance of the parser (e.g., `new DoubleParser()`)
  2. Calls the parser's `parseField` or equivalent method with a malformed input string (e.g., `"1."`, `"2."`, `".5"`, `"-3."`)
  3. Verifies that the parser returns a non-zero error state (e.g., `parseError != 0` or `return value indicating failure`)
  4. Tests that malformed inputs throw an appropriate exception or set the error flag, rather than silently accepting them
  5. Specifically tests the boundary case where a number is followed by a decimal point with no trailing digits (e.g., `"1."`) — which `Double.parseDouble("1.")` in Java standard library incorrectly accepts as valid for `1.0`

- Common pitfalls to avoid:
  - **Testing only obviously invalid inputs** like `"abc"` or `""` and missing edge cases like `"1."`, `"2."`, `"-3."`
  - **Assuming that standard library parsing methods (e.g., `Double.parseDouble()`) reject all invalid inputs** — in Java, `Double.parseDouble("1.")` returns `1.0` without throwing an exception
  - **Testing only one malformed input** — use a variety of edge cases: `"1."`, `".5"`, `"-3."`, `"1.0."`, `"1..0"`, `" 1."`, `"1. "`
  - **Not checking the parser's error state** — simply checking that no exception is thrown is not sufficient; verify the parse error flag is set

### Correct Example (Java/JUnit)
```java
@Test
public void testInValidStringInIsolation() {
    // Create parser instance
    DoubleParser parser = new DoubleParser();
    
    // Malformed inputs that should be rejected
    String[] invalidInputs = {"1.", "2.", "-3.", ".5", "1..0", "abc"};
    
    for (String invalidInput : invalidInputs) {
        byte[] bytes = invalidInput.getBytes();
        int numRead = parser.parseField(bytes, 0, bytes.length, new byte[]{(byte) '|'}, 0);
        
        // Verify the parser detected an error
        assertTrue("Parser accepted the invalid value " + invalidInput, parser.getParseError() != 0);
    }
}
```

### Incorrect Example (testing only obviously invalid inputs)
```java
@Test
public void testInValidStringInIsolation() {
    DoubleParser parser = new DoubleParser();
    
    // Only testing clearly non-numeric inputs — misses the "1." edge case
    String[] invalidInputs = {"abc", "", "1.0.0", "NaN"};  // Missing "1.", ".5", etc.
    
    for (String invalidInput : invalidInputs) {
        byte[] bytes = invalidInput.getBytes();
        parser.parseField(bytes, 0, bytes.length, new byte[]{(byte) '|'}, 0);
        assertTrue("Parser accepted the invalid value " + invalidInput, parser.getParseError() != 0);
    }
    // BUG: Does NOT test "1." which Double.parseDouble() incorrectly accepts as valid
}
```
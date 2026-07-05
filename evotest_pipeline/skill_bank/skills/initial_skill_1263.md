---
name: alternative-protocol-decoding-path
description: When a protocol decoder has multiple alternative parsing paths (e.g. different message formats or fallback logic), test each path individually to ensure no path throws an unexpected exception. This skill helps detect bugs where a secondary decoding branch fails due to state assumptions or edge cases.
code_tags: ['ALTERNATIVE_PROTOCOL_DECODING']
test_pattern: PARAMETRIC_TEST
---

# alternative-protocol-decoding-path

## Instructions

# Alternative Protocol Decoding Path Testing

## Instructions

- WHEN the TG encounters a protocol decoder class (e.g., `VisiontekProtocolDecoder`) that contains multiple branching logic paths for decoding different message formats — such as if-else chains, switch statements, or try-catch blocks that attempt alternative parsing — THEN the TG MUST write parameterized tests that exercise each distinct decoding path with appropriate input data.

- For each alternative decoding path, the TG MUST:
  1. Identify the specific condition that selects that path (e.g., message length, frame header bytes, String prefix/suffix, checksum presence).
  2. Construct a valid test input (byte array or String message) that triggers that exact condition.
  3. Verify that calling the decode method on that input does NOT throw an unexpected RuntimeException or IndexOutOfBoundsException.
  4. Assert that the decoded result contains meaningful values (e.g., position data, device ID) that match the expected protocol format for that path.

- Common pitfalls to avoid:
  - ❌ Testing only the "happy path" (first branch) and assuming other branches work identically.
  - ❌ Using malformed or random input that could fail for reasons unrelated to the branch logic.
  - ❌ Not verifying that the output structure differs across branches when each branch extracts different fields.
  - ❌ Forgetting to test edge cases like empty message bodies, minimum-length frames, or boundary index values (e.g., substring ranges that could go out of bounds).
  - ❌ Using a single test method that covers all branches — use parameterized tests with named test cases for clarity.

- Example of a correct approach:
```java
// Parametric test — each input exercises a different decoding branch
@ParameterizedTest
@CsvSource({
    "'+RESP:GT...',  true",   // branch 1: standard response
    "'+RESP:AL...',  true",   // branch 2: alarm message
    "'+RESP:ID...',  true",   // branch 3: identification
    "'+RESP:...',    true"    // generic fallback
})
void testDecodingBranches(String rawMessage, boolean expectedSuccess) {
    assertDoesNotThrow(() -> {
        VisiontekProtocolDecoder decoder = new VisiontekProtocolDecoder();
        // decode returns a position object
        Position position = decoder.decode(rawMessage.getBytes(StandardCharsets.US_ASCII));
        assertNotNull(position);
    });
}
```

- Example of a WRONG approach (only tests one branch):
```java
@Test
void testDecode() {
    VisiontekProtocolDecoder decoder = new VisiontekProtocolDecoder();
    // Only tests the first/standard branch
    Position position = decoder.decode("+RESP:GT...".getBytes());
    assertNotNull(position);
    // The AL and ID branches are never tested!
}
```
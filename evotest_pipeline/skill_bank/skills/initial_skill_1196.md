---
name: alternative-protocol-decoder-fallback-testing
description: ''
code_tags:
- ALTERNATIVE_PROTOCOL_DECODING
test_pattern: PARAMETRIC_TEST
---

# alternative-protocol-decoder-fallback-testing

## Instructions

# Alternative Protocol Decoder Fallback Testing

## Instructions

- WHEN the TG encounters a protocol decoder that branches on message type (e.g., an `if` / `switch` on a header byte, a message ID, or a device identifier) or has an alternative decoding path for different frame formats,
- THEN the TG MUST write **parametric tests** that feed at least one representative input per branch, verifying that each branch produces the expected decoded output without throwing an exception.
  - Identify each branch by inspecting the decoder's `decode()` method (or equivalent). Look for conditions such as `if (type == ...)`, `switch (msgId)`, or `if (alternativeFormat)`.
  - For each branch, construct a valid byte buffer (or string input) that will trigger that branch, then assert that decoding succeeds (no exception) and that the resulting object contains the expected fields.
  - **Concrete example**: if the decoder handles two message types – standard position reports (type `0x12`) and alarm messages (type `0x13`) – write parametric tests like:
    ```java
    @ParameterizedTest
    @MethodSource("provideMessages")
    void testDecode(String input, boolean expectedValid) {
        MeiligaoProtocolDecoder decoder = new MeiligaoProtocolDecoder(null);
        ByteBuf buf = Unpooled.wrappedBuffer(ByteBufUtil.decodeHexDump(input));
        Object result = decoder.decode(null, null, buf);
        assertNotNull(result);
    }
    static Stream<Arguments> provideMessages() {
        return Stream.of(
            // Standard position report
            Arguments.of("68641200...", true),
            // Alarm message (alternative path)
            Arguments.of("68641300...", true)
        );
    }
    ```
  - **Common pitfall**: Testing only the "happy path" (the most common message type) and missing the alternative decoding branch. This leaves the alternative path untested and any regression there undetected.
  - **Another pitfall**: Testing each branch with the exact same input structure. Alternative branches often expect different field layouts (e.g., different number of bytes, different checksum positions). Verify that each input is structurally valid for **its own branch**.
  - **What to expect**: On the buggy version, at least one branch will either throw an exception (e.g., `IndexOutOfBoundsException`, `IllegalArgumentException`) or produce an incorrect/null result. The fixed version resolves that branch's logic.
  - **Mistake to avoid**: Relying on a single integration test that feeds a mixed or random stream. Parametric tests with explicit, hand-crafted inputs for each branch give far better diagnostic coverage.
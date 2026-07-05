---
name: protocol-decoder-frame-attribute-parsing
description: When writing protocol decoder tests that parse GPS device frames with
  key=value attributes, test that attribute parsing does not throw NullPointerException
  on missing or malformed values. Apply this skill when the decoder processes semicolon-separated
  fields containing equals-delimited key-value pairs.
code_tags:
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# protocol-decoder-frame-attribute-parsing

## Instructions

# Protocol Decoder Frame Attribute Parsing

## Instructions

- WHEN the TG encounters a protocol decoder that splits frame fields (e.g., using `split(";")`) and then splits those fields again on `"="` to extract key-value attribute pairs
- THEN the TG should write a test that sends a frame ending with a key-value attribute where the value is **empty** (e.g., `"attributeKey="` or just a trailing semicolon with no value), and verify that:
  1. The decoder does **NOT** throw a `NullPointerException` or `ArrayIndexOutOfBoundsException` when `"="` is present but the value part is empty string
  2. The resulting decoded position object correctly handles the empty/missing value (returns a sensible default, skips the attribute, etc.)
- Include tests for the following scenarios:
  - Frame with a key-value attribute where the value is missing after `=` (e.g., `"#D#vs=1.4;cs=0;time=;vm=;s5=70"` — `time=` and `vm=` have no value)
  - Frame with attributes that only have a key with no `=` at all (e.g., an attribute field where the field does not contain `=` — but checking with the specific protocol's delimiter rules)
- **Common pitfall to avoid**: Only testing valid, well-formed frames with all attributes populated. This misses cases where the device sends frames with incomplete trailing data or missing attribute values.
- **Common pitfall to avoid**: Assuming that `split("=")` on a field like `"time="` will produce an array of length 1 (it produces `["time", ""]` with length 2), or accessing index 1 without checking the array length.
- **Common pitfall to avoid**: Not testing empty or null values that could cause `NullPointerException` when calling `.trim()`, `.isEmpty()`, or similar methods on a null substring.

### Correct example (pseudocode):
```java
// Test that a frame with an empty attribute value does NOT throw NPE
String frameWithEmptyAttribute = "#D#vs=1.4;cs=0;time=;vm=;s5=70";
assertDoesNotThrow(() -> decoder.decode(null, null, frameWithEmptyAttribute));
Position position = decoder.decode(null, null, frameWithEmptyAttribute);
assertNotNull(position);
```

### Incorrect example (pseudocode):
```java
// BUG: Only tests well-formed frames with all values present
String validFrame = "#D#vs=1.4;cs=0;time=12345;vm=123;vm1=456";
Position position = decoder.decode(null, null, validFrame);
// Missing: test frames with empty attribute values like "time=" or "vm="
```
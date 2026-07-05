---
name: protocol-decoder-polymorphic-type-dispatch
description: When a protocol decoder dispatches based on polymorphic types (e.g.,
  String vs CtTypeReference from a toString call), the decoder may silently handle
  only one type and ignore the other, leading to silent failures. This skill teaches
  the TG to test all input types that the polymorphic dispatch can produce.
code_tags:
- VALIDATION
- TYPE_CONVERSION
- STATE_MUTATION
test_pattern: PARAMETRIC_TEST
---

# protocol-decoder-polymorphic-type-dispatch

## Instructions

# Protocol Decoder Polymorphic Type Dispatch

## Instructions

- WHEN the TG encounters a protocol decoder that receives a parameter of a general type (e.g., `Object`, `String`, `Serializable`) and dispatches behavior based on its actual runtime type via `instanceof` checks, type casts, or `toString()` results
- THEN the TG should:
  1. Identify all **concrete runtime types** that the parameter can actually take (e.g., String, CtTypeReference, Integer, etc.) based on the calling context and any type conversion/formatting logic
  2. Write **separate test cases** that exercise the decoder with **each concrete type** as input
  3. For each test case, verify that a **valid decoded result** (position, object, etc.) is produced — not just that no exception is thrown
  4. Expect the buggy version to **silently skip processing** (return early, return null, or produce an empty/incomplete result) for types that are not explicitly handled

- Common pitfalls to avoid:
  - ❌ Testing only with `String` type inputs, assuming that covers all cases
  - ❌ Only verifying absence of exceptions rather than verifying complete/correct decoded output
  - ❌ Assuming that if one type works, all types from the same source will work

### Correct Example (finding the bug)

```java
@Test
public void testDecodePolymorphicTypes() {
    Gt30ProtocolDecoder decoder = new Gt30ProtocolDecoder(null);
    
    // Test with String type parameter
    Position position1 = decoder.decode(null, null, "someStringData");
    assertNotNull("Position should decode for String input", position1);
    
    // Test with CtTypeReference or other non-String type parameter
    // In this bug, a CtTypeReference (from toString() of CtElement) was silently ignored
    Position position2 = decoder.decode(null, null, new CtTypeReference<String>() {});
    assertNotNull("Position should decode for CtTypeReference input", position2);
}
```

### Incorrect Example (missing the bug)

```java
@Test
public void testDecode() {
    Gt30ProtocolDecoder decoder = new Gt30ProtocolDecoder(null);
    // Only testing String inputs — misses the CtTypeReference case
    Position position = decoder.decode(null, null, "1234567890");
    assertNotNull(position);
    // The CtTypeReference input would silently fail without this test
}
```
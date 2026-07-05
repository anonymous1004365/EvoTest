---
name: resource-mapper-encode-roundtrip
description: When testing resource reference mappers, verify that the encoded path
  can be cleanly decoded back (round-trip), ensuring encode/decode symmetry. This
  catches bugs where encode cleans/transforms the path in ways decode doesn't reverse.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- STATE_MUTATION
- RESOURCE_MAPPER_ENCODE_CHECK
test_pattern: STATE_TEST
---

# resource-mapper-encode-roundtrip

## Instructions

# Resource Mapper Encode Round-Trip Testing

## Instructions

- WHEN the Test Generator (TG) encounters a resource reference mapper (e.g., `BasicResourceReferenceMapper`, `ResourceReferenceMapper`) that has `encode()` and `decode()` methods, or a `cleanPath()` method used during encoding
- THEN the TG should write a state test that verifies the **round-trip** property: encoding a request and then decoding the result should be equivalent to the original, or at minimum the encoded URL should be decodable without exceptions
- WHEN the mapper's `encode()` method calls utility methods like `cleanPath()` that add/remove/modify path segments (e.g., stripping leading `./`, normalizing slashes, removing file extensions)
- THEN verify that after encoding, any `decode()` or URL parsing logic can successfully handle the cleaned path
- **Concrete example from this bug**: `BasicResourceReferenceMapper` encodes resource references by calling `cleanPath()` on the backing resource path. If `cleanPath()` transforms the path in ways that cause `decode()` to fail (e.g., by stripping `./` prefixes that the decode logic expects), then resource URL mapping breaks for certain resource types. Write a test that:
  1. Creates a mock or real `Request` object with a resource key/path that exercises the path-cleaning logic
  2. Calls the mapper's encode method to produce a `Url`
  3. Calls the mapper's decode/compatibility method on that `Url`
  4. Asserts that no exception is thrown and that the decoded result is not null
  5. Optionally asserts the decoded resource reference matches the original
- **Common pitfalls**: 
  - Testing only that encode works (happy path) without also testing that the encoded output can be decoded
  - Testing only a single type of resource reference (e.g., only `ResourceReference` without `IResource` or package resources)
  - Using a `Request` object that bypasses the path-cleaning logic (e.g., a path without `./` or leading slashes)
  - Forgetting that decode may throw an exception (e.g., `NullPointerException`) on buggy code even though encode ran fine

- **Incorrect test** (surface-level, does not catch the bug):
```java
@Test
public void testEncode() {
    ResourceReference resourceRef = ...;
    Url encoded = mapper.encode(request, resourceRef);
    assertNotNull(encoded);
    assertEquals("expected/path", encoded.toString());
}
```

- **Correct test** (catches the round-trip bug):
```java
@Test
public void testEncodeDecodeRoundTrip() {
    ResourceReference resourceRef = ...;
    Url encoded = mapper.encode(request, resourceRef);
    assertNotNull("Encoding should produce a URL", encoded);
    
    // Decode the encoded URL back - this is where the bug manifests
    ImmutableList<ResourceReferenceInfo> decoded = mapper.decode(
        RequestBuilder.parseUrl(encoded.toString()));
    assertNotNull("Decode should not return null", decoded);
    assertFalse("Decode should find the resource", decoded.isEmpty());
    assertEquals(resourceRef.getKey(), decoded.get(0).getResourceReference().getKey());
}
```
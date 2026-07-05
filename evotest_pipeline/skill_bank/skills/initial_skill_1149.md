---
name: protocol-decoder-null-position-handling
description: When decoding GPS protocol data, position fields (latitude, longitude,
  altitude, speed, course) may be null or zero. Tests should verify decoder handles
  null/zero/missing position data gracefully, producing a valid position object without
  throwing NullPointerException.
code_tags:
- NULL_CHECK
- VALIDATION
- BOUNDARY_CHECK
- ARGUMENT_VALIDATION
test_pattern: EXCEPTION_TEST
---

# protocol-decoder-null-position-handling

## Instructions

# Protocol Decoder Null Position Handling

## Instructions

- WHEN the TG encounters a GPS protocol decoder that passes individual position fields (latitude, longitude, altitude, speed, course, time) to a Position object setter method  
- THEN it should test with inputs where these fields are null, zero, or absent in the raw protocol message
- The test must verify that:
  1. No NullPointerException is thrown when constructing or populating the Position object
  2. The returned Position object is not null
  3. The Position object has valid default/sentinel values for missing fields (e.g., longitude=0.0, latitude=0.0, altitude=0.0)
- Include a test case where ALL position data fields from the raw message are empty/missing/null, expecting a valid Position object (not null) to still be returned without any exception
- Common pitfalls:
  - Testing only with complete, well-formed protocol messages that contain all position fields
  - Assuming the decoder will skip position creation entirely when data is missing (which can cause NullPointerException downstream)
  - Not testing the scenario where individual numeric fields parse to null (e.g., when `Double.parseDouble()` is never called because the field is absent)
- Correct example:
  ```java
  @Test
  public void testDecodeWithNullPosition() throws Exception {
      KenjiProtocolDecoder decoder = new KenjiProtocolDecoder();
      // Craft a protocol message missing position fields (latitude, longitude, etc.)
      String msg = "...";  // minimal message with device ID but no position data
      Object result = decoder.decode(null, null, msg);
      assertNotNull("Decoder should return a non-null position even with null position data", result);
      assertTrue(result instanceof Position);
      // Verify position fields use defaults
      Position position = (Position) result;
      assertEquals(0.0, position.getLatitude(), 0.001);
      assertEquals(0.0, position.getLongitude(), 0.001);
  }
  ```
- Incorrect example:
  ```java
  @Test
  public void testDecodeWithFullData() throws Exception {
      KenjiProtocolDecoder decoder = new KenjiProtocolDecoder();
      // Only testing with complete data — misses the null position bug
      String msg = "...lat=12.34,lon=56.78...";  // full data only
      Object result = decoder.decode(null, null, msg);
      assertNotNull(result);
  }
  ```
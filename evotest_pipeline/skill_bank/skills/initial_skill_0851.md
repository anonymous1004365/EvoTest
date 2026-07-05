---
name: gpx-temperature-testing
description: When testing GPX extensions that handle temperature/atmospheric data
  with different units (celsius vs fahrenheit), use both String and CtTypeReference
  parameter types to verify type-safe attribute handling. The TG should test writing
  temperature data and verify it round-trips correctly without data corruption.
code_tags:
- NULL_CHECK
- VALIDATION
- BOUNDARY_CHECK
test_pattern: PARAMETRIC_TEST
---

# gpx-temperature-testing

## Instructions

# GPX Temperature Extension Testing

## Instructions

- WHEN testing GPX 1.1 extensions that involve temperature/atmospheric data attributes (e.g., `temperature`, `Temperature`, `Double` type temperature values)
- THEN the TG should write a parametric test that:
  1. Creates a route with temperature extensions using **both** `String` type parameters for attribute name lookup and `CtTypeReference` type parameters for type-safe element creation
  2. Sets a temperature value (e.g., `10.0` degrees Celsius) on the extension
  3. Writes the route to a GPX 1.1 format
  4. Reads back the GPX data and verifies the temperature value round-trips correctly (e.g., assert that `route.getTemperature()` equals `10.0`)
  5. Expects the buggy version to **fail** with either:
     - A `NullPointerException` during write
     - A corrupted/zero temperature value on read-back (e.g., `0.0` instead of `10.0`)
     - An incorrect attribute value being written

- Common pitfalls:
  - Testing only `String`-based attribute lookups without testing type-safe `CtTypeReference`-based creation paths
  - Forgetting to verify round-trip behavior (write then read back) to catch data corruption
  - Using only integer temperature values instead of floating-point (e.g., `Double`) values
  - Not testing edge cases like negative temperatures, zero, or boundary values (e.g., `-273.15`, `0.0`, `100.0`)

- Example correct pattern:
  ```java
  @Test
  public void testWriteTemperature() {
      // Setup: create route with temperature extension
      Route route = new Route();
      route.setTemperature(10.0);  // Double value in Celsius
      
      // Write to GPX format
      Gpx11Writer writer = new Gpx11Writer();
      String gpxContent = writer.write(route);
      
      // Read back and verify
      Gpx11Reader reader = new Gpx11Reader();
      Route readRoute = reader.read(gpxContent);
      assertEquals(10.0, readRoute.getTemperature(), 0.001);
  }
  ```

- Example incorrect pattern:
  ```java
  @Test
  public void testTemperature() {
      // Only tests String parameter — misses type-safe CtTypeReference bug
      Route route = new Route();
      route.setTemperature(10);
      assertEquals(10, route.getTemperature());
      // Does NOT test write/read round-trip
  }
  ```

- When the developer adds a new temperature value to an extension, the TG should specifically verify that:
  - The attribute is correctly written with the `"°C"` or temperature unit suffix
  - The type-safe extension element path (using `CtTypeReference`) handles the value correctly
  - Both writer and reader pass through the value without precision loss
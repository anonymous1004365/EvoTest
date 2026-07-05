---
name: dashboard-readonly-state-validation
description: When a GUI Dashboard component receives data updates but multiple read
  methods must be called to consume all received values, the TG should verify that
  all expected fields are populated after a single update cycle and that specific
  read methods do not block or skip subsequent reads.
code_tags:
- VALIDATION
test_pattern: STATE_TEST
---

# dashboard-readonly-state-validation

## Instructions

# Dashboard Readonly State Validation

## Instructions

- WHEN the TG encounters a `Dashboard` (or similar GUI component) class that receives a `readonlyInputData` packet containing multiple typed values (e.g., `fuelLevel`, `speed`, `engineTemperature`, `gear`) AND provides separate getter/read methods for each value
- THEN the TG should write a **state test** that:
  1. Calls `updateReadonlyInputData(readonlyInputData)` with a fully populated `ReadonlyInputData` object (all fields set to distinct, non-default values)
  2. THEN calls **every** getter method to verify that **each** getter returns the expected value from the single update
  3. The test must ensure all values from the single `updateReadonlyInputData` call are reflected after calling the getters, regardless of the order in which getters are called
- Concrete values to use: set `fuelLevel` to a value like `50`, `speed` to `100`, `engineTemperature` to `90`, `gear` to `3` on the `ReadonlyInputData` object
- The test should verify these assertions after one single call to `updateReadonlyInputData`:
  - `assertEquals(50, dashboard.getFuelLevel())`
  - `assertEquals(100, dashboard.getSpeed())`
  - `assertEquals(90, dashboard.getEngineTemperature())`
  - `assertEquals(3, dashboard.getGear())`
- **Common pitfall**: Testing only one getter after an update call is insufficient. The bug may be that calling one getter clears or resets internal state, causing a subsequent getter for a *different* field to read a stale/zero value. Always test ALL getters after the single update call.
- **Another pitfall**: Creating a new `ReadonlyInputData` between each getter call. The test must use a single update call, then read through all getters, to catch order-dependent state mutation bugs where reading one property invalidates another.

### Correct Example (what TG should generate)
```java
@Test
public void allRequiredValuesReceivedOnUpdate() {
    ReadonlyInputData inputData = new ReadonlyInputData();
    inputData.setFuelLevel(50);
    inputData.setSpeed(100);
    inputData.setEngineTemperature(90);
    inputData.setGear(3);
    
    dashboard.updateReadonlyInputData(inputData);
    
    assertEquals(50, dashboard.getFuelLevel());
    assertEquals(100, dashboard.getSpeed());
    assertEquals(90, dashboard.getEngineTemperature());
    assertEquals(3, dashboard.getGear());
}
```

### Incorrect Example (misses the bug)
```java
@Test
public void testFuelLevel() {
    ReadonlyInputData inputData = new ReadonlyInputData();
    inputData.setFuelLevel(50);
    dashboard.updateReadonlyInputData(inputData);
    assertEquals(50, dashboard.getFuelLevel());
}
// Separate test for speed - but speed is never set!
@Test
public void testSpeed() {
    ReadonlyInputData inputData = new ReadonlyInputData();
    inputData.setSpeed(100);
    dashboard.updateReadonlyInputData(inputData);
    assertEquals(100, dashboard.getSpeed());
}
// This misses the bug because each getter is tested in isolation
```
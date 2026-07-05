---
name: creator-collector-property-ownership
description: Helps test generators detect bugs when a method incorrectly ignores or
  reuses property ownership state during deserialization, particularly when delegating
  constructors and property-based creators interact with SettableBeanProperty instances.
  Use this skill when a test must verify that each creator property is properly owned
  and not incorrectly shared across creator types.
code_tags:
- VALIDATION
- STATE_MUTATION
- EXCEPTION_HANDLING
test_pattern: STATE_TEST
---

# creator-collector-property-ownership

## Instructions

# CreatorCollector Property Ownership Verification

## Instructions

WHEN the TG encounters a `CreatorCollector` class that accumulates `SettableBeanProperty` instances for both delegate constructors AND property-based creators (methods like `addPropertyCreator`, `addDelegatingCreator`, `constructCreatorProperties`), THEN the TG should write a test that:

1. **Constructs a CreatorCollector** with a valid `DeserializationConfig` and a target type (e.g., `SimplePojo` or equivalent POJO class).

2. **Registers both a delegating creator and a property-based creator** using the collector's public methods (e.g., `addDelegatingCreator(...)` and `addPropertyCreator(...)`), simulating the scenario where the collector processes creator properties.

3. **Extracts the resulting property list** from methods like `constructCreatorProperties(...)` or `properties()` and verifies that **each property is a distinct object** (i.e., not the same reference reused across creators). Specifically:
   - Assert that properties assigned to the delegating creator are NOT the same object instances as properties assigned to the property-based creator.
   - Assert that modifying one property does not affect the other.

4. **Verifies that no exception is thrown** when processing properties with mismatched or shared ownership. The bug likely manifests as an `IllegalArgumentException` (or similar) when a property is already owned by one creator but reused for another.

5. **Expected failure on buggy version**: The test should fail with an exception (e.g., `IllegalArgumentException: 'property' is already owned by the CreatorContainer`) or produce duplicate/shared property references.

**Common pitfalls to avoid:**
- Testing only a single creator type (e.g., only property-based, or only delegating) — the bug is triggered by the **interaction** between multiple creator types.
- Using mocks for `SettableBeanProperty` — use **real instances** (or simple subclasses) to ensure the internal ownership check (`isOwnedBy(...)`) fires correctly.
- Forgetting to call the method that finalizes/constructs properties (e.g., `constructCreatorProperties(...)`) — the bug may not surface until properties are collected and returned.
- Assuming properties are independent by default — the bug is that the same property instance is incorrectly shared.

**Example (correct):**

```java
// Create a CreatorCollector with a real or mock config/type
DeserializationConfig config = new ObjectMapper().getDeserializationConfig();
JavaType type = config.constructType(SimplePojo.class);
CreatorCollector collector = new CreatorCollector(config, type);

// Create two distinct properties
SettableBeanProperty propA = new SimplePojoProperty("a", null, null);
SettableBeanProperty propB = new SimplePojoProperty("b", null, null);

// Register both a delegating creator and a property creator using these properties
collector.addDelegatingCreator(null, false, null, propA);  // propA owned by delegating
collector.addPropertyCreator(null, null, false, propB);     // propB owned by property creator

// This call may incorrectly share ownership or throw
List<SettableBeanProperty> props = collector.constructCreatorProperties(…);

// Verify each property is distinct
assertNotNull(props);
assertTrue(props.contains(propA));
assertTrue(props.contains(propB));
```

**Example (incorrect):**

```java
// BAD: Test only one creator type — does not trigger the bug
CreatorCollector collector = new CreatorCollector(config, type);
SettableBeanProperty prop = new SimplePojoProperty("a", null, null);
collector.addPropertyCreator(null, null, false, prop);
List<SettableBeanProperty> props = collector.constructCreatorProperties(…);
assertEquals(1, props.size());

// BAD: Using mocks for SettableBeanProperty — bypasses isOwnedBy check
SettableBeanProperty mockProp = mock(SettableBeanProperty.class);
when(mockProp.isOwnedBy(any())).thenReturn(false);
// ... won't trigger the real bug
```
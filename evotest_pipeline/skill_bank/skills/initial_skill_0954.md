---
name: type-converter-registry-miss-cache-staleness
description: WHEN a TypeConverterRegistry caches "misses" (failed conversions) in
  a misses cache, THEN tests should verify that registering a new type converter later
  overrides the cached miss and allows the conversion to succeed. This prevents stale
  miss entries from permanently blocking valid conversions.
code_tags:
- TYPE_CONVERSION
- STATE_MUTATION
- CACHING_STALE_STATE
test_pattern: STATE_TEST
---

# type-converter-registry-miss-cache-staleness

## Instructions

# Type Converter Registry Miss Cache Staleness

## Instructions

- WHEN the TG encounters a `TypeConverterRegistry` (e.g., `BaseTypeConverterRegistry`, `DefaultTypeConverter`) that maintains a `misses` cache (e.g., `LRUSoftCache<TypeMapping, TypeMapping> misses`) used to short-circuit previously failed type conversions by checking `misses.containsKey(key)` before attempting conversion,
- THEN the TG should write a **state mutation test** that:
  1. Performs an initial type conversion that will fail (returns `null`) because no converter exists for the given `(toType, fromType)` pair.
  2. Verifies the conversion returns `null` on the first attempt (or returns `Void.TYPE`/`null`).
  3. Registers a new type converter for that exact `(toType, fromType)` pair using `registry.addTypeConverter(toType, fromType, converter)`.
  4. Performs the **same conversion again** and verifies it now **succeeds** (returns a non-null, correctly converted value).
  5. Specifically checks that the conversion result is now non-null and contains the expected transformed data.

- The test must use a **custom type** (e.g., a POJO like `MyOrder`) and a **custom `TypeConverter`** implementation (e.g., extending `TypeConverterSupport`), not built-in types that already have converters registered.

- **Common pitfalls to avoid**:
  - ❌ Testing only with built-in types (e.g., `String` → `Integer`) that already have converters — these won't exercise the misses cache.
  - ❌ Skipping the initial failed conversion step — without it, the miss is never cached and the bug cannot be reproduced.
  - ❌ Assuming the misses cache is checked only in one location — the `misses.containsKey(key)` check happens inside `doConvertTo()` before looking up `typeMappings`.
  - ❌ Assuming that registering a converter while the registry is already started will automatically invalidate the misses cache — the bug is that registering after a miss does **not** clear the relevant miss entry, so the cached miss still blocks the conversion.
  - ❌ Not verifying the converted value's correctness — checking only non-null is insufficient; the test should assert the expected field value (e.g., `assertEquals(123, order.getId())`).

### Correct example (Java with Camel API)

```java
public class MissesThenAddTest extends TestCase {
    public void testMissThenAddTypeConverter() {
        DefaultCamelContext context = new DefaultCamelContext();
        
        // 1. Attempt conversion that will fail (no converter yet)
        MyOrder order = context.getTypeConverter().convertTo(MyOrder.class, "123");
        assertNull("First conversion should fail (null)", order);
        
        // 2. Register the missing converter
        context.getTypeConverterRegistry().addTypeConverter(
            MyOrder.class, String.class, new MyOrderTypeConverter());
        
        // 3. Try again — should now succeed
        order = context.getTypeConverter().convertTo(MyOrder.class, "123");
        assertNotNull("Second conversion should succeed", order);
        assertEquals("Converted value should be correct", 123, order.getId());
    }
    
    private static class MyOrder {
        private int id;
        public int getId() { return id; }
        public void setId(int id) { this.id = id; }
    }
    
    private static class MyOrderTypeConverter extends TypeConverterSupport {
        @SuppressWarnings("unchecked")
        public <T> T convertTo(Class<T> type, Exchange exchange, Object value) {
            MyOrder order = new MyOrder();
            order.setId(Integer.parseInt(value.toString()));
            return (T) order;
        }
    }
}
```

### Incorrect example (missing key elements)

```java
// BAD: Only tests built-in types that already have converters
public void testBuiltInConversion() {
    DefaultCamelContext context = new DefaultCamelContext();
    Integer result = context.getTypeConverter().convertTo(Integer.class, "123");
    assertNotNull(result);  // This works without any registration, doesn't test misses cache
}

// BAD: Skips the first failed conversion (misses cache never populated)
public void testAddThenConvert() {
    DefaultCamelContext context = new DefaultCamelContext();
    context.getTypeConverterRegistry().addTypeConverter(
        MyOrder.class, String.class, new MyOrderTypeConverter());
    MyOrder order = context.getTypeConverter().convertTo(MyOrder.class, "123");
    assertNotNull(order);  // Misses cache was never populated — bug not triggered
}
```
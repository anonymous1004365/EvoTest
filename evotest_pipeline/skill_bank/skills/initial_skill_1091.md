---
name: property-resolver-type-mismatch-on-field-set
description: When a PropertyResolver.setValue() call targets a field whose getter
  returns a different type than the field itself, the resolution may use the wrong
  type and fail with a ConversionException. Apply this skill to test that field set
  operations handle type mismatches between the getter return type and the actual
  field type.
code_tags:
- NULL_CHECK
- VALIDATION
- EXCEPTION_HANDLING
test_pattern: EXCEPTION_TEST
---

# property-resolver-type-mismatch-on-field-set

## Instructions

# PropertyResolver Type Mismatch on Field Set

## Instructions

WHEN the TG encounters code that uses `PropertyResolver.setValue()` (or `PropertyResolver.getValue()`) with a target object where:
- A public getter method exists for a property (e.g. `String getXyz()`)
- The backing field has a **different, incompatible type** (e.g. `Integer xyz`)
- The test sets the property value using `PropertyResolver.setValue("xyz", object, value)` where the value type matches the **getter** return type (e.g. `String`) but is incompatible with the actual **field** type (e.g. `Integer`)

THEN the TG should:
1. Create a test class with an inner static class (e.g. `DirectFieldSetWithDifferentTypeThanGetter`) that contains:
   - A field of type T1 (e.g. `Integer`) named `xyz`
   - A public getter method returning type T2 that is different from T1 (e.g. `public String getXyz()` returning `null` or `String.valueOf(field)`)
   - No public setter for that field
2. Write a test method that:
   - Instantiates the inner class
   - Calls `PropertyResolver.setValue("propertyName", instance, value)` where `value` is of type T2 (the getter's return type)
   - Asserts that the field was **not set** (still null, or still its default value) — i.e. assert that `getXyz()` still returns null
   - OR expects a `ConversionException` if the type mismatch causes a conversion failure
3. Verify the behavior against the buggy version: the buggy `PropertyResolver.setValue()` may incorrectly attempt to use reflection to set the field directly with the wrong type, causing either a silent failure (field not set, getter still returns null) or a `ConversionException`

Common pitfalls to avoid:
- Do NOT assume that `PropertyResolver.setValue()` will always throw an exception on type mismatch — it may silently fail to set the field
- Do NOT only test with matching getter/field types — this bug specifically manifests when the getter return type differs from the field type
- Do NOT use a setter for the test property — the bug involves direct field access bypassing setters
- Do NOT forget to test that the getter still returns null (the value was not set) after the `setValue` call

Correct example:
```java
private static class DirectFieldSetWithDifferentTypeThanGetter
{
    private final Integer xyz;

    public DirectFieldSetWithDifferentTypeThanGetter()
    {
        xyz = Integer.valueOf(1);
    }

    public String getXyz()
    {
        return String.valueOf(xyz);
    }
}

@Test
public void testDirectFieldSetWithDifferentTypeThanGetter()
{
    DirectFieldSetWithDifferentTypeThanGetter obj = new DirectFieldSetWithDifferentTypeThanGetter();
    PropertyResolver.setValue("xyz", obj, "123", null);
    assertNull(obj.getXyz());
}
```

Incorrect example (would NOT trigger the bug):
```java
private static class SameTypes
{
    private String xyz;
    public String getXyz() { return xyz; }
    public void setXyz(String xyz) { this.xyz = xyz; }
}

@Test
public void testSameTypes()
{
    SameTypes obj = new SameTypes();
    PropertyResolver.setValue("xyz", obj, "123", null);
    assertEquals("123", obj.getXyz()); // No bug here, works fine
}
```
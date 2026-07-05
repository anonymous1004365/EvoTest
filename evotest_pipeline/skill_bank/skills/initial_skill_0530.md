---
name: default-converter-type-instance-check
description: When testing general-purpose fallback converters (like DefaultConverter
  in ConverterLocator), ensure they handle interface types such as Serializable and
  Object by checking if the input value is already an instance of the target type.
  The TG should verify that String values can be converted to interface types like
  java.io.Serializable or java.lang.Object.
code_tags:
- CACHING_AND_CONVERTER_REGISTRY
- NULL_CHECK
- TYPE_CONVERSION
test_pattern: EXCEPTION_TEST
---

# default-converter-type-instance-check

## Instructions

# Default Converter Type Instance Check

## Instructions

- WHEN the TG encounters a `ConverterLocator` or similar converter registry that has a `DefaultConverter` inner class responsible for converting values to types that have no explicit registered converter
- THEN the TG should test that `ConverterLocator.getConverter(Serializable.class).convertToObject("test", Locale.US)` returns `"test"` (the original string), because `String` is an instance of `Serializable`
- ALSO test that `ConverterLocator.getConverter(Object.class).convertToObject("test", Locale.US)` returns `"test"`, because `String` is an instance of `Object`
- WHEN the target type is an interface or supertype of `String` (e.g., `java.io.Serializable`, `java.lang.Object`, `java.lang.CharSequence`, `java.lang.Comparable`), the `DefaultConverter` should check `theType.isInstance(value)` after `Objects.convertValue` returns null
- Common pitfall: Testing only primitive or well-known types (Integer, Double, Boolean) and missing interface types that have no dedicated converter but where the input value is already compatible
- Example: `locator.getConverter(Serializable.class).convertToObject("test", Locale.US)` should not throw `ConversionException` with message "Could not convert value: test to type: java.io.Serializable. Could not find compatible converter."
- Correct: Test with `locator.getConverter(Serializable.class).convertToObject("test", Locale.US)` and expect `"test"` to be returned successfully
- Incorrect: Assuming that any type without a registered converter will always throw a ConversionException — the code has a fallback `theType.isInstance(value)` check that should succeed for interface/supertype matches
---
name: aggregation-type-generic-field-validation
description: Tests aggregations (sum/min/max) on generic types must validate that
  the field type is actually summable (e.g., Integer, Long, Float, Double, Byte, Short)
  and not a generic type parameter or unsupported type like Tuple, or an `InvalidTypesException`/`InvalidProgramException`
  will be thrown at runtime.
code_tags:
- TYPE_CONVERSION
- VALIDATION
- STATE_MUTATION
test_pattern: EXCEPTION_TEST
---

# aggregation-type-generic-field-validation

## Instructions

# Aggregation Type Generic Field Validation

## Instructions

- WHEN the TG encounters code that uses `SumAggregator`, `MinAggregator`, `MaxAggregator`, or any `AggregationFunction` subclass — specifically when the field to aggregate is accessed by field position (int) or field name (String) and a `TypeInformation` is passed — THEN the TG must test that the field's data type is a concrete numeric type (Integer, Long, Float, Double, Byte, Short, or their primitive equivalents).

- WHEN the aggregation is performed on a class where the aggregated field is declared as a **generic type parameter** (e.g., `T` in `class MyPojo<T> { public T f1; }`) or as `Object` with no concrete numeric type information, THEN the TG must verify that the constructor call throws an `InvalidTypesException` (from org.apache.flink.api.common.functions.InvalidTypesException) at construction time, because the SumFunction cannot determine an add operation for a generic/unknown type.

- WHEN the aggregation field is of type `Tuple` (raw tuple, not Tuple1/Tuple2/etc.), THEN the TG must verify that an `InvalidProgramException` or `InvalidTypesException` is thrown with the message "Usage of class Tuple as a type is not allowed".

- The TG must NOT test only with concrete types like Integer, String, or custom POJOs with concrete fields. The TG MUST also test with a POJO that uses a generic type parameter `T` for the aggregated field, and expect the exception.

- **Common pitfall**: Testing only with concrete fields (e.g., `Integer f1`) and missing the generic type parameter case. The bug occurs because `SumAggregator` / `SumFunction` cannot create a `SumFunction.Add` for a generic type `T`, and it throws an `InvalidTypesException` at construction time with a message like "Usage of class T is not allowed" (the exact message may vary). Always test with both a concrete summable type AND a generic type parameter.

### Correct Example (catches the bug)

```java
@Test
public void testSumWithGenericFieldThrowsException() {
    // MyPojo has a generic field: class MyPojo<T> { public T f1; }
    TypeInformation<MyPojo> typeInfo = TypeExtractor.createTypeInfo(MyPojo.class);
    ExecutionConfig config = new ExecutionConfig();
    assertThrows(InvalidTypesException.class, () -> new SumAggregator<>("f1", typeInfo, config));
}
```

### Incorrect Example (misses the bug)

```java
@Test
public void testSumWithConcreteFieldSucceeds() {
    // Only testing concrete types — this passes even with the bug
    TypeInformation<MyPojo> typeInfo = TypeExtractor.createTypeInfo(MyPojo.class);
    ExecutionConfig config = new ExecutionConfig();
    ReduceFunction<MyPojo> sum = new SumAggregator<>("f1", typeInfo, config);
    // This test would pass on both buggy and fixed versions if MyPojo has concrete Integer f1
}
```
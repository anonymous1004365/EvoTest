---
name: raw-type-function-type-extraction
description: When extracting types from Java generic methods that accept raw (non-parameterized)
  functional interface types, test that the type extractor throws an IllegalArgumentException
  instead of failing with an internal error or returning incorrect results.
code_tags:
- TYPE_CONVERSION
- VALIDATION
- EXCEPTION_HANDLING
test_pattern: EXCEPTION_TEST
---

# raw-type-function-type-extraction

## Instructions

# Raw-Type Function Type Extraction

## Instructions

- WHEN the TG encounters a type extraction method (e.g., `TypeExtractor.getMapReturnTypes(...)`, `TypeExtractor.getUDFReturnType(...)`) that accepts a function object whose generic type parameter uses a raw (non-parameterized) functional interface (e.g., `MapFunction` instead of `MapFunction<String, Integer>`)
- THEN the TG should write a test that:
  1. Creates a raw functional interface instance — e.g., `new MapFunction() { ... }` with no generic type parameters in the declaration
  2. Passes it to the type extraction API with `InputTypeConfigurable` or equivalent configuration calls
  3. Asserts that an `IllegalArgumentException` is thrown (as the type extractor cannot infer the types from raw types)
  4. Uses `@Test(expected = IllegalArgumentException.class)` or `assertThrows(IllegalArgumentException.class, ...)` to verify

- Common pitfalls to avoid:
  - Using only properly parameterized generic types — these will succeed, so the test won't catch the regression
  - Not wrapping the extraction call in a try-catch or expected exception — the bug causes failure during extraction, so the test MUST catch the exception
  - Testing with only one type of raw function — test with raw `MapFunction`, `FlatMapFunction`, or other functional interfaces used in the codebase
  - Forgetting to test the `InputTypeConfigurable.configure(...)` or similar setup that triggers the code path

### Correct Example
```java
@Test(expected = IllegalArgumentException.class)
public void testInputMismatchWithRawFunction() {
    MapFunction<String, String> stringDuplicator = new MapFunction<String, String>() {
        @Override
        public String map(String value) throws Exception {
            return value + value;
        }
    };
    
    // Raw (non-parameterized) function that causes type extraction to fail
    MapFunction rawDuplicator = stringDuplicator;
    
    TypeInformation<?>[] types = TypeExtractor.getMapReturnTypes(rawDuplicator, 
        new TupleTypeInfo(Tuple2.class, BasicTypeInfo.STRING_TYPE_INFO, BasicTypeInfo.STRING_TYPE_INFO),
        new MyInputTypeConfigurable(),
        false);
}
```

### Incorrect Example
```java
// ❌ Only tests parameterized MapFunction — doesn't catch the raw type bug
@Test
public void testMapReturnTypesWithParameterizedFunction() {
    MapFunction<String, String> f = new MapFunction<String, String>() {
        @Override
        public String map(String value) { return value; }
    };
    TypeInformation<?> types = TypeExtractor.getMapReturnTypes(f, ...);
    assertNotNull(types); // This test passes on both buggy and fixed versions
}
```

### When to apply this skill
- Any time you see a type extraction utility that processes generic functional interfaces
- Particularly when the code path involves `InputTypeConfigurable` or similar callback-based configuration that interacts with generic type resolution
- The test should verify that raw types cause a clear `IllegalArgumentException` rather than a cryptic internal error or silently producing incorrect type information
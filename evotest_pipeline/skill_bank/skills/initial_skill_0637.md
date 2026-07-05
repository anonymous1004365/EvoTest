---
name: pojo-type-extraction-from-object
description: When analyzing POJO type extraction code, test that the TypeExtractor
  can correctly infer POJO types from object instances containing null fields. This
  skill applies to type extraction logic where getForObject() must handle null-valued
  POJO fields without throwing NullPointerException.
code_tags:
- NULL_CHECK
- VALIDATION
- TYPE_CONVERSION
test_pattern: EXCEPTION_TEST
---

# pojo-type-extraction-from-object

## Instructions

# POJO Type Extraction from Object with Null Fields

## Instructions

- WHEN the TG encounters code that calls `TypeExtractor.getForObject()` with a POJO object (a class with `public` getter/setter methods and a no-arg constructor, such as a POJO containing String/int/List fields)
- THEN the TG should write a test that:
  1. Creates an instance of the POJO class where multiple fields are set to `null` (e.g., a String field set to `null`, a `List<?>` field set to `null`)
  2. Calls `TypeExtractor.getForObject(pojoInstance)` on that instance
  3. Verifies that the result is a `PojoTypeInfo` by asserting `assertTrue(ti instanceof PojoTypeInfo)`
  4. Verifies that the returned TypeInformation contains the expected field names and types (e.g., `PojoField` entries for each field of the POJO)
- The test must verify that NO `NullPointerException` or `NullPointerException`-related error is thrown when the POJO has null-valued fields. On the buggy version, calling `getForObject()` on a POJO with null fields may throw a `NullPointerException` because the type extractor attempts to call `.getClass()` on a null value returned by a getter.
- Common pitfalls to avoid:
  - Testing only POJOs where all fields are non-null; the bug manifests only when fields are null
  - Testing with null POJO reference instead of a POJO with null fields
  - Forgetting to call the specific method `getForObject()` — other methods like `getForClass()` or `getMapReturnTypes()` may not trigger the same bug path
  - Only testing primitive (int, boolean) fields that cannot be null; the bug triggers on reference-typed fields (String, List, etc.)

### Correct example (what the TG should write):

```java
public static class MyPojo {
    public String name;
    public int age;
    public List<String> items;
    
    public MyPojo() {}
    
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public int getAge() { return age; }
    public void setAge(int age) { this.age = age; }
    public List<String> getItems() { return items; }
    public void setItems(List<String> items) { this.items = items; }
}

@Test
public void testPojoTypeExtractionWithNullFields() {
    MyPojo pojo = new MyPojo();
    pojo.setName(null);      // String field set to null
    pojo.setAge(25);         // primitive field, non-null is fine
    pojo.setItems(null);     // List field set to null
    
    // This must not throw NullPointerException
    TypeInformation<?> ti = TypeExtractor.getForObject(pojo);
    assertTrue("Must be PojoTypeInfo", ti instanceof PojoTypeInfo);
    PojoTypeInfo<?> pti = (PojoTypeInfo<?>) ti;
    assertEquals("name", pti.getPojoFieldAt(0).getField().getName());
    assertEquals("age", pti.getPojoFieldAt(1).getField().getName());
    assertEquals("items", pti.getPojoFieldAt(2).getField().getName());
}
```

### Common mistake (incorrect code that misses the bug):

```java
// BAD: Only tests with non-null fields
MyPojo pojo = new MyPojo();
pojo.setName("Alice");
pojo.setAge(30);
pojo.setItems(Arrays.asList("a", "b"));
TypeInformation<?> ti = TypeExtractor.getForObject(pojo); // This works even in buggy version
// The above test passes even on the buggy version — it doesn't catch the bug!
```

```java
// BAD: Tests with null POJO itself instead of POJO with null fields
TypeInformation<?> ti = TypeExtractor.getForObject(null); // Wrong — completely different error
```

```java
// BAD: Only tests primitive fields that cannot be null
public static class PrimitiveOnlyPojo {
    public int x;
    public int getX() { return x; }
    public void setX(int x) { this.x = x; }
}
PrimitiveOnlyPojo p = new PrimitiveOnlyPojo();
TypeInformation<?> ti = TypeExtractor.getForObject(p); // Works even in buggy version
```
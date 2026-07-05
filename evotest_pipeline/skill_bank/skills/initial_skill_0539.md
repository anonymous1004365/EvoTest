---
name: one-to-many-array-cast-type-conversion
description: WHEN the code casts a PostgreSQL JDBC Array.getArray() result to a specific
  type (e.g., String[]) for one-to-many attributes, THEN the TG should test with non-String
  element types (e.g., Integer[]) since PostgreSQL returns array elements in their
  native SQL type.
code_tags:
- NULL_CHECK
- STATE_MUTATION
- ARRAY_INDEX_ACCESS
- TYPE_CONVERSION
test_pattern: PARAMETRIC_TEST
---

# one-to-many-array-cast-type-conversion

## Instructions

# One-To-Many Array Cast Type Conversion

## Instructions

WHEN the TG encounters code in `PostgreSqlEntityFactory.EntityMapper.mapValueOneToMany(Array, Attribute)` that casts `arrayValue.getArray()` to a type like `String[]` (or `Object[]`), THEN the TG should verify the code works correctly when the JDBC array contains elements of different native types (e.g., `Integer[]` instead of `String[]`).

WHEN the ref entity's ID attribute has a non-String data type (e.g., `INT`, `LONG`), THEN the TG should test with an array of the corresponding Java type (e.g., `new Integer[] { 0, 1 }`) because PostgreSQL returns array elements in their native SQL type, not as strings.

WHEN calling `arrayValue.getArray()` on a JDBC `Array`, THEN the TG should be aware that the returned type depends on the database column type and is NOT always `String[]`. For example, integer arrays return `Integer[]`, not `String[]`.

WHEN the TG tests `mapValueOneToMany` with integer IDs, THEN the TG should verify that the method:
1. Properly handles the cast from the actual array type (e.g., `Integer[]`) instead of assuming `String[]`
2. Correctly converts each element via `convertMrefIdValue(mrefIdRaw.toString(), idAttr)`
3. Produces the correct collection of IDs (e.g., `newArrayList(0, 1)` for integers) when passed to `entityManager.getReferences()`

Common Pitfalls to Avoid:
- Testing only with `String[]` array values. The bug occurs when the array contains non-String elements (e.g., `Integer[]`). Always test with at least one non-String type if the ID attribute supports it.
- Forgetting to verify the exact IDs passed to `entityManager.getReferences()`. The expected collection should contain the actual numeric values (e.g., `newArrayList(0, 1)`), not string representations (`newArrayList("0", "1")`).
- Not setting up the mock for `refIdAttr.getDataType()` to return the appropriate type (e.g., `AttributeType.INT` for integer IDs).

### Correct Example (test that would catch the bug)

```java
@Test
public void createRowMapperOneToManyIntegerIds() throws Exception
{
    Attribute refIdAttr = mock(Attribute.class);
    when(refIdAttr.getDataType()).thenReturn(AttributeType.INT);

    EntityType refEntityMeta = mock(EntityType.class);
    when(refEntityMeta.getIdAttribute()).thenReturn(refIdAttr);

    String oneToManyAttrName = "oneToManyAttr";
    Attribute oneToManyAttr = mock(Attribute.class);
    when(oneToManyAttr.getName()).thenReturn(oneToManyAttrName);
    when(oneToManyAttr.getDataType()).thenReturn(ONE_TO_MANY);
    when(oneToManyAttr.getRefEntity()).thenReturn(refEntityMeta);

    EntityType entityType = mock(EntityType.class);
    when(entityType.getAtomicAttributes()).thenReturn(singleton(oneToManyAttr));
    ResultSet rs = mock(ResultSet.class);
    Array oneToManyArray = mock(Array.class);
    // NOTE: Integer[], not String[] — this is what PostgreSQL returns for integer array columns
    when(oneToManyArray.getArray()).thenReturn(new Integer[] { 0, 1 });
    when(rs.getArray(oneToManyAttrName)).thenReturn(oneToManyArray);
    int rowNum = 0;

    Entity entity = mock(Entity.class);
    when(entityManager.createFetch(entityType, null)).thenReturn(entity);
    Entity refEntity1 = mock(Entity.class);
    Entity refEntity0 = mock(Entity.class);
    // NOTE: IDs are integers (0, 1), not strings ("id0", "id1")
    when(entityManager.getReferences(refEntityMeta, newArrayList(0, 1))).thenReturn(
            newArrayList(refEntity0, refEntity1));
    assertEquals(postgreSqlEntityFactory.createRowMapper(entityType, null).mapRow(rs, rowNum), entity);
    verify(entity).set(oneToManyAttrName, newArrayList(refEntity0, refEntity1));
}
```

### Incorrect Example (what would miss the bug)

```java
// This test would pass even on the buggy version because it only tests with String[]
@Test
public void createRowMapperOneToMany() throws Exception
{
    // ... same setup ...
    // BUG: only tests with String[] — doesn't expose the ClassCastException for Integer[]
    when(oneToManyArray.getArray()).thenReturn(new String[] { "id0", "id1" });
    // ...
    when(entityManager.getReferences(refEntityMeta, newArrayList("id0", "id1"))).thenReturn(...);
    // ...
}
```
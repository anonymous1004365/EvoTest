---
name: level-mapping-completeness-check
description: When testing bidirectional level mappings (e.g., Log4j↔JUL), verify ALL
  Log4j levels are mapped to a non-null JUL level. The DefaultLevelConverter uses
  IdentityHashMap, so IdentityHashMap.get() returns null for unmapped keys — FATAL
  was mapped in the constructor but the test expects SEVERE for FATAL — ensure test
  covers every Log4j Level enum value.
code_tags:
- ARRAY_INDEX_ACCESS
- BOUNDARY_CHECK
- PRIME_SIEVE_GENERATION
test_pattern: PARAMETRIC_TEST
---

# level-mapping-completeness-check

## Instructions

# Level Mapping Completeness Check

## Instructions

- WHEN the TG encounters a level converter that maps between two level systems (e.g., Log4j `Level` → `java.util.logging.Level`) using a `Map` lookup
- THEN the TG should write a parametric test that iterates over ALL enum values/constants of the source level system and verifies that each one maps to a non-null target level
- For the Log4j→JUL case: test all 8 Log4j levels (`Level.OFF`, `Level.FATAL`, `Level.ERROR`, `Level.WARN`, `Level.INFO`, `Level.DEBUG`, `Level.TRACE`, `Level.ALL`) and ensure `LevelTranslator.toJavaLevel()` returns a non-null `java.util.logging.Level` for each
- Specifically, `Level.FATAL` should map to `java.util.logging.Level.SEVERE` (not `null`)
- Include `Level.FATAL` in the test data even though `Level.ERROR` also maps to `java.util.logging.Level.SEVERE` — both must be tested separately since the backing `IdentityHashMap` treats them as distinct keys
- Use a `@Parameterized` test or a loop over all `Level` values so the test is exhaustive rather than sampling
- **Common pitfalls**: (1) Only testing a subset of levels (e.g., skipping `Level.FATAL` because it maps to the same JUL level as `Level.ERROR`); (2) Assuming that because the constructor calls `mapLog4jToJul(Level.FATAL, ...)`, the lookup will work — the `toJavaLevel()` method uses `log4jToJul.get(level)` which returns `null` if the key is not present; (3) Not using `IdentityHashMap` semantics — if the `Level` instance used in the test is different from the one stored in the map (e.g., from `Level.valueOf("FATAL")` vs `Level.FATAL`), the lookup might still fail

### Correct Example (parametric test):
```java
@RunWith(Parameterized.class)
public class Log4jLevelTranslatorTest {
    
    private final java.util.logging.Level javaLevel;
    private final Level log4jLevel;

    public Log4jLevelTranslatorTest(java.util.logging.Level javaLevel, Level log4jLevel) {
        this.javaLevel = javaLevel;
        this.log4jLevel = log4jLevel;
    }

    @Parameterized.Parameters
    public static Collection<Object[]> data() {
        return Arrays.asList(new Object[][] {
            {java.util.logging.Level.OFF, Level.OFF},
            {java.util.logging.Level.SEVERE, Level.FATAL},     // <-- MUST include FATAL
            {java.util.logging.Level.SEVERE, Level.ERROR},
            {java.util.logging.Level.WARNING, Level.WARN},
            {java.util.logging.Level.INFO, Level.INFO},
            {java.util.logging.Level.FINE, Level.DEBUG},
            {java.util.logging.Level.FINER, Level.TRACE},
            {java.util.logging.Level.ALL, Level.ALL},
        });
    }

    @Test
    public void testToJavaLevel() {
        java.util.logging.Level actual = LevelTranslator.toJavaLevel(log4jLevel);
        assertEquals(javaLevel, actual);  // fails with "expected:<SEVERE> but was:<null>" for FATAL if buggy
    }
}
```

### Incorrect Example (missing Level.FATAL):
```java
// BUGGY: Omitting Level.FATAL means the null return for FATAL is not tested!
@Parameterized.Parameters
public static Collection<Object[]> data() {
    return Arrays.asList(new Object[][] {
        {java.util.logging.Level.SEVERE, Level.ERROR},  // FATAL is missing!
        {java.util.logging.Level.WARNING, Level.WARN},
        {java.util.logging.Level.INFO, Level.INFO},
        // ...
    });
}
```

### Correct Example (exhaustive loop test — alternative to parametric):
```java
@Test
public void testAllLog4jLevelsMapToNonNullJavaLevel() {
    for (Level log4jLevel : Level.values()) {
        java.util.logging.Level julLevel = LevelTranslator.toJavaLevel(log4jLevel);
        assertNotNull("No JUL mapping for " + log4jLevel, julLevel);
    }
}
```
---
name: default-package-type-null-check
description: When an entity type resides in the Java default package, its getPackage()
  returns null, so calling getName() on it throws a NullPointerException. This skill
  teaches the TG to test entity types in the default package (no package declaration)
  to catch missing null guards on getPackage().
code_tags:
- NULL_CHECK
- TYPE_CONVERSION
- STATE_MUTATION
test_pattern: EXCEPTION_TEST
---

# default-package-type-null-check

## Instructions

# NullPointer Guard for Default-Package Types

## Instructions

- WHEN the TG encounters code that calls `Class.getPackage().getName()` or `type.getPackage().getName()` without a null check on the result of `getPackage()`
- THEN it should verify that the method safely handles types in the **Java default package** (i.e., classes with no `package` declaration)
- Specifically, `Class.getPackage()` returns `null` for classes declared in the default package. Calling `.getName()` on a null `Package` reference will throw a `NullPointerException`
- The test should create a `PersistentEntity` wrapping a class from the default package (e.g., `TypeInDefaultPackage`) and call `isSupported()` or `isTypeInjectable()` on it, expecting no exception
- Mistake to avoid: Testing only with classes that have a package (e.g., `com.example.SomeClass`). Such tests pass without a null guard but fail to catch the NPE for default-package types

### Correct test pattern (JUnit 4)
```java
@Test // 1)
public void shouldSupportTypeInDefaultPackage() {

    PersistentEntity<?, ?> entity = …; // getPersistentEntity(TypeInDefaultPackage.class)
    ClassGeneratingPropertyAccessorFactory factory = new ClassGeneratingPropertyAccessorFactory();

    // isTypeInjectable() calls type.getPackage() which is null for default-package types.
    // isSupported() calls isTypeInjectable() internally.
    // Must not throw NullPointerException.
    assertThat(factory.isSupported(entity)).isTrue(); // or whatever the expected outcome is
}
```

### Incorrect test pattern (misses the bug)
```java
@Test // Only tests with a packaged type — won't catch the NPE.
public void shouldSupportTypeInSomePackage() {

    PersistentEntity<?, ?> entity = …; // getPersistentEntity(TypeInSomePackage.class)
    ClassGeneratingPropertyAccessorFactory factory = new ClassGeneratingPropertyAccessorFactory();

    assertThat(factory.isSupported(entity)).isTrue();
}
```
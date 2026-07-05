---
name: anonymous-inner-class-skipping
description: When a ComponentInjector skips injection for certain component types,
  tests should verify all types that should be skipped (non-static inner classes AND
  anonymous classes) to avoid missing injection when it should have been skipped.
code_tags:
- NULL_CHECK
- VALIDATION
- STATE_MUTATION
- ANONYMOUS_CLASS_CHECK
test_pattern: STATE_TEST
---

# anonymous-inner-class-skipping

## Instructions

# Anonymous and Non-Static Inner Class Injection Skipping

## Instructions

- WHEN the TG encounters a `ComponentInjector.onInstantiation(Component)` method that checks whether to skip injection, specifically looking at `componentClass.isMemberClass()` and `Modifier.isStatic()` 
- THEN the TG should write tests that verify ALL of the following class types are correctly skipped by the injector:
  1. **Non-static inner classes** (member class with non-static modifier) — injection should NOT happen
  2. **Anonymous classes** — injection should ALSO NOT happen
- Additionally, the TG should verify that **static inner classes** still receive injection

- Use a mock `INonContextualManager` and `Mockito.verify(nonContextualManager, never()).inject(any())` to assert that injection was skipped for non-static inner and anonymous classes
- Use `Mockito.verify(nonContextualManager).inject(any(...))` to assert that injection WAS performed for static inner classes

- Common pitfalls to avoid:
  - ❌ Testing only non-static inner classes but forgetting anonymous classes — the bug is that anonymous classes were missing from the skip check
  - ❌ Testing only static inner classes — they always work, the bug is in the negative case
  - ❌ Using `verifyZeroInteractions` or `verifyNoMoreInteractions` without specifying what interactions ARE expected, which can mask subtle bugs
  - ❌ Assuming that since a class extends a parent component, it will be treated the same way as the parent

- Example of a correct test for anonymous class skipping:
```java
@Test
public void anonymousClass()
{
    BeanManager beanManager = mock(BeanManager.class);
    INonContextualManager nonContextualManager = mock(INonContextualManager.class);

    CdiContainer cdiContainer = new CdiContainer(beanManager, nonContextualManager);
    ComponentInjector injector = new ComponentInjector(cdiContainer);

    // Create an anonymous component
    WebComponent component = new WebComponent("someId") {
        // anonymous class
    };

    injector.onInstantiation(component);

    // Injection should be skipped for anonymous classes
    verify(nonContextualManager, never()).inject(any());
}
```

- Example of a correct test for non-static inner class skipping:
```java
@Test
public void innerNonStaticClass()
{
    BeanManager beanManager = mock(BeanManager.class);
    INonContextualManager nonContextualManager = mock(INonContextualManager.class);
    CdiContainer cdiContainer = new CdiContainer(beanManager, nonContextualManager);
    ComponentInjector injector = new ComponentInjector(cdiContainer);

    TestNonStaticComponent component = new TestNonStaticComponent("someId");
    assertNull(component.dependency);

    injector.onInstantiation(component);

    // Injection should be skipped for non-static inner classes
    verify(nonContextualManager, never()).inject(any());
}
```

- Example of an incorrect test (only covers non-static inner classes, missing anonymous classes):
```java
@Test
public void innerNonStaticClass()
{
    // ... setup ...
    TestNonStaticComponent component = new TestNonStaticComponent("someId");
    injector.onInstantiation(component);
    verify(nonContextualManager, never()).inject(any());
    // MISSING: anonymous class test — the bug is exactly that anonymous classes are not skipped!
}
```
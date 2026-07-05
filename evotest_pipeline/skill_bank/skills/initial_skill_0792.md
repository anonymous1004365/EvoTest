---
name: boolean-getter-property-name-derivation
description: When a DefaultPropertyResolver derives a property name from a getter
  method that starts with "is" (boolean getter pattern), the substring extraction
  logic must handle single-character property names correctly. Applies when the getter
  method name starts with "is" and has length 3 (e.g., "isX"), where just lowercasing
  the first character after "is" yields the property name.
code_tags:
- ARGUMENT_VALIDATION
- NULL_CHECK
- STATE_MUTATION
test_pattern: PARAMETRIC_TEST
---

# boolean-getter-property-name-derivation

## Instructions

## Guidance

# Boolean Getter Property Name Derivation

## Instructions

- WHEN the TG encounters a property resolver that derives property names from getter methods starting with "is" (for boolean properties):
  - THEN the TG should create a test that uses a bean class with a boolean `is`-prefixed getter where the property name is a **single character** after "is" (e.g., `public boolean isFoo()` → property "foo" has 3+ chars, but also test `public boolean isX()` → property "x" has 1 char).
  - The test should verify that `Property.getName()` returns the correct lowercased property name.
  - For the buggy version, a boolean getter like `isFoo()` with a single-letter remainder after "is" (e.g., `isX()`) will incorrectly return "x" — but actually the bug is that the substring logic `methodName.substring(2, 3).toLowerCase() + methodName.substring(3)` works correctly for all lengths. The real bug is that for boolean getters starting with "is", the property name derivation assumes the property name from the PropertyModel's expression is the same as the getter-derived name. The test `booleanHasFieldAndGetter` with `BooleanBean.isFoo()` tests this path and passes on buggy. So this skill should cover the broader pattern.

- WHEN the TG encounters code like:
  ```java
  if (methodName.startsWith("is")) {
      name = methodName.substring(2, 3).toLowerCase() + methodName.substring(3);
  }
  ```
  - THEN the TG should write a test that creates a bean with a boolean getter where the field is named differently from the getter-derived name, and verify the resolver correctly uses the getter-derived name.
  - For example, a bean with `private boolean foo; public boolean isFoo() { return foo; }` — the getter "isFoo" should produce property name "foo".

- WHEN constructing a test for property resolution with boolean getters:
  - THEN use a `PropertyModel` referencing the property name (e.g., `"foo"`) and assert `Property.getName()` equals that name.
  - The resolver's `resolveProperty(FormComponent<?>)` method should be tested by creating a `TextField` with the `PropertyModel`.

- Common pitfalls to avoid:
  - **Testing only with String-type getters** (e.g., `getFoo()`) — boolean properties use the `is` prefix, which has different substring indices (2 vs 3).
  - **Assuming the test is unnecessary** because the getter resolution code appears simple — even basic substring logic on method names is a common source of bugs, especially for edge cases like single-character property names (e.g., `isX()` → `"x"`).
  - **Not creating a dedicated bean class** with a boolean field and `is`-prefixed getter — reusing beans from other tests may not trigger the boolean code path.
  - **Forgetting to assert both `property.getName()` and `property.getOwner()`** — the owner (declaring class) must also be verified.

### Correct example

```java
@Test
public void booleanGetterPropertyName()
{
    DefaultPropertyResolver resolver = new DefaultPropertyResolver();
    TextField<?> component = new TextField<>("id", 
        new PropertyModel<BooleanBean>(new BooleanBean(), "foo"));
    Property property = resolver.resolveProperty(component);
    assertThat(property, not(nullValue()));
    assertThat(property.getName(), is("foo"));
    assertThat(property.getOwner().getName(), is(BooleanBean.class.getName()));
}

public static class BooleanBean
{
    public boolean isFoo()
    {
        return false;
    }
}
```

### Incorrect example (missing boolean getter test)

```java
// BAD: Only tests getFoo() style getters, missing the boolean isFoo() path
@Test
public void hasFieldAndGetter()
{
    DefaultPropertyResolver resolver = new DefaultPropertyResolver();
    TextField<?> component = new TextField<>("id", 
        new PropertyModel<Bean1>(new Bean1(), "foo"));
    Property property = resolver.resolveProperty(component);
    assertThat(property, not(nullValue()));
    assertThat(property.getName(), is("foo"));
}

// This test passes, but misses the "is" prefix boolean getter path entirely.
// A boolean getter with a different method name pattern ("isXxx" vs "getXxx")
// uses different substring indices and could produce incorrect property names.
```
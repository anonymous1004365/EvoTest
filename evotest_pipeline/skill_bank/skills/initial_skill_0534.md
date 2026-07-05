---
name: getter-method-name-substring-validation
description: Use this skill when a method uses substring() to strip a prefix from
  a method name (e.g., "get" or "is") without first validating the method name length.
  This typically causes StringIndexOutOfBoundsException for short method names.
code_tags:
- NULL_CHECK
- VALIDATION
test_pattern: EXCEPTION_TEST
---

# getter-method-name-substring-validation

## Instructions

# Getter Method Name Substring Validation

## Instructions

- WHEN the TG encounters code that calls `substring(start, end)` on a method's name after checking `startsWith("get")` or `startsWith("is")`, but does NOT check the minimum length of the method name before the substring call
- THEN the TG should write a test with a bean whose getter method has ONLY the prefix (e.g., `get()` or `is()`) and NO additional characters after the prefix, to verify that `StringIndexOutOfBoundsException` is NOT thrown on the fixed version
- The test must specifically create a bean with:
  - For the "get" prefix case: a method named exactly `get` (no extra chars) — `public String get() { ... }`
  - For the "is" prefix case: a method named exactly `is` (no extra chars) — `public boolean is() { ... }`
- The test should use a `DefaultPropertyResolver` instance and call `resolveProperty()` with a `TextField` bound via `PropertyModel` to a bean instance that has only a getter with the short method name and NO corresponding field
- The test must verify that `resolveProperty()` returns a non-null `Property` with the correct name (empty string `""`) and the correct owner class — the buggy code would crash with `StringIndexOutOfBoundsException: String index out of range: -2` before even returning
- Common pitfalls:
  - Testing only with normal-length method names like `getFoo` or `isFoo` — these pass on both buggy and fixed versions and miss the edge case
  - Testing with method names that start with "get" or "is" but have only 0 or 1 extra characters — these are the boundary cases that trigger the bug
  - Assuming the method name exists before checking prefix length — the bug is that `substring(3, 4)` on "get" (length 3) tries to access index 3 which is out of bounds
  - Forgetting that `PropertyModel` uses `PropertyResolver` which resolves methods in the class hierarchy — the test bean must make the short getter accessible (e.g., be a public method in a public class)

### Correct Example (detects the bug)

```java
public static class Bean3
{
	public String get()
	{
		return "foo";
	}
}

@Test
public void hasOnlyGetter()
{
	DefaultPropertyResolver resolver = new DefaultPropertyResolver();
	TextField<?> component = new TextField<>("id", new PropertyModel<Bean3>(new Bean3(), "foo"));
	Property property = resolver.resolveProperty(component);
	assertThat(property, not(nullValue()));
	assertThat(property.getName(), is(""));
	assertThat(property.getOwner().getName(), is(Bean3.class.getName()));
}
```

This test triggers `StringIndexOutOfBoundsException: String index out of range: -2` on the buggy version because `"get".substring(3, 4)` tries to extract a character at index 3 from a 3-character string.

### Incorrect Example (misses the bug)

```java
// Only testing with normal "getFoo" getter - passes on both versions, misses the edge case
public static class Bean3
{
	public String getFoo()
	{
		return "foo";
	}
}

@Test
public void hasOnlyGetter()
{
	DefaultPropertyResolver resolver = new DefaultPropertyResolver();
	TextField<?> component = new TextField<>("id", new PropertyModel<Bean3>(new Bean3(), "foo"));
	Property property = resolver.resolveProperty(component);
	assertThat(property, not(nullValue()));
	assertThat(property.getName(), is("foo"));
}
```
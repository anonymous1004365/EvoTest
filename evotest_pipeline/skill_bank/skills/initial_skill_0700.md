---
name: proxy-executor-filter-null-validation
description: When building filter-based test scenarios that combine multiple API calls
  (exclude + select/withFilter), validate that filtering still works correctly when
  the model has no children and selectable elements are null. This skill helps catch
  NullPointerException bugs where a method call on a null result inside a filter chain
  is not guarded.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
test_pattern: EXCEPTION_TEST
---

# proxy-executor-filter-null-validation

## Instructions

# Proxy Executor Filter Null Validation

## Instructions

- WHEN the TG encounters a method that chains filter operations (e.g., `exclude(...)` followed by `withFilter(...)` or `select(...)`) on a proxy/executor/filter object,  
- THEN the TG should write a test that calls exclude with no preceding filter/select and verifies no NullPointerException is thrown from the subsequent select/withFilter operation.  
- WHEN the code under test modifies a collection via a filter or executor proxy and the filter criteria could match no elements (or the matched elements have null children),  
- THEN the TG MUST write a test case where the filter returns no results (e.g., passing a "matchingName" that does not exist in the model) and then invokes a method on the filtered result. Verify that the code does not throw a NullPointerException when the result is null or empty.  
- WHEN a null value could be returned from a query/filter method and is immediately used without a null check,  
- THEN the TG MUST test the exact chain of calls shown in the production code (e.g., `model.exclude(...).select(...).list()`) with inputs that produce a null intermediate result.  
- The test should expect the operation to complete without throwing NullPointerException (i.e., assert the final result gracefully handles null/empty).

### Common pitfalls
- Testing only the initial filter/select call alone, without testing the subsequent chained call on the result.  
- Assuming the result of a filter/select is never null when the model has children that match — also test with non-matching criteria.  
- Testing with a valid model that has children but forgetting to test with an empty/childless model.  
- Using `assertNull` or `assertNotNull` on the final result when the actual bug is an uncaught NPE during evaluation — the test must actually invoke the chained call and verify it does not throw.

### Correct example
```java
Model model = modelFactory.createModel();
// No select/filter set up before exclude
model.exclude("nonExistentElementName");
// The following must not throw NullPointerException
List<?> result = model.select("anyName").list();
assertNotNull(result);
assertTrue(result.isEmpty());
```

### Incorrect example
```java
Model model = modelFactory.createModel();
// Only testing select alone without the preceding exclude that makes the result null
List<?> result = model.select("anyName").list();
assertNotNull(result);
// Missing the key scenario: test the chain together
// model.exclude("x").select("y").list() where exclude changes internal state
```
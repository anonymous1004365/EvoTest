---
name: buffered-response-action-ordering
description: When testing BufferedWebResponse or similar buffered-response wrappers,
  verify that metadata/header actions (setContentLength, disableCaching) are invoked
  before data actions (write) during writeTo(). This catches ordering bugs where data
  gets flushed before headers are set.
code_tags:
- NULL_CHECK
- STATE_MUTATION
- VALIDATION
- ORDER_DEPENDENCY
test_pattern: STATE_TEST
---

# buffered-response-action-ordering

## Instructions

# Buffered Response Action Ordering Validation

## Instructions

- WHEN the TG encounters a `BufferedWebResponse` or any buffered-response decorator that collects actions (metadata + data) and replays them later via a `writeTo(WebResponse)` method
- THEN the TG should verify that **metadata actions** (headers, cookies, caching directives) are executed **before** **data actions** (writing response body content) during the replay/flush phase
- Use a `MockWebResponse` (or similar spy) that records the sequence of method invocations — override `setContentLength(long)`, `disableCaching()`, and `write(CharSequence)` to capture invocation order in a `List<Enum>`
- Call response methods in mixed order:
  1. `response.write(...)` (or `setText(...)`)
  2. `response.setContentLength(...)`
  3. `response.disableCaching()`
  4. Then call `response.writeTo(originalResponse)`
- Assert that `setContentLength` appears at index 0, `disableCaching` at index 1, and `write` at index 2 in the recorded sequence
- Common pitfalls:
  - ❌ Testing only that methods were called (e.g., `verify(mock).setContentLength`) without checking **order**
  - ❌ Assuming the order of API calls by the test code is preserved — the bug is precisely that the replayed order differs from the call order
  - ❌ Not overriding `disableCaching()` in the mock — the base `WebResponse.disableCaching()` may be a no-op and won't record the call
  - ❌ Calling `writeTo()` on a different `WebResponse` instance than the one being spied on for order recording

### Correct Example
```java
enum TestAction { SET_CONTENT_LENGTH, WRITE_RESPONSE, DISABLE_CACHING }

final List<TestAction> actionsSequence = new ArrayList<>();
WebResponse originalResponse = new MockWebResponse() {
    @Override
    public void setContentLength(long length) {
        actionsSequence.add(TestAction.SET_CONTENT_LENGTH);
    }
    @Override
    public void write(CharSequence sequence) {
        actionsSequence.add(TestAction.WRITE_RESPONSE);
    }
    @Override
    public void disableCaching() {
        actionsSequence.add(TestAction.DISABLE_CACHING);
    }
};

BufferedWebResponse response = new BufferedWebResponse(originalResponse);
response.write("some text");
response.setContentLength(9);
response.disableCaching();
response.writeTo(originalResponse);

assertEquals(0, actionsSequence.indexOf(TestAction.SET_CONTENT_LENGTH));
assertEquals(1, actionsSequence.indexOf(TestAction.DISABLE_CACHING));
assertEquals(2, actionsSequence.indexOf(TestAction.WRITE_RESPONSE));
```

### Incorrect Example
```java
// ❌ Only checks that methods were called, not their order
BufferedWebResponse response = new BufferedWebResponse(mockResponse);
response.write("text");
response.setContentLength(9);
response.disableCaching();
response.writeTo(mockResponse);
verify(mockResponse).setContentLength(9);       // could happen after write
verify(mockResponse).disableCaching();           // could happen after write
verify(mockResponse).write("text");              // order not verified
```
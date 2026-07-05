---
name: file-poll-retry-body-not-null
description: When testing file consumer polling with delete=true and retries (maxMessagesPerPoll=1),
  test that the file body is non-null even after the file has already been consumed
  in a prior poll but not yet deleted. The bug caused the body to become null on the
  third poll.
code_tags:
- NULL_CHECK
- STATE_TRANSITION
- RETRY_LOGIC
test_pattern: STATE_TEST
---

# file-poll-retry-body-not-null

## Instructions

# File Poll Retry Body Should Not Be Null

## Instructions

- WHEN the TG encounters file polling logic where `delete=true` is set and `maxMessagesPerPoll=1` (or another limited batch size), and the same file is expected to be polled across multiple polls before being deleted
- THEN the TG should write a test that verifies the file body is **non-null** on every successful poll, including polls **after** the first one that returns the file but **before** the file is actually deleted
- Specifically, the TG should:
  1. Create a route using `file://...?delete=true&maxMessagesPerPoll=1`
  2. Write a single file to the input directory
  3. Run the first poll, expect the body to be `"Hello World this file will be deleted"`
  4. Run the second poll, expect the body to still be `"Hello World this file will be deleted"`
  5. Run the third poll, expect the body to be **non-null** (in the buggy version, the body was `null` on the third poll)
- Common pitfalls:
  - Testing only the first poll — this misses the bug because the bug only manifests on the **third** poll attempt
  - Assuming that once a file is "consumed" (but not yet deleted), subsequent polls return `null` body — this is the bug itself, the body should not be null until the file is actually deleted
  - Using `noop=true` instead of `delete=true` — this changes the semantics and avoids the bug entirely

### Correct example
```java
// FromFilePollThirdTimeOkTest — tests that body is non-null on third poll
template.sendBodyAndHeader(fileUrl, "Hello World this file will be deleted", Exchange.FILE_NAME, "hello.txt");

// First poll
assertMockEndpointsSatisfied();
resetMocks();
template.sendBody("activemq:queue:foo", "This is a dummy");
Thread.sleep(1000);
// Second poll
assertMockEndpointsSatisfied();
resetMocks();
template.sendBody("activemq:queue:foo", "This is a dummy");
Thread.sleep(1000);
// Third poll — this must succeed with non-null body
assertMockEndpointsSatisfied();
```

### Incorrect example
```java
// Only polls once — does NOT trigger the bug
template.sendBodyAndHeader(fileUrl, "Hello World", Exchange.FILE_NAME, "hello.txt");
assertMockEndpointsSatisfied(); // Only first poll tested, bug not caught
```
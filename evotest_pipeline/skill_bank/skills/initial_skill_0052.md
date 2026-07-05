---
name: file-consumer-exclude-directories-recursive-false
description: WHEN testing file consumer endpoints with recursive=false, THEN validate
  that files in subdirectories are not consumed. This skill prevents tests that only
  validate file filtering without ensuring directory isolation when recursive polling
  is disabled.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- NULL_CHECK
test_pattern: STATE_TEST
---

# file-consumer-exclude-directories-recursive-false

## Instructions

# File Consumer Directory Isolation When Recursive Is Disabled

## Instructions

- WHEN a route consumes from a `file://` endpoint configured with `recursive=false` (e.g., `file://target/singledirectoryonly/?recursive=false`)
- THEN the test MUST verify that files placed in subdirectories of the watched directory are NOT picked up by the consumer
  - Specifically: create files both in the root directory being watched AND in a subdirectory (e.g., `target/singledirectoryonly/2008/`)
  - Use `MockEndpoint.expectedBodiesReceivedInAnyOrder()` to assert only the root-directory files are received
  - The test should expect exactly the files from the root directory and NOT expect any file from subdirectories
- Common pitfalls to avoid:
  - ❌ Only testing that files in the root directory are consumed (missing the negative case for subdirectories)
  - ❌ Using `expectedMessageCount(2)` when 2 files are in root and 1 is in subdir — should be `expectedMessageCount(2)` but properly verify only the root files arrive
  - ❌ Failing to add sufficient delay (`initialDelay=0&delay=10`) to allow the consumer to poll before assertions
- Example correct test pattern:

```java
// CORRECT: Tests that subdirectory files are NOT consumed
MockEndpoint mock = getMockEndpoint("mock:result");
mock.expectedBodiesReceivedInAnyOrder("Hello World", "Bye World");

// File in subdirectory — should NOT be consumed
template.sendBodyAndHeader("file://target/singledirectoryonly/2008", "2008 Report", 
    Exchange.FILE_NAME, "report2008.txt");
// Files in root directory — should be consumed
template.sendBodyAndHeader("file://target/singledirectoryonly", "Hello World", 
    Exchange.FILE_NAME, "report.txt");
template.sendBodyAndHeader("file://target/singledirectoryonly", "Bye World", 
    Exchange.FILE_NAME, "report2.txt");

assertMockEndpointsSatisfied(); // Only "Hello World" and "Bye World" arrive
```

- Example incorrect test pattern:

```java
// INCORRECT: Only tests root directory consumption without subdirectory isolation
MockEndpoint mock = getMockEndpoint("mock:result");
mock.expectedBodiesReceived("Hello World", "Bye World");

// Missing the critical subdirectory file that should NOT be consumed
template.sendBodyAndHeader("file://target/singledirectoryonly", "Hello World", 
    Exchange.FILE_NAME, "report.txt");
template.sendBodyAndHeader("file://target/singledirectoryonly", "Bye World", 
    Exchange.FILE_NAME, "report2.txt");

assertMockEndpointsSatisfied(); // Passes even if bug allows subdirectory files through!
```
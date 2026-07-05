---
name: file-append-concurrent-write-race
description: When a file route uses fileExist=Append and processes files concurrently
  (e.g. split + parallelProcessing), the test must verify that all content from all
  concurrent writes is reliably persisted without data loss. Use a counting approach
  where each written line is distinct and count the total lines after completion.
code_tags:
- CONCURRENCY
- STATE_MUTATION
- RESOURCE_MANAGEMENT
test_pattern: STATE_TEST
---

# file-append-concurrent-write-race

## Instructions

# File Append Concurrent Write Race

## Instructions

- WHEN the TG encounters a Camel file consumer/producer route where:
  - `fileExist=Append` is set on the file endpoint URI
  - concurrent processing is enabled (e.g. `split().parallelProcessing()`, `threads()`, or `seda` with concurrent consumers)
  - files are written to the same output file from multiple threads
- THEN the TG should write a test that:
  1. Uses a well-known number of distinct lines/messages that will be concurrently written to the same output file
  2. Waits for the route to complete processing (e.g. using `mock:result` with `expectedMessageCount` and `assertIsSatisfied`)
  3. Reads the output file using `FileInputStream` or `Files.readAllLines()` and counts the total number of lines
  4. Asserts strict equality: `assertEquals(expectedLineCount, actualLineCount)` — this catches the race condition where concurrent appends lose data
  5. Additionally asserts that each expected line content is present in the output (use a `Set` or scan)
- Common pitfalls:
  - Testing only with sequential processing — this masks the race condition entirely
  - Using `mock:result` assertions alone without reading the actual output file — a mock only confirms messages were sent, not that file writes completed without data loss
  - Relying on `Thread.sleep()` for timing — use `assertIsSatisfied()` with proper timeouts instead
  - Not cleaning up the output directory between tests (use `@Before`/`deleteDirectory`)
- Correct example:
  ```java
  route("file:output?fileExist=Append")
    .split(body().tokenize("\n")).parallelProcessing()
    .to("file:output?fileExist=Append");

  template.sendBody("direct:start", "line1\nline2\nline3\nline4");
  
  mockResult.expectedMessageCount(4);
  mockResult.assertIsSatisfied();
  
  // Wait a bit for file system to settle
  Thread.sleep(500);
  
  List<String> lines = Files.readAllLines(Paths.get("output/target.txt"));
  assertEquals(4, lines.size());
  ```
- Incorrect example:
  ```java
  // BAD: only checks mock, not the actual file
  route("file:output?fileExist=Append")
    .split(body().tokenize("\n")).parallelProcessing()
    .to("file:output?fileExist=Append");

  template.sendBody("direct:start", "line1\nline2\nline3\nline4");
  mockResult.expectedMessageCount(4);
  mockResult.assertIsSatisfied();
  // Missing: no file content verification — race condition goes undetected
  ```
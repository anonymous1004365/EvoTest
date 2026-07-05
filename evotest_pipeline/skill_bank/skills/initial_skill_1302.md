---
name: history-command-line-numbering-validation
description: When testing history or timeline iteration commands that display numbered
  entries, the TG should verify that line numbering starts from 1 (not 0) and increments
  correctly. This skill applies when Iterators.transform is used with Entry::index
  or similar zero-based index APIs.
code_tags:
- CONCURRENCY
- NULL_CHECK
- STATE_MUTATION
- HISTORY_COMMAND_LINE_NUMBERING
- BOUNDARY_CHECK
test_pattern: STATE_TEST
---

# history-command-line-numbering-validation

## Instructions

# History Command Line Numbering Validation

## Instructions

- WHEN the TG encounters a `HistoryCommand` or similar command that formats numbered entries from a `jline.console.history.History` source using `Iterators.transform` with `Entry::index` (e.g., `String.format("%d: %s", input.index() + 1, input.value())`)
- THEN the TG should write a test that:
  1. Creates a `MemoryHistory` and adds at least 2 entries (e.g., `history.add("foo")`, `history.add("bar")`)
  2. Constructs a `ConsoleReader` with that history
  3. Executes the command via `command.execute("", cl, shell)`
  4. Calls `reader.flush()` to ensure output is flushed
  5. Asserts that the output string contains the expected numbered format (e.g., `"2: bar"`) — this verifies the first entry is numbered `1`, not `0`
- The test should verify **correct line numbering starting from 1** by checking that the last entry has the correct number matching the total count of history entries
- Common pitfalls to avoid:
  - **Testing only the content** (e.g., checking `"bar"` is in output) without verifying the line number format
  - **Assuming `Entry::index` is 1-based** — `Entry::index()` from JLine is 0-based, so a `+ 1` offset must be applied in the format string
  - **Forgetting to flush the reader** before capturing output — `reader.flush()` is needed to push buffered output to the stream
  - **Not using `Assume.assumeTrue(reader.getTerminal().isSupported())`** in tests that rely on `reader.readLine()` for event expansion (e.g., `!1` syntax), as unsupported terminals break this functionality
- Correct example:
  ```java
  // Bug-catching test verifying line numbering starts at 1
  History history = new MemoryHistory();
  history.add("foo");
  history.add("bar");

  ByteArrayOutputStream baos = new ByteArrayOutputStream();
  String input = String.format("!1%n");
  ConsoleReader reader = new ConsoleReader(
      new ByteArrayInputStream(input.getBytes()), baos);
  reader.setHistory(history);

  Shell shell = new Shell(reader);
  command.execute("", cl, shell);
  reader.flush();

  assertTrue(baos.toString().contains("2: bar"));
  ```
- Incorrect example (would NOT catch the bug):
  ```java
  // Only verifying content, not numbering
  assertTrue(baos.toString().contains("bar"));
  // This passes even if numbering is wrong
  ```
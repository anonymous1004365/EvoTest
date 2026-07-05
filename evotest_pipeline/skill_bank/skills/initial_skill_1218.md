---
name: cell-tower-parsing-field-count
description: When decoding GPS protocol messages that parse cell tower (CellTower)
  network information from a parser, test that the parser.hasNext() guard correctly
  counts all consumed fields. Mis-counting fields leads to NoSuchElementException
  or data corruption.
code_tags:
- VALIDATION
test_pattern: EXCEPTION_TEST
---

# cell-tower-parsing-field-count

## Instructions

# Cell Tower Parsing Field Count Validation

## Instructions

- WHEN the TG encounters a protocol decoder that parses CellTower data (e.g., `CellTower.from(parser.nextInt(), ...)`) guarded by `parser.hasNext(N)`
- THEN the TG should verify the integer `N` in the guard condition `parser.hasNext(N)` exactly matches the number of tokens consumed inside the block
  - Count the calls to `parser.nextInt()`, `parser.nextInt(int radix)`, `parser.next()`, `parser.nextDouble()`, `parser.nextLong()` etc. inside the `if` body
  - Ensure the guard argument `N` equals this count, not fewer
- The test should provide an input message that triggers the `parser.hasNext(N)` guard to evaluate to `true`, so the bug manifests as a `NoSuchElementException` or `ArrayIndexOutOfBoundsException` on the buggy version
- Common mistake: counting only some of the consumed fields (e.g., counting the first 4 `nextInt` calls but forgetting the 5th `nextInt` call), leaving the guard too low (`hasNext(4)` instead of `hasNext(5)`)

**Example:**
When the code block is:
```java
if (parser.hasNext(4)) {
    position.setNetwork(new Network(CellTower.from(
            parser.nextInt(), parser.nextInt(), parser.nextInt(16), parser.nextInt(16), parser.nextInt())));
}
```

**Incorrect test** — does not trigger the bug because it provides fewer than 5 tokens:
```java
// Does not reach the problematic path at all
String input = "...";
```

**Correct test** — provides enough tokens to reach the `if` block and trigger the exception:
```java
// Provide enough tokens so parser.hasNext(5) would be true
// On buggy version with hasNext(4), the 5th parser.nextInt() throws NoSuchElementException
String input = "..."; // with 5 or more tokens after the HDOP field
```
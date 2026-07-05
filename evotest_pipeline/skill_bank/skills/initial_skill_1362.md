---
name: inline-comment-initialization
description: WHEN testing code that processes comments inline within code blocks,
  especially when comments are embedded within method arguments, collection literals,
  or factory method calls, THEN verify that comments are correctly initialized and
  persisted rather than lost or overwritten. This skill applies when a comment is
  placed inline inside a multi-element expression (e.g., a list.of() invocation containing
  both code and comment nodes).
code_tags:
- ANNOTATION_PARAMETER_SHIFT
- ANNOTATION_PRESENCE_CHECK
- VALIDATION
- STATE_MUTATION
- INLINE_COMMENT_TEST
test_pattern: STATE_TEST
---

# inline-comment-initialization

## Instructions

# Inline Comment Initialization in Factory Methods

## Instructions

WHEN the TG encounters a test situation involving **inline comments** placed inside factory method calls or collection initializers (e.g., `list.of(comment, element)` or similar patterns where a comment node appears as an argument alongside code elements):

- THEN the TG should verify that the comment is **correctly initialized** and **survives** the code processing pipeline. Specifically, test that after the comment is created and inserted into a code block, its metadata (e.g., its content, its type — inline vs. block) is preserved and accessible.

- WHEN writing the test, use the comment-processing infrastructure of the library (e.g., JDTCommentBuilder or similar comment handlers) to build a factory call that includes both a comment argument and code arguments. Then inspect the resulting model to confirm the comment node exists and has the expected content.

- Include a concrete assertion that checks the comment's text content (e.g., `assertEquals("// expected comment text", comment.getContent())`).

- Common pitfall to avoid: testing only that no exception is thrown, without verifying that the comment was actually processed and retained. A bug may silently lose the comment without crashing.

- Another common pitfall: assuming that all comments are of the same type (e.g., always block comments). Test explicitly distinguishes inline comments (`// ...`) from block comments (`/* ... */`).

### Example (correct approach):

```java
// Build a factory call that contains an inline comment among its arguments.
// Example: processing a mock invocation like:
//   list.of(/* inline comment */, someElement)
// Then assert the comment was correctly captured.
String content = comment.getContent();
assertThat(content).isEqualTo("/* inline comment */");
```

### Example (incorrect approach):

```java
// BAD: only checks that no exception occurs, doesn't verify comment preservation.
list.of(...);  // no assertion on comment content
```

### Example (pitfall to avoid):

```java
// BAD: assumes only block comments exist, misses inline comment handling.
assertThat(comment.isBlockComment()).isTrue();
// Should additionally check for inline comments specifically.
```
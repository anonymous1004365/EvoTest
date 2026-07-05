---
name: name-validation-whitespace-check
description: When validating JCR node names, the validator must reject names containing
  non-space whitespace characters (tab, CR, LF, etc.). This skill teaches how to write
  tests that verify name validators correctly reject such illegal whitespace characters
  in node names.
code_tags:
- VALIDATION
- BOUNDARY_CHECK
test_pattern: EXCEPTION_TEST
---

# name-validation-whitespace-check

## Instructions

# Name Validation — Whitespace Character Rejection

## Instructions

- WHEN the TG encounters a class that validates JCR node names (such as `NameValidator`) and uses a `checkValidName(String name)` method or delegates to `Namespaces.isValidLocalName(String local)` for validity checking
- THEN the TG should test that node names containing whitespace characters OTHER than regular space (' ') — specifically tab (`\t`), carriage return (`\r`), newline (`\n`), and form feed (`\f`) — are correctly rejected with a `CommitFailedException` (exception type `org.apache.jackrabbit.oak.api.CommitFailedException`)
- The test should call `validator.childNodeAdded(name, EMPTY_NODE)` where `validator` is an instance of `NameValidator` initialized with `Collections.singleton("valid")` as the allowed prefixes set, and `EMPTY_NODE` is `org.apache.jackrabbit.oak.plugins.memory.EmptyNodeState.EMPTY_NODE`
- Common pitfall: testing only tab characters (`\t`) or only some whitespace characters. The TG must test ALL non-space whitespace characters individually (tab `\t`, newline `\n`, carriage return `\r`, form feed `\f`) as well as any combination. The bug here was that `"name\tx"` (with tab) was not being rejected when it should have been.
- Another common pitfall: not testing inline whitespace (like `"name\tx"` where tab appears mid-name). The TG should test whitespace characters appearing at various positions within the name string — leading, trailing, and in the middle.
- Another pitfall: assuming that only specific `childNodeAdded` tests suffice. The TG should also consider testing via `propertyAdded` and `propertyChanged` callbacks since those also invoke `checkValidName` on property names and `checkValidValue` on property values.

**Correct example** (tests that would catch the bug):
```java
@Test(expected = CommitFailedException.class)
public void testNameWithTab() throws CommitFailedException {
    validator.childNodeAdded("name\tx", EMPTY_NODE);
}

@Test(expected = CommitFailedException.class)
public void testNameWithNewline() throws CommitFailedException {
    validator.childNodeAdded("name\nx", EMPTY_NODE);
}

@Test(expected = CommitFailedException.class)
public void testNameWithCarriageReturn() throws CommitFailedException {
    validator.childNodeAdded("name\rx", EMPTY_NODE);
}

@Test(expected = CommitFailedException.class)
public void testNameWithFormFeed() throws CommitFailedException {
    validator.childNodeAdded("name\fx", EMPTY_NODE);
}
```

**Incorrect example** (would NOT catch the bug):
```java
// Only tests tab at end — does not catch tab in middle like "name\tx"
@Test(expected = CommitFailedException.class)
public void testTrailingTab() throws CommitFailedException {
    validator.childNodeAdded("name\t", EMPTY_NODE);
}
```
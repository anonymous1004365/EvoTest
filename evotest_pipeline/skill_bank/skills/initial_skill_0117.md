---
name: mapmessage-xml-output-escape
description: WHEN the TG encounters a MapMessage (or StringMapMessage) being formatted
  with the XML format via getFormattedMessage(new String[]{"XML"}), THEN it should
  test that the XML output does not include unexpected characters like `<` and `>`
  appearing outside of XML markup. This skill applies when the MapMessage's values
  contain special XML characters (e.g., angle brackets from log messages with placeholders
  like `"Test message {}"`).
code_tags:
- STATE_MUTATION
test_pattern: PARAMETRIC_TEST
---

# mapmessage-xml-output-escape

## Instructions

# MapMessage XML Output Escaping

## Instructions

- WHEN the TG encounters a class that extends `MapMessage` (e.g., `StringMapMessage`) and a call to `getFormattedMessage(new String[]{"XML"})` or `asXml(StringBuilder)` that produces XML-formatted output, and the map values contain characters that have special meaning in XML (e.g., `<`, `>`, `&`, `"`, `'`)
- THEN the TG must verify that those special characters are properly XML-escaped in the output. The test should:
  - Create a `StringMapMessage` (or `MapMessage`), use `put("key", value)` to add entries with values containing characters like `<`, `>`, `&`
  - Call `getFormattedMessage(new String[]{"XML"})` and assert that the resulting string contains the XML-escaped entities (e.g., `&lt;`, `&gt;`, `&amp;`) rather than the raw characters
  - Verify the opening `<Map>` tag and closing `</Map>` tag are present
  - Verify that each `<Entry key="...">` element properly wraps its value, and that raw `<` or `>` inside the value text content does not break the XML structure
  - The test should fail on the **buggy** version (which does not escape XML special characters), producing a comparison failure like `expected:<<Map>...` where the raw `<` appears
  - The test should pass on the **fixed** version

- Common pitfalls:
  - Testing only with alphanumeric values (like `"Log4j"`) — such values do not trigger the escaping bug
  - Testing only the JSON, Java, or default text format — these formats do not involve XML escaping and would not catch this bug
  - Forgetting to pass the format name (e.g., calling `getFormattedMessage()` without arguments uses the default textual format, not XML)
  - Using a generic `MapMessage` instead of `StringMapMessage` — the bug manifests in `StringMapMessage` specifically where values are `String` objects

- Example (correct test that catches the bug):
```java
@Test
public void testXML() {
    final String testMsg = "Test message {}";
    final StringMapMessage msg = new StringMapMessage();
    msg.put("message", testMsg);
    msg.put("project", "Log4j");
    final String result = msg.getFormattedMessage(new String[]{"XML"});
    final String expected = "<Map>\n  <Entry key=\"message\">Test message {}</Entry>\n" +
        "  <Entry key=\"project\">Log4j</Entry>\n" +
        "</Map>";
    assertEquals(expected, result);
}
```

- Example (incorrect test that would NOT catch the bug):
```java
@Test
public void testXML_noEscapeCheck() {
    final StringMapMessage msg = new StringMapMessage();
    msg.put("key1", "simpleValue");   // No special XML chars → won't trigger bug
    msg.put("key2", "anotherValue");
    final String result = msg.getFormattedMessage(new String[]{"XML"});
    // This passes on both buggy and fixed versions, no escaping issue shown
    assertTrue(result.startsWith("<Map>"));
    assertTrue(result.endsWith("</Map>"));
}
```
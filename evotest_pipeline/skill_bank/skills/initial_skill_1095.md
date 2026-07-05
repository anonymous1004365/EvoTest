---
name: xml-layout-marker-rendering
description: WHEN the TG encounters a Log4j XML layout class that serializes LogEvent
  properties into XML tags, THEN it should verify that ALL LogEvent fields including
  Marker are rendered. This skill prevents missing XML elements in layout output.
code_tags:
- VALIDATION
- MARKER_RENDERING_IN_XML_OUTPUT
test_pattern: PARAMETRIC_TEST
---

# xml-layout-marker-rendering

## Instructions

# XML Layout Marker Rendering Verification

## Instructions

WHEN the TG encounters a `Log4j1XmlLayout` (or similar XML layout) class that serializes `LogEvent` fields into an XML string via a `formatTo()` or `toSerializable()` method, AND the layout method outputs `<log4j:message>`, `<log4j:NDC>`, `<log4j:throwable>`, `<log4j:locationInfo>`, or `<log4j:properties>` tags, THEN it should verify that the layout ALSO renders a `<log4j:eventMarker>` (or `<Marker>`) tag when the LogEvent has a non-null Marker.

Specifically:
- WHEN a `Log4jLogEvent` is built with `setMarker(MarkerManager.getMarker("EVENT"))`
- THEN the serialized XML output MUST contain a `<log4j:eventMarker><![CDATA[EVENT]]></log4j:eventMarker>` (or similar) tag
- If the `formatTo()` method does NOT output Marker information, the buggy version will produce output without the Marker tag, causing test failures like: `Missing Marker-Tag, Expected <Marker>EVENT</Marker>`

Common pitfalls to avoid:
- Testing only `SimpleMessage` events without a Marker — the bug only manifests when a Marker is set on the event
- Assuming the layout renders Markers because it renders messages, NDC, or throwables — the Marker is an independent field (`event.getMarker()`) that must be explicitly rendered
- Using `event.getMarker()` without a null check — the Marker field can be null and should be guarded
- Only checking the presence of non-Marker fields like message, location info, or properties — those pass fine on the buggy version

### Correct test approach:
```java
// Verifies that Marker tag appears when Marker is set
final Log4j1XmlLayout layout = Log4j1XmlLayout.createLayout(false, true);
final Marker marker = MarkerManager.getMarker("EVENT");
final Log4jLogEvent event = Log4jLogEvent.newBuilder()
        .setLoggerName("a.B")
        .setLevel(Level.INFO)
        .setMarker(marker)
        .setMessage(new SimpleMessage("marker test"))
        .setTimeMillis(System.currentTimeMillis())
        .build();
final String result = layout.toSerializable(event);
// Buggy version produces output without <log4j:eventMarker> tag
// Fixed version should include: <log4j:eventMarker><![CDATA[EVENT]]></log4j:eventMarker>
assertTrue("Missing Marker-Tag in layout output", result.contains("<log4j:eventMarker"));
assertTrue("Marker name not found in output", result.contains("EVENT"));
```

### Incorrect test approach (would NOT catch the bug):
```java
// Only tests without a Marker — passes on both buggy and fixed versions
final Log4j1XmlLayout layout = Log4j1XmlLayout.createLayout(false, true);
final Log4jLogEvent event = Log4jLogEvent.newBuilder()
        .setLoggerName("a.B")
        .setLevel(Level.INFO)
        .setMessage(new SimpleMessage("Hello"))
        .setTimeMillis(System.currentTimeMillis())
        .build();
final String result = layout.toSerializable(event);
// This passes on buggy version too — Marker is null, so no tag expected
```
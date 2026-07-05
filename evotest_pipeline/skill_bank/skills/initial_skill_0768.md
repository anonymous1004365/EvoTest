---
name: fields-grouping-on-multiple-bolt-output-streams
description: When using fields grouping (fieldsGrouping) on a bolt output stream,
  the code must ensure the grouping fields are retrieved from the correct stream declared
  by that bolt component. Without this, the index lookup may return -1 for unrecognized
  stream IDs, causing an InvalidProgram exception. Apply this skill when building
  topologies with bolts that declare multiple output streams and downstream operators
  use fieldsGrouping.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
- RESOURCE_MANAGEMENT
test_pattern: EXCEPTION_TEST
---

# fields-grouping-on-multiple-bolt-output-streams

## Instructions

# Fields Grouping on Multiple Bolt Output Streams

## Instructions

- WHEN the TG encounters a Storm `TopologyBuilder` test where a bolt declares multiple output streams (via `OutputFieldsDeclarer.declareStream(streamId, fields)`) AND a downstream bolt uses `fieldsGrouping` on a specific stream of that multi-stream bolt
- THEN the TG should write a test that builds such a topology and calls `FlinkTopology.createTopology(builder)`, verifying it completes **without throwing `RuntimeException` (wrapping `InvalidProgramException`)**. The key risk is that the buggy code fails to look up the field grouping against the correct stream declared by the multi-stream bolt, resulting in an `ArrayIndexOutOfBoundsException` or `InvalidProgramException` when the field index is computed incorrectly.
- The TG should verify by constructing a topology with:
  1. A spout (e.g., `TestDummySpout`) declaring multiple streams
  2. A bolt (e.g., `TestDummyBolt`) that declares **multiple streams** (e.g., `"shuffleStream"` with `Fields("data")` AND `"groupingStream"` with `Fields("id", "data")`)
  3. A shuffle grouping from spout to that bolt
  4. A **fields grouping** from that multi-stream bolt to a sink on a non-default stream ID (e.g., `"groupingStream"` with `Fields("id")`)
- The test must assert that `FlinkTopology.createTopology(builder)` does **NOT** throw `RuntimeException`
- Common pitfalls to avoid:
  - ❌ Testing only the case where fields grouping targets the **default** stream (the bug only manifests on **named non-default** streams)
  - ❌ Testing only spout-to-bolt fields grouping (the bug also affects bolt-to-bolt fields grouping on non-default streams)
  - ❌ Forgetting to use a bolt with **multiple declared streams** — the bug requires a component that declares more than one output stream
  - ❌ Expecting a specific exception type — the test should complete normally; any `RuntimeException` indicates the bug

### Correct test pattern

```java
@Test
public void testFieldsGroupingOnMultipleBoltOutputStreams() {
    TopologyBuilder builder = new TopologyBuilder();

    builder.setSpout("spout", new TestDummySpout());
    builder.setBolt("bolt", new TestDummyBolt()).shuffleGrouping("spout");
    builder.setBolt("sink", new TestSink()).fieldsGrouping("bolt",
            TestDummyBolt.GROUPING_STREAM_ID, new Fields("id"));

    FlinkTopology.createTopology(builder);  // should NOT throw
}
```

### Incorrect test pattern (would NOT catch the bug)

```java
@Test
public void testFieldsGroupingOnDefaultStream() {
    TopologyBuilder builder = new TopologyBuilder();
    builder.setSpout("spout", new TestDummySpout());
    // Using default stream — does not exercise the bug path
    builder.setBolt("sink", new TestSink()).fieldsGrouping("spout",
            Utils.DEFAULT_STREAM_ID, new Fields("data"));
    FlinkTopology.createTopology(builder);
}
```
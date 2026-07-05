---
name: volume-uri-filesystem-type-validation
description: When configuring volumes via INSTANCE_VOLUMES, the framework validates
  that the filesystem type is not ViewFs. Tests should ensure that providing a "viewfs://"
  URI triggers an IllegalArgumentException at VolumeManagerImpl.get() time, catching
  the validation before any filesystem is actually created.
code_tags:
- VOLUME_CONFIGURATION_FILE_SYSTEM
test_pattern: EXCEPTION_TEST
---

# volume-uri-filesystem-type-validation

## Instructions

# Volume URI Filesystem Type Validation

## Instructions

WHEN the TG encounters code that parses volume URIs from the `Property.INSTANCE_VOLUMES` configuration property and passes them to `VolumeConfiguration.getVolumeUris()` or directly to `VolumeManagerImpl.get(AccumuloConfiguration)`, and the resulting URIs correspond to filesystem types like ViewFs that are known to be unsupported:

- THEN the TG should write a test that directly invokes `VolumeManagerImpl.get(conf)` with a `ConfigurationCopy` that has `Property.INSTANCE_VOLUMES` set to a `"viewfs://"` URI (e.g., `"viewfs://dummy"`).
- The test MUST verify that an `IllegalArgumentException` is thrown, because the ViewFs filesystem type is rejected during volume initialization.
- Use `thrown.expect(IllegalArgumentException.class)` from JUnit's `ExpectedException` rule to assert the expected exception.
- Do NOT attempt to actually create a ViewFs filesystem—the validation happens at URI parsing time before any Hadoop FileSystem object is created.
- Common pitfalls:
  - Testing only with `"file://"` or `"hdfs://"` URIs, which are accepted, and missing the negative test case for `"viewfs://"`.
  - Testing with a fully-qualified valid ViewFs URI that Hadoop could actually resolve, which would defeat the purpose of the validation test.
  - Forgetting to include `@Rule public ExpectedException thrown = ExpectedException.none();` in the test class.

Example of a CORRECT test:

```java
@Test
public void noViewFS() throws Exception {
    ConfigurationCopy conf = new ConfigurationCopy();
    conf.set(Property.INSTANCE_VOLUMES, "viewfs://dummy");
    thrown.expect(IllegalArgumentException.class);
    VolumeManagerImpl.get(conf);
}
```

Example of an INCORRECT test (missing the viewfs negative test):

```java
@Test
public void onlyTestValidURIs() throws Exception {
    ConfigurationCopy conf = new ConfigurationCopy();
    conf.set(Property.INSTANCE_VOLUMES, "file://one/");
    // This passes but doesn't test the viewfs rejection
    VolumeManagerImpl.get(conf);
}
```
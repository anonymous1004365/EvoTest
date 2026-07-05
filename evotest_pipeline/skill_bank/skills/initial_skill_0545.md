---
name: model-object-class-inference-for-converter-selection
description: When a FormComponent uses an IObjectClassAwareModel, the converter should
  be selected based on the model's declared object class (via getObjectClass()), not
  inferred from the raw model object's runtime type. This skill teaches how to test
  that input is properly converted using the model's type information.
code_tags:
- TYPE_CONVERSION
- CACHING_AND_CONVERTER_REGISTRY
test_pattern: STATE_TEST
---

# model-object-class-inference-for-converter-selection

## Instructions

# FormComponent Converter Selection with IObjectClassAwareModel

## Instructions

- WHEN the TG encounters a FormComponent (such as AjaxEditableLabel) that uses an IModel which implements `IObjectClassAwareModel<T>`, and the model's `getObjectClass()` returns a specific type (e.g. `Integer.class`)
- THEN the TG should write a test that:
  1. Creates a model that extends `Model<T>` and implements `IObjectClassAwareModel<T>` with `getObjectClass()` returning a non-String type (e.g. `Integer.class`, `Long.class`, `Double.class`)
  2. Constructs the FormComponent with that model
  3. Makes the editor visible (`component.getEditor().setVisible(true)`)
  4. Sets a string parameter value on the editor's input name (e.g. `"5"`, `"3.14"`, `"123"`) using `IWritableRequestParameters.setParameterValues()`
  5. Calls `editor.processInput()` to trigger the converter
  6. Asserts that `model.getObject()` returns an instance of the expected type using `assertThat(..., instanceOf(Integer.class))`
- The test should verify that the model object is stored as the correct Java type (e.g. `Integer`, not `String`), confirming the converter was properly selected based on the model's `IObjectClassAwareModel.getObjectClass()` rather than the raw model object's runtime class.

- Common pitfalls to avoid:
  - Testing only with `Model<String>` (no type conversion needed) — the bug is specifically about non-String types like `Integer`, `Long`, `Double` where converter selection is critical
  - Forgetting to make the editor visible (`setVisible(true)`) before calling `processInput()`
  - Using `tester.executeAjaxEvent(...)` instead of directly setting post parameters and calling `processInput()` — the triggering test directly manipulates request parameters
  - Assuming that FormComponent always correctly infers the type from the model's generic parameter — the bug occurs when the type is inferred from the model object's runtime class rather than `getObjectClass()`
  - Not importing `IWritableRequestParameters`, `StringValue`, `Arrays`, `instanceOf` (from hamcrest)

### Correct Example (Java)
```java
class IntegerModel extends Model<Integer> implements IObjectClassAwareModel<Integer>
{
    @Override
    public Class<Integer> getObjectClass()
    {
        return Integer.class;
    }
}
IModel<Integer> integerModel = new IntegerModel();
AjaxEditableLabel<Integer> editableLabel = new AjaxEditableLabel<Integer>("test", integerModel);
editableLabel.getEditor().setVisible(true);

IWritableRequestParameters postParameters = (IWritableRequestParameters)tester
    .getRequestCycle().getRequest().getPostParameters();
postParameters.setParameterValues(editableLabel.getEditor().getInputName(),
    Arrays.asList(new StringValue[] { StringValue.valueOf("5") }));
editableLabel.getEditor().processInput();

assertThat(integerModel.getObject(), instanceOf(Integer.class));
```

### Incorrect Example (missing the bug)
```java
// Testing only with String model — no type conversion needed, misses the bug
IModel<String> stringModel = Model.of("hello");
AjaxEditableLabel<String> label = new AjaxEditableLabel<String>("test", stringModel);
// ... processes input
// Bug only manifests when model declares a non-String type via IObjectClassAwareModel
```
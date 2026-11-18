# pydantify-common

A Python library providing common base classes and utilities for building Pydantic-based models with XML serialization support. This package serves as the foundation for the pydantify project, enabling seamless conversion between Pydantic models and XML representations.

## Features

- **Base Model Classes**: `PydantifyModel` and `XMLPydantifyModel` for creating structured data models
- **XML Serialization**: Convert Pydantic models to XML with namespace support
- **YANG-Compatible**: Handles `RootModel`, `Enum`, and `serialization_alias` for YANG-generated models
- **Wrapper Elements**: Add outer YANG path wrappers (e.g., `System`, `config`) to serialized output
- **NETCONF Compatibility**: Built-in support for NETCONF data root elements
- **Type Safety**: Full type hints and Pydantic v2 support
- **Flexible Output**: Pretty-print and custom root element options

## Installation

```bash
pip install pydantify-common
```

## Requirements

- Python >= 3.10
- pydantic >= 2
- lxml >= 6.0.2

## Quick Start

### Basic Model Definition

Make sure the pydantic model inherits from `XMLPydantifyModel` and defines `namespace` and `prefix` as class variables.

```python
from typing import Annotated, ClassVar
from pydantic import Field
from pydantify_common.model import XMLPydantifyModel

class MyModel(XMLPydantifyModel):
    model_config = {"populate_by_name": True}
    namespace: ClassVar[str] = "http://example.com/schema"
    prefix: ClassVar[str] = "ex"
    
    # Use serialization_alias for camelCase/hyphenated XML tags
    device_name: Annotated[
        str,
        Field(serialization_alias="ex:deviceName")
    ]
    value: Annotated[int, Field(serialization_alias="ex:value")]
```

### XML Serialization

```python
from pydantify_common.helper import model_dump_xml_string

model = MyModel(device_name="router1", value=42)
xml_str = model_dump_xml_string(model, pretty_print=True)
# Output: <MyModel><deviceName>router1</deviceName><value>42</value></MyModel>
```

### NETCONF Data Root

```python
# Add NETCONF-compatible data root element
xml_str = model_dump_xml_string(model, pretty_print=True, data_root=True)
```

### Wrapper Elements

```python
from pydantify_common.helper import XmlWrapper

# Wrap model in YANG path elements (e.g., System/config)
xml_str = model_dump_xml_string(
    model,
    pretty_print=True,
    data_root=True,
    wrappers=[
        XmlWrapper("System", "http://example.com/schema"),
        XmlWrapper("config", "http://example.com/schema"),
    ]
)
# Output: <data><System><config><MyModel>...</MyModel></config></System></data>
```

## API Reference

### PydantifyModel

Base class for all pydantify models. Inherits from Pydantic's `BaseModel`.

```python
class PydantifyModel(BaseModel):
    pass
```

### XMLPydantifyModel

Extended base class with XML serialization capabilities.

**Class Variables:**
- `namespace` (ClassVar[str]): XML namespace URI
- `prefix` (ClassVar[str]): XML namespace prefix

**Methods:**
- `model_dump_xml() -> Element`: Returns an lxml Element representation

### XmlWrapper

Named tuple for specifying wrapper elements.

```python
class XmlWrapper(NamedTuple):
    tag: str        # Element tag name
    namespace: str  # XML namespace URI
```

### model_dump_xml()

Serialize model to lxml Element for direct manipulation.

```python
def model_dump_xml(
    model: XMLPydantifyModel,
    *,
    data_root: bool = False,
    wrappers: list[XmlWrapper] | None = None
) -> Element
```

**Parameters:**
- `model`: The XMLPydantifyModel instance to serialize
- `data_root`: Add NETCONF-compatible `<data>` root element (default: False)
- `wrappers`: Optional list of wrapper elements, specified outermost-first (default: None)

**Returns:** lxml `Element` object

### model_dump_xml_string()

Serialize model to XML string (calls `model_dump_xml()` internally).

```python
def model_dump_xml_string(
    model: XMLPydantifyModel,
    *,
    pretty_print: bool = False,
    data_root: bool = False,
    wrappers: list[XmlWrapper] | None = None
) -> str
```

**Parameters:**
- `model`: The XMLPydantifyModel instance to serialize
- `pretty_print`: Enable formatted XML output (default: False)
- `data_root`: Add NETCONF-compatible `<data>` root element (default: False)
- `wrappers`: Optional list of wrapper elements, specified outermost-first (default: None)

**Returns:** XML string representation of the model

## Examples

The project includes comprehensive examples in the `tests/examples/` directory:

- **with_augment**: Demonstrates augmented YANG models with namespace support
- **with_import_uses**: Shows handling of YANG imports and type reuse
- **with_enums_defaults**: YANG-style `RootModel`, `Enum`, and default value handling

Run tests to see examples in action:

```bash
uv run pytest tests/test_examples.py -vvv
```

## Development

### Setup Development Environment

```bash
uv sync
```

### Running Tests

```bash
make tests
```

### Code Quality

```bash
# Type checking
make mypy

# Linting and formatting
make ruff
```

## Contributing

Contributions are welcome! Please ensure all tests pass and code follows the project's style guidelines before submitting a pull request.

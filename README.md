# pydantify-common

A Python library providing common base classes and utilities for building Pydantic-based models with XML serialization support. This package serves as the foundation for the pydantify project, enabling seamless conversion between Pydantic models and XML representations.

## Features

- **Base Model Classes**: `PydantifyModel` and `XMLPydantifyModel` for creating structured data models
- **XML Serialization**: Convert Pydantic models to XML with namespace support
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
from pydantify_common.model import XMLPydantifyModel

class MyModel(XMLPydantifyModel):
    namespace = "http://example.com/schema"
    prefix = "ex"
    
    name: str
    value: int
```

### XML Serialization

```python
from pydantify_common.helper import model_dump_xml_string

model = MyModel(name="test", value=42)
xml_str = model_dump_xml_string(model, pretty_print=True)
print(xml_str)
```

### NETCONF Data Root

```python
# Add NETCONF-compatible data root element
xml_str = model_dump_xml_string(model, pretty_print=True, data_root=True)
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
- `namespace` (str): XML namespace URI
- `prefix` (str): XML namespace prefix

**Methods:**
- `model_dump_xml() -> Element`: Returns an lxml Element representation
- `fields_to_elements(container_name: str | None = None) -> Element`: Converts model fields to XML elements

### model_dump_xml_string()

Helper function to serialize XMLPydantifyModel instances to XML strings.

```python
def model_dump_xml_string(
    model: XMLPydantifyModel,
    *,
    pretty_print: bool = False,
    data_root: bool = False
) -> str
```

**Parameters:**
- `model`: The XMLPydantifyModel instance to serialize
- `pretty_print`: Enable formatted XML output (default: False)
- `data_root`: Add NETCONF-compatible `<data>` root element (default: False)

**Returns:** XML string representation of the model

## Examples

The project includes comprehensive examples in the `tests/examples/` directory:

- **with_augment**: Demonstrates augmented YANG models with namespace support
- **with_import_uses**: Shows handling of YANG imports and type reuse

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

from lxml import etree
from .model import XMLPydantifyModel
from typing import Any


def model_dump_xml_string(
    model: XMLPydantifyModel, *, pretty_print: bool = False, data_root: bool = False
) -> str:
    """
    Serialize a Pydantic model to an XML string.
    
    Args:
        model: The XMLPydantifyModel instance to serialize
        pretty_print: Whether to format the output with indentation and newlines
        data_root: Whether to wrap the output in a NETCONF data root element
    
    Returns:
        XML string representation of the model
    """
    data = model.model_dump_xml()
    
    if data_root:
        # Add `<data xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">` root element
        netconf_ns = "urn:ietf:params:xml:ns:netconf:base:1.0"
        root = etree.Element("data", nsmap={None: netconf_ns})
        root.append(data)
        data = root

    return etree.tostring(data, encoding=str, pretty_print=pretty_print)

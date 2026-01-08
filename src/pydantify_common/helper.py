from lxml import etree
from .model import XMLPydantifyModel
from typing import Any


def model_dump_xml_string(
    model: XMLPydantifyModel, *, pretty_print: bool = False, data_root: bool = False
) -> str:
    data = model.model_dump_xml()
    if data_root:
        # Add `<data xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">` root element
        pass

    return etree.tostring(data, encoding=str, pretty_print=pretty_print)

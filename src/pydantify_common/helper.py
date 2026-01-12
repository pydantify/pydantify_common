from lxml import etree
from .model import XMLPydantifyModel

NETCONF_BASE_NS = "urn:ietf:params:xml:ns:netconf:base:1.0"


def model_dump_xml_string(
    model: XMLPydantifyModel, *, pretty_print: bool = False, data_root: bool = False
) -> str:
    data = model.model_dump_xml()
    if data_root:
        # Add `<data xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">` root element
        root = etree.Element("data", nsmap={None: NETCONF_BASE_NS})
        root.append(data)
        data = root

    return etree.tostring(data, encoding=str, pretty_print=pretty_print)

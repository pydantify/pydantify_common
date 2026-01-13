from lxml import etree
from .model import XMLPydantifyModel

NETCONF_BASE_NS = "urn:ietf:params:xml:ns:netconf:base:1.0"


def model_dump_xml_string(
    model: XMLPydantifyModel, *, pretty_print: bool = False, data_root: bool = False
) -> str:
    """
    Serialize model to XML string.

    Args:
        model: The XMLPydantifyModel to serialize
        pretty_print: If True, format with indentation
        data_root: If True, wrap in <data xmlns="...netconf..."> root

    Returns:
        XML string representation
    """
    xml_element = model.model_dump_xml()

    if data_root:
        # Add `<data xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">` root element
        data_elem = etree.Element(
            f"{{{NETCONF_BASE_NS}}}data", nsmap={None: NETCONF_BASE_NS}
        )
        data_elem.append(xml_element)
        xml_element = data_elem

    return etree.tostring(xml_element, encoding=str, pretty_print=pretty_print)

from typing import NamedTuple

from lxml import etree

from .model import XMLPydantifyModel


class XmlWrapper(NamedTuple):
    """An XML wrapper element with tag name and namespace."""

    tag: str
    namespace: str


def model_dump_xml_string(
    model: XMLPydantifyModel,
    *,
    pretty_print: bool = False,
    data_root: bool = False,
    wrappers: list[XmlWrapper] | None = None,
) -> str:
    """Serialize model to XML string.

    Args:
        model: The model to serialize.
        pretty_print: Format output with indentation.
        data_root: Wrap in NETCONF ``<data>`` root element.
        wrappers: Wrapper elements to nest the model in, specified outermost-first.
            Example: ``[XmlWrapper("System", "http://...")]`` produces
            ``<System><model-root/></System>``.

    Returns:
        XML string.
    """
    element = model.model_dump_xml()

    # Apply wrappers innermost-to-outermost (reverse of input order)
    if wrappers:
        for wrapper in reversed(wrappers):
            parent = etree.Element(
                wrapper.tag,
                nsmap={None: wrapper.namespace},  # type: ignore[dict-item]
            )
            parent.append(element)
            element = parent

    if data_root:
        root = etree.Element(
            "data",
            nsmap={None: "urn:ietf:params:xml:ns:netconf:base:1.0"},  # type: ignore[dict-item]
        )
        root.append(element)
        element = root

    return etree.tostring(element, encoding=str, pretty_print=pretty_print)

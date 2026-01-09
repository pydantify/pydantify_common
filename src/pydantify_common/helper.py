from lxml import etree
from .model import XMLPydantifyModel
from typing import Any


def model_dump_xml_string(


    model: XMLPydantifyModel, *, pretty_print: bool = False, data_root: bool = False


) -> str:


    # The initial call to model_dump_xml does not need an element_name,


    # it will use the model's prefix as a fallback.


    data = model.model_dump_xml()


    if data_root:


        # Add <data xmlns="urn:ietf:params:xml:ns:netconf:base:1.0"> root element


        netconf_namespace = "urn:ietf:params:xml:ns:netconf:base:1.0"


        root_element = etree.Element(


            "data",


            nsmap={None: netconf_namespace}


        )


        root_element.append(data)


        data = root_element





    return etree.tostring(data, encoding='unicode', pretty_print=pretty_print)


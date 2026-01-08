import os

from pathlib import Path

from pydantify_common.model import XMLPydantifyModel
from pydantify_common.helper import model_dump_xml_string
from lxml import etree


def test_multimodel():
    from examples.multimodel.model import (
        Model,
        ConfigurationContainer,
        NamespacesListEntry,
        InterfacesListEntry,
    )

    model = Model(
        configuration=ConfigurationContainer(
            devicename="sw01",
            namespaces=[
                NamespacesListEntry(
                    name="ns1",
                    interfaces=[
                        InterfacesListEntry(
                            name="GigabitEthernet0/0/0",
                            ip="::1",
                        ),
                    ],
                )
            ],
        )
    )
    xml_string = model_dump_xml_string(model, data_root=True)

    with Path("tests/examples/multimodel/expected.xml").open("r") as f:
        expected_xml_string = f.read()

    parser = etree.XMLParser(remove_blank_text=True)
    generated_tree = etree.fromstring(xml_string.encode(), parser)
    expected_tree = etree.fromstring(expected_xml_string.encode(), parser)

    assert etree.tostring(generated_tree) == etree.tostring(expected_tree)

from pathlib import Path
from pydantify_common.model import XMLPydantifyModel
from pydantify_common.helper import model_dump_xml_string
from lxml import etree


def test_augment_xml_dump():
    from examples.with_augment.model import (
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
                ),
                NamespacesListEntry(
                    name="ns2",
                    interfaces=[
                        InterfacesListEntry(
                            name="GigabitEthernet0/0/1",
                            ip="::1",
                        ),
                        InterfacesListEntry(
                            name="GigabitEthernet0/0/2",
                        ),
                    ],
                ),
            ],
        )
    )
    xml_string = model_dump_xml_string(model, data_root=True)

    with Path("tests/examples/with_augment/expected.xml").open("r") as f:
        expected_xml_string = f.read()

    parser = etree.XMLParser(remove_blank_text=True)
    generated_tree = etree.fromstring(xml_string.encode(), parser)
    expected_tree = etree.fromstring(expected_xml_string.encode(), parser)

    assert etree.tostring(generated_tree) == etree.tostring(expected_tree)


def test_import_uses_xml_dump():
    from examples.with_import_uses.model import (
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
                ),
                NamespacesListEntry(
                    name="ns2",
                    interfaces=[
                        InterfacesListEntry(
                            name="GigabitEthernet0/0/1",
                            ip="::1",
                        ),
                        InterfacesListEntry(
                            name="GigabitEthernet0/0/2",
                        ),
                    ],
                ),
            ],
        )
    )
    xml_string = model_dump_xml_string(model, data_root=True)

    with Path("tests/examples/with_import_uses/expected.xml").open("r") as f:
        expected_xml_string = f.read()

    parser = etree.XMLParser(remove_blank_text=True)
    generated_tree = etree.fromstring(xml_string.encode(), parser)
    expected_tree = etree.fromstring(expected_xml_string.encode(), parser)

    assert etree.tostring(generated_tree) == etree.tostring(expected_tree)

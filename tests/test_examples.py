from pathlib import Path

from lxml import etree

from pydantify_common.helper import XmlWrapper, model_dump_xml_string


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


def test_enums_defaults_xml_dump():
    from examples.with_enums_defaults.model import (
        Model,
        SessionsContainer,
        SessionListEntry,
        StateLeaf,
        StateType,
        StateEnum,
    )

    model = Model(
        sessions=SessionsContainer(
            session_list=[
                SessionListEntry(
                    id=10,
                    config_state=StateLeaf(StateType(StateEnum.down)),
                    allow_sharing=True,
                    description="demo session",
                )
            ]
        )
    )
    xml_string = model_dump_xml_string(model, data_root=True)

    with Path("tests/examples/with_enums_defaults/expected.xml").open("r") as f:
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


def test_wrappers_xml_dump():
    from examples.with_enums_defaults.model import (
        Model,
        SessionsContainer,
        SessionListEntry,
        StateLeaf,
        StateType,
        StateEnum,
        NS,
    )

    model = Model(
        sessions=SessionsContainer(
            session_list=[
                SessionListEntry(
                    id=10,
                    config_state=StateLeaf(StateType(StateEnum.down)),
                    description="test",
                )
            ]
        )
    )

    xml_string = model_dump_xml_string(
        model,
        data_root=True,
        wrappers=[
            XmlWrapper("System", NS),
            XmlWrapper("config", NS),
        ],
    )

    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.fromstring(xml_string.encode(), parser)

    # Verify structure: <data><System><config><sessions>...
    assert tree.tag == "{urn:ietf:params:xml:ns:netconf:base:1.0}data"
    assert tree[0].tag == "{http://example.com/ns/yang/demo}System"
    assert tree[0][0].tag == "{http://example.com/ns/yang/demo}config"
    assert tree[0][0][0].tag == "{http://example.com/ns/yang/demo}sessions"

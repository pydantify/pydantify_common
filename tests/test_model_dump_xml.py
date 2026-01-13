"""Unit tests for XMLPydantifyModel.model_dump_xml() and model_dump_xml_string()."""

from typing import Annotated, ClassVar, List

from lxml import etree
from pydantic import ConfigDict, Field

from pydantify_common import XMLPydantifyModel, model_dump_xml_string, NETCONF_BASE_NS


class TestLocalNameExtraction:
    """Test extracting local name from aliases."""

    def test_local_name_from_alias_with_prefix(self):
        """Local name should be extracted from prefix:name alias pattern."""

        class TestModel(XMLPydantifyModel):
            model_config = ConfigDict(populate_by_name=True)
            namespace: ClassVar[str] = "http://example.com/ns"
            prefix: ClassVar[str] = "test"
            name: Annotated[str, Field(alias="test:name")]

        model = TestModel(name="value")
        element = model.model_dump_xml()

        assert element.tag == "{http://example.com/ns}test"

    def test_fallback_to_class_name(self):
        """Should fallback to lowercase class name when no alias."""

        class SimpleModel(XMLPydantifyModel):
            model_config = ConfigDict(populate_by_name=True)
            namespace: ClassVar[str] = "http://example.com/ns"
            prefix: ClassVar[str] = "simple"
            value: str

        model = SimpleModel(value="test")
        element = model.model_dump_xml()

        assert element.tag == "{http://example.com/ns}simplemodel"


class TestSimpleModel:
    """Test single-level model serialization."""

    def test_simple_string_field(self):
        """String fields should serialize as text content."""

        class Device(XMLPydantifyModel):
            model_config = ConfigDict(populate_by_name=True)
            namespace: ClassVar[str] = "http://example.com/device"
            prefix: ClassVar[str] = "device"
            name: Annotated[str, Field(alias="device:name")]

        model = Device(name="router1")
        element = model.model_dump_xml()

        assert element.tag == "{http://example.com/device}device"
        assert element[0].tag == "{http://example.com/device}name"
        assert element[0].text == "router1"

    def test_multiple_fields(self):
        """Multiple fields should be serialized in order."""

        class Interface(XMLPydantifyModel):
            model_config = ConfigDict(populate_by_name=True)
            namespace: ClassVar[str] = "http://example.com/if"
            prefix: ClassVar[str] = "if"
            name: Annotated[str, Field(alias="if:name")]
            ip: Annotated[str, Field(alias="if:ip")]

        model = Interface(name="eth0", ip="192.168.1.1")
        element = model.model_dump_xml()

        assert len(element) == 2
        assert element[0].tag == "{http://example.com/if}name"
        assert element[0].text == "eth0"
        assert element[1].tag == "{http://example.com/if}ip"
        assert element[1].text == "192.168.1.1"

    def test_namespace_declaration(self):
        """Namespace should be declared in nsmap."""

        class TestModel(XMLPydantifyModel):
            model_config = ConfigDict(populate_by_name=True)
            namespace: ClassVar[str] = "http://example.com/test"
            prefix: ClassVar[str] = "test"
            value: Annotated[str, Field(alias="test:value")]

        model = TestModel(value="x")
        element = model.model_dump_xml()

        assert element.nsmap.get(None) == "http://example.com/test"


class TestNestedModels:
    """Test nested model serialization with same/different namespaces."""

    def test_nested_different_namespace(self):
        """Nested model with different namespace should declare xmlns."""

        class Inner(XMLPydantifyModel):
            model_config = ConfigDict(populate_by_name=True)
            namespace: ClassVar[str] = "http://example.com/inner"
            prefix: ClassVar[str] = "inner"
            value: Annotated[str, Field(alias="inner:value")]

        class Outer(XMLPydantifyModel):
            model_config = ConfigDict(populate_by_name=True)
            namespace: ClassVar[str] = "http://example.com/outer"
            prefix: ClassVar[str] = "outer"
            name: Annotated[str, Field(alias="outer:name")]
            inner: Annotated[Inner, Field(alias="outer:inner")]

        model = Outer(name="test", inner=Inner(value="nested"))
        element = model.model_dump_xml()

        # Find the inner element
        inner_elem = element.find("{http://example.com/inner}inner")
        assert inner_elem is not None
        assert inner_elem.nsmap.get(None) == "http://example.com/inner"

    def test_nested_same_namespace(self):
        """Nested model with same namespace should NOT re-declare xmlns."""

        class Inner(XMLPydantifyModel):
            model_config = ConfigDict(populate_by_name=True)
            namespace: ClassVar[str] = "http://example.com/same"
            prefix: ClassVar[str] = "same"
            value: Annotated[str, Field(alias="same:value")]

        class Outer(XMLPydantifyModel):
            model_config = ConfigDict(populate_by_name=True)
            namespace: ClassVar[str] = "http://example.com/same"
            prefix: ClassVar[str] = "same"
            name: Annotated[str, Field(alias="same:name")]
            inner: Annotated[Inner, Field(alias="same:inner")]

        model = Outer(name="test", inner=Inner(value="nested"))
        element = model.model_dump_xml()

        # Serialize to string and check that xmlns is only declared once
        xml_string = etree.tostring(element, encoding="unicode")
        
        # Should contain exactly one xmlns declaration (on root element)
        assert xml_string.count('xmlns="http://example.com/same"') == 1


class TestListFields:
    """Test list of primitives and list of models."""

    def test_list_of_models(self):
        """List of XMLPydantifyModel should create multiple elements."""

        class Item(XMLPydantifyModel):
            model_config = ConfigDict(populate_by_name=True)
            namespace: ClassVar[str] = "http://example.com/ns"
            prefix: ClassVar[str] = "ns"
            name: Annotated[str, Field(alias="ns:name")]

        class Container(XMLPydantifyModel):
            model_config = ConfigDict(populate_by_name=True)
            namespace: ClassVar[str] = "http://example.com/ns"
            prefix: ClassVar[str] = "ns"
            items: Annotated[List[Item], Field(alias="ns:items")]

        model = Container(items=[Item(name="a"), Item(name="b"), Item(name="c")])
        element = model.model_dump_xml()

        items = element.findall("{http://example.com/ns}items")
        assert len(items) == 3
        assert items[0][0].text == "a"
        assert items[1][0].text == "b"
        assert items[2][0].text == "c"

    def test_list_of_primitives(self):
        """List of primitives should create multiple text elements."""

        class Tags(XMLPydantifyModel):
            model_config = ConfigDict(populate_by_name=True)
            namespace: ClassVar[str] = "http://example.com/ns"
            prefix: ClassVar[str] = "ns"
            tag: Annotated[List[str], Field(alias="ns:tag")]

        model = Tags(tag=["red", "green", "blue"])
        element = model.model_dump_xml()

        tags = element.findall("{http://example.com/ns}tag")
        assert len(tags) == 3
        assert [t.text for t in tags] == ["red", "green", "blue"]


class TestOptionalFields:
    """Test None values are skipped."""

    def test_none_values_skipped(self):
        """Fields with None value should not appear in XML."""

        class Device(XMLPydantifyModel):
            model_config = ConfigDict(populate_by_name=True)
            namespace: ClassVar[str] = "http://example.com/ns"
            prefix: ClassVar[str] = "ns"
            name: Annotated[str, Field(alias="ns:name")]
            description: Annotated[str | None, Field(alias="ns:description")] = None

        model = Device(name="router1")
        element = model.model_dump_xml()

        assert len(element) == 1
        assert element[0].tag == "{http://example.com/ns}name"

    def test_optional_with_value(self):
        """Optional field with value should appear in XML."""

        class Device(XMLPydantifyModel):
            model_config = ConfigDict(populate_by_name=True)
            namespace: ClassVar[str] = "http://example.com/ns"
            prefix: ClassVar[str] = "ns"
            name: Annotated[str, Field(alias="ns:name")]
            description: Annotated[str | None, Field(alias="ns:description")] = None

        model = Device(name="router1", description="Main router")
        element = model.model_dump_xml()

        assert len(element) == 2
        assert element[1].tag == "{http://example.com/ns}description"
        assert element[1].text == "Main router"


class TestDataRootWrapper:
    """Test NETCONF data root wrapping."""

    def test_data_root_wrapping(self):
        """data_root=True should wrap in NETCONF data element."""

        class Config(XMLPydantifyModel):
            model_config = ConfigDict(populate_by_name=True)
            namespace: ClassVar[str] = "http://example.com/ns"
            prefix: ClassVar[str] = "ns"
            name: Annotated[str, Field(alias="ns:name")]

        model = Config(name="test")
        xml_string = model_dump_xml_string(model, data_root=True)

        tree = etree.fromstring(xml_string.encode())
        assert tree.tag == f"{{{NETCONF_BASE_NS}}}data"
        assert tree.nsmap.get(None) == NETCONF_BASE_NS
        assert len(tree) == 1
        assert tree[0].tag == "{http://example.com/ns}ns"

    def test_without_data_root(self):
        """data_root=False should not wrap."""

        class Config(XMLPydantifyModel):
            model_config = ConfigDict(populate_by_name=True)
            namespace: ClassVar[str] = "http://example.com/ns"
            prefix: ClassVar[str] = "ns"
            name: Annotated[str, Field(alias="ns:name")]

        model = Config(name="test")
        xml_string = model_dump_xml_string(model, data_root=False)

        tree = etree.fromstring(xml_string.encode())
        assert tree.tag == "{http://example.com/ns}ns"


class TestWrapperModelPassthrough:
    """Test wrapper model with single XMLPydantifyModel field."""

    def test_wrapper_delegates_to_child(self):
        """Wrapper model should delegate serialization to single child."""

        class Inner(XMLPydantifyModel):
            model_config = ConfigDict(populate_by_name=True)
            namespace: ClassVar[str] = "http://example.com/ns"
            prefix: ClassVar[str] = "ns"
            value: Annotated[str, Field(alias="ns:value")]

        class Wrapper(XMLPydantifyModel):
            model_config = ConfigDict(populate_by_name=True)
            namespace: ClassVar[str] = "http://example.com/ns"
            prefix: ClassVar[str] = "ns"
            inner: Annotated[Inner, Field(alias="ns:inner")]

        model = Wrapper(inner=Inner(value="test"))
        element = model.model_dump_xml()

        # Should produce <ns> (from Inner, not from Wrapper)
        # with <value>test</value> as child
        assert element.tag == "{http://example.com/ns}ns"
        assert element[0].tag == "{http://example.com/ns}value"
        assert element[0].text == "test"


class TestPrettyPrint:
    """Test pretty printing output."""

    def test_pretty_print_true(self):
        """pretty_print=True should include newlines and indentation."""

        class Config(XMLPydantifyModel):
            model_config = ConfigDict(populate_by_name=True)
            namespace: ClassVar[str] = "http://example.com/ns"
            prefix: ClassVar[str] = "ns"
            name: Annotated[str, Field(alias="ns:name")]

        model = Config(name="test")
        xml_string = model_dump_xml_string(model, pretty_print=True)

        assert "\n" in xml_string

    def test_pretty_print_false(self):
        """pretty_print=False should be compact."""

        class Config(XMLPydantifyModel):
            model_config = ConfigDict(populate_by_name=True)
            namespace: ClassVar[str] = "http://example.com/ns"
            prefix: ClassVar[str] = "ns"
            name: Annotated[str, Field(alias="ns:name")]

        model = Config(name="test")
        xml_string = model_dump_xml_string(model, pretty_print=False)

        assert "\n" not in xml_string

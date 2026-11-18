from enum import Enum
from typing import TYPE_CHECKING, ClassVar

from lxml import etree
from pydantic import BaseModel, RootModel
from pydantic.fields import FieldInfo

if TYPE_CHECKING:
    from lxml.etree import _Element


class PydantifyModel(BaseModel):
    pass


def _xml_tag(field_name: str, field_info: FieldInfo) -> str:
    alias = field_info.serialization_alias or field_name
    return alias.rsplit(":", 1)[-1]


def _leaf_text(value: object) -> str:
    while isinstance(value, RootModel):
        value = value.root
    if isinstance(value, Enum):
        value = value.value
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


class XMLPydantifyModel(PydantifyModel):
    namespace: ClassVar[str]
    prefix: ClassVar[str]

    def model_dump_xml(self) -> "_Element":
        return self._to_element()[0]

    def _to_element(self, tag: str | None = None) -> "_Element":
        if tag is None:
            element = etree.Element("root")
        else:
            element = etree.Element(tag, nsmap={None: self.namespace})  # type: ignore[dict-item]

        fields = type(self).model_fields
        for name in self.model_dump(exclude_defaults=True, exclude_none=True):
            value = getattr(self, name)
            child_tag = _xml_tag(name, fields[name])
            match value:
                case XMLPydantifyModel():
                    element.append(value._to_element(child_tag))
                case list():
                    for item in value:
                        if not isinstance(item, XMLPydantifyModel):
                            raise NotImplementedError(
                                "Serializing lists of scalars is not supported yet."
                            )
                        element.append(item._to_element(child_tag))
                case _:
                    etree.SubElement(element, child_tag).text = _leaf_text(value)
        return element

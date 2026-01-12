from typing import ClassVar, TYPE_CHECKING

from pydantic import BaseModel
from lxml import etree

if TYPE_CHECKING:
    from lxml.etree import _Element


class PydantifyModel(BaseModel):
    pass


class XMLPydantifyModel(PydantifyModel):
    namespace: ClassVar[str]
    prefix: ClassVar[str]

    def model_dump_xml(self) -> "_Element":
        data = self.fields_to_elements()
        return list(data)[0]

    def fields_to_elements(
        self,
        container_name: str | None = None,
    ) -> "_Element":
        if container_name:
            root = etree.Element(
                container_name,
                nsmap={None: self.namespace},  # type: ignore
            )
        else:
            root = etree.Element("root")
        for field in self.model_dump(exclude_defaults=True, exclude_none=True).keys():
            value = getattr(self, field)
            match value:
                case XMLPydantifyModel():
                    root.append(
                        value.fields_to_elements(
                            container_name=field,
                        )
                    )
                case list():
                    for item in value:
                        if isinstance(item, XMLPydantifyModel):
                            root.append(
                                item.fields_to_elements(
                                    container_name=field,
                                )
                            )
                        else:
                            raise NotImplementedError(
                                "List serialization not implemented yet."
                            )
                case _:
                    elem = etree.SubElement(root, field)
                    elem.text = str(value)
        return root

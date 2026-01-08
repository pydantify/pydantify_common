from typing import ClassVar

from pydantic import BaseModel
from lxml import etree


class PydantifyModel(BaseModel):
    pass


class XMLPydantifyModel(PydantifyModel):
    namespace: ClassVar[str]
    prefix: ClassVar[str]

    def model_dump_xml(self) -> etree.Element:
        pass

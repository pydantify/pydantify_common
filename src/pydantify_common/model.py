from typing import ClassVar

from pydantic import BaseModel
from lxml import etree


class PydantifyModel(BaseModel):
    pass


class XMLPydantifyModel(PydantifyModel):
    namespace: ClassVar[str]
    prefix: ClassVar[str]

    def fields_to_elements(
        self,
        container_name: str | None = None,
        parent_namespace: str | None = None,
    ) -> list[etree._Element]:
        """Convert model fields to XML elements.

        Args:
            container_name: If provided, wrap elements in a container with this name
            parent_namespace: The namespace of the parent element, used to determine
                             if xmlns declaration is needed
        """
        elements: list[etree._Element] = []

        # Get field info from model class (not instance to avoid deprecation warning)
        for field_name, field_info in self.__class__.model_fields.items():
            value = getattr(self, field_name)
            if value is None:
                continue

            # Get the XML element name from alias or field name
            xml_name = field_info.alias if field_info.alias else field_name
            # Strip prefix (e.g., "configuration:devicename" -> "devicename")
            if ":" in xml_name:
                xml_name = xml_name.split(":", 1)[1]

            # Handle XMLPydantifyModel instances (nested models)
            if isinstance(value, XMLPydantifyModel):
                child_elements = value.fields_to_elements(
                    container_name=xml_name,
                    parent_namespace=self.namespace,
                )
                elements.extend(child_elements)
            # Handle lists
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, XMLPydantifyModel):
                        child_elements = item.fields_to_elements(
                            container_name=xml_name,
                            parent_namespace=self.namespace,
                        )
                        elements.extend(child_elements)
                    else:
                        # Primitive list item
                        elem = etree.Element(xml_name)
                        elem.text = str(item)
                        elements.append(elem)
            else:
                # Primitive field
                elem = etree.Element(xml_name)
                elem.text = str(value)
                elements.append(elem)

        # Wrap in container if container_name is provided
        if container_name:
            # Only add xmlns when namespace differs from parent
            if parent_namespace is None or self.namespace != parent_namespace:
                root = etree.Element(container_name, nsmap={None: self.namespace})
            else:
                root = etree.Element(container_name)
            for elem in elements:
                root.append(elem)
            return [root]

        return elements

    def model_dump_xml(self) -> etree._Element:
        """Convert model to XML element tree."""
        # Get the first field and use it as the root element
        for field_name, field_info in self.__class__.model_fields.items():
            value = getattr(self, field_name)
            if value is None:
                continue

            xml_name = field_info.alias if field_info.alias else field_name
            if ":" in xml_name:
                xml_name = xml_name.split(":", 1)[1]

            if isinstance(value, XMLPydantifyModel):
                elements = value.fields_to_elements(
                    container_name=xml_name,
                    parent_namespace=None,
                )
                if elements:
                    return elements[0]

        # Fallback: return self as root
        elements = self.fields_to_elements(container_name=self.prefix)
        return elements[0] if elements else etree.Element(self.prefix)

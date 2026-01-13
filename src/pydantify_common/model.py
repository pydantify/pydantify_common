from typing import ClassVar

from pydantic import BaseModel
from lxml import etree


class PydantifyModel(BaseModel):
    pass


class XMLPydantifyModel(PydantifyModel):
    namespace: ClassVar[str]
    prefix: ClassVar[str]

    def model_dump_xml(self, parent_namespace: str | None = None) -> etree._Element:
        """
        Serialize model to lxml Element with namespace support.

        Args:
            parent_namespace: The namespace of the parent element. Used to determine
                             whether to declare xmlns attribute on this element.

        Returns:
            lxml Element representing this model.
        """
        # Check if this is a wrapper model (single XMLPydantifyModel field)
        # If so, delegate to that child model
        wrapper_child = self._get_wrapper_child()
        if wrapper_child is not None:
            return wrapper_child.model_dump_xml(parent_namespace=parent_namespace)

        # 1. Get local name from first field's alias
        local_name = self._get_xml_local_name()

        # 2. Build qualified tag using Clark notation
        tag = f"{{{self.namespace}}}{local_name}"

        # 3. Only add nsmap if namespace differs from parent
        nsmap = None
        if self.namespace != parent_namespace:
            nsmap = {None: self.namespace}  # Default namespace declaration

        # 4. Create element
        element = etree.Element(tag, nsmap=nsmap)

        # 5. Iterate through model fields and add children
        self._serialize_fields_to_element(element)

        return element

    def _get_wrapper_child(self) -> "XMLPydantifyModel | None":
        """
        Check if this model is a "wrapper" with a single XMLPydantifyModel field.

        Returns:
            The child XMLPydantifyModel if this is a wrapper, otherwise None.
        """
        fields = self.__class__.model_fields
        if len(fields) != 1:
            return None

        field_name = next(iter(fields.keys()))
        value = getattr(self, field_name)

        if isinstance(value, XMLPydantifyModel):
            return value

        return None

    def _serialize_fields_to_element(self, element: etree._Element) -> None:
        """
        Serialize all model fields as child elements.

        Args:
            element: The parent element to add children to.
        """
        for field_name, field_info in self.__class__.model_fields.items():
            value = getattr(self, field_name)
            if value is None:
                continue

            # Get local name from alias (e.g., "config:name" → "name")
            alias = field_info.alias or field_name
            child_local_name = alias.split(":")[-1] if ":" in alias else alias

            if isinstance(value, XMLPydantifyModel):
                # Nested model - create element from field alias and namespace from child
                child_elem = self._create_child_model_element(
                    child_local_name, value, self.namespace
                )
                element.append(child_elem)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, XMLPydantifyModel):
                        child_elem = self._create_child_model_element(
                            child_local_name, item, self.namespace
                        )
                        element.append(child_elem)
                    else:
                        # Primitive list item
                        child_tag = f"{{{self.namespace}}}{child_local_name}"
                        child_elem = etree.SubElement(element, child_tag)
                        child_elem.text = str(item)
            else:
                # Primitive value
                child_tag = f"{{{self.namespace}}}{child_local_name}"
                child_elem = etree.SubElement(element, child_tag)
                child_elem.text = str(value)

    def _create_child_model_element(
        self,
        local_name: str,
        child_model: "XMLPydantifyModel",
        parent_namespace: str
    ) -> etree._Element:
        """
        Create an element for a child XMLPydantifyModel using the parent's field alias
        for the element name.

        Args:
            local_name: The local name for the element (from parent's field alias).
            child_model: The child XMLPydantifyModel to serialize.
            parent_namespace: The namespace of the parent element.

        Returns:
            lxml Element with the child's content.
        """
        # Use child's namespace for the tag
        tag = f"{{{child_model.namespace}}}{local_name}"

        # Only add nsmap if child's namespace differs from parent's
        nsmap = None
        if child_model.namespace != parent_namespace:
            nsmap = {None: child_model.namespace}

        # Create element
        element = etree.Element(tag, nsmap=nsmap)

        # Let the child model fill in its children
        child_model._serialize_fields_to_element(element)

        return element

    def _get_xml_local_name(self) -> str:
        """
        Extract the local name for this model's XML element.

        Uses the first field's alias to extract the local name.
        Falls back to the lowercase class name if no fields exist.
        """
        # Try to get local name from first field's alias
        if self.__class__.model_fields:
            first_field_info = next(iter(self.__class__.model_fields.values()))
            alias = first_field_info.alias
            if alias:
                # Extract prefix from "prefix:localname" pattern
                # e.g., "configuration:devicename" → "configuration"
                parts = alias.split(":")
                if len(parts) >= 1:
                    return parts[0]

        # Fallback to lowercase class name
        return self.__class__.__name__.lower()

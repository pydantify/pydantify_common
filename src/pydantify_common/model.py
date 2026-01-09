from typing import ClassVar, List, get_origin, get_args, Annotated

from pydantic import BaseModel, Field
from lxml import etree


class PydantifyModel(BaseModel):
    pass


class XMLPydantifyModel(PydantifyModel):
    namespace: ClassVar[str]
    prefix: ClassVar[str]

    def model_dump_xml(self, element_name: str | None = None) -> etree.Element:
        # Wrapper logic: If a model has only one field which is another XMLPydantifyModel,
        # it acts as a transparent container.
        if (
            len(self.__class__.model_fields) == 1
            and isinstance(getattr(self, list(self.__class__.model_fields.keys())[0]), XMLPydantifyModel)
        ):
            single_field_name = list(self.__class__.model_fields.keys())[0]
            # Recursively call, passing down the element_name from parent, or using self.prefix as fallback.
            return getattr(self, single_field_name).model_dump_xml(element_name=element_name or self.prefix)

        # Determine the name for the current element.
        current_element_local_name = element_name if element_name else self.prefix
        current_element_namespace = self.namespace

        # Create the element, setting its default namespace. This is the key.
        element = etree.Element(
            current_element_local_name,
            nsmap={None: current_element_namespace}
        )

        for field_name, field_info in self.__class__.model_fields.items():
            field_value = getattr(self, field_name)

            if field_value is None:
                continue

            xml_local_tag_name = field_info.alias.split(":")[-1] if field_info.alias else field_name

            if isinstance(field_value, XMLPydantifyModel):
                # Recursively call for nested models.
                nested_element = field_value.model_dump_xml(element_name=xml_local_tag_name)
                element.append(nested_element)
            elif isinstance(field_value, list):
                # Correctly handle Annotated[List[...]]
                field_type = field_info.annotation
                if get_origin(field_type) is Annotated:
                    field_type = get_args(field_type)[0] # Get the inner type, e.g., List[InterfacesListEntry]

                origin = get_origin(field_type)
                args = get_args(field_type)

                if origin is list and args and hasattr(args[0], 'model_dump_xml'):
                    for item in field_value:
                        if hasattr(item, 'model_dump_xml'):
                            # Recursively call for each item in the list.
                            list_item_element = item.model_dump_xml(element_name=xml_local_tag_name)
                            element.append(list_item_element)
                else: # List of primitive types
                    if field_value:
                        for item in field_value:
                            # Primitives inherit the parent's default namespace.
                            sub_element = etree.SubElement(element, xml_local_tag_name)
                            sub_element.text = str(item)
            else:
                # Handle single primitive types. They inherit the parent's default namespace.
                sub_element = etree.SubElement(element, xml_local_tag_name)
                sub_element.text = str(field_value)

        return element
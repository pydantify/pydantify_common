from typing import ClassVar, Any, Dict, Optional, get_origin, get_args

from pydantic import BaseModel
from lxml import etree


class PydantifyModel(BaseModel):
    pass


class XMLPydantifyModel(PydantifyModel):
    namespace: ClassVar[str]
    prefix: ClassVar[str]

    def model_dump_xml(self) -> etree.Element:
        """
        Convert this Pydantic model instance to an lxml.etree.Element.
        
        Creates an XML element tree from the model, handling nested models 
        and managing namespaces appropriately.
        """
        # Use the first field to create the root element
        return self._create_root_element()
    
    def _create_root_element(self) -> etree.Element:
        """Create the root XML element for this model."""
        fields_items = list(self.__class__.model_fields.items())
        
        if not fields_items:
            return etree.Element("empty")
        
        # Use the first field as the root element
        first_field_name, first_field_info = fields_items[0]
        first_value = getattr(self, first_field_name)
        
        if first_value is None:
            return etree.Element("empty")
        
        # Extract tag name from alias
        field_alias = first_field_info.alias if first_field_info.alias else first_field_name
        tag_name = field_alias.split(':')[-1] if ':' in field_alias else field_alias
        
        # Create the element with proper namespace
        if isinstance(first_value, XMLPydantifyModel):
            nested_ns = first_value.namespace if hasattr(first_value, 'namespace') else None
            nested_prefix = first_value.prefix if hasattr(first_value, 'prefix') else None
            
            # Create element with namespace map for default namespace
            nsmap = {None: nested_ns} if nested_ns else None
            element = etree.Element(tag_name, nsmap=nsmap)
            
            # Add children from the nested model
            self._add_model_children(element, first_value)
        else:
            element = etree.Element(tag_name)
            element.text = str(first_value)
        
        return element
    
    def _add_model_children(self, parent_element: etree.Element, model: 'XMLPydantifyModel') -> None:
        """Add all fields of a model as child elements."""
        parent_ns = model.namespace if hasattr(model, 'namespace') else None
        
        for field_name, field_info in model.__class__.model_fields.items():
            value = getattr(model, field_name)
            
            # Skip None values
            if value is None:
                continue
            
            # Get the field's alias if it exists
            field_alias = field_info.alias if field_info.alias else field_name
            
            # Extract tag name from alias
            tag_name = field_alias.split(':')[-1] if ':' in field_alias else field_alias
            
            # Handle list fields
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, XMLPydantifyModel):
                        # Create element with item's namespace
                        item_ns = item.namespace if hasattr(item, 'namespace') else None
                        
                        # Only add nsmap if namespace differs from parent
                        if item_ns and item_ns != parent_ns:
                            nsmap = {None: item_ns}
                            child_element = etree.SubElement(parent_element, tag_name, nsmap=nsmap)
                        else:
                            child_element = etree.SubElement(parent_element, tag_name)
                        
                        # Recursively add the nested model's children
                        self._add_model_children(child_element, item)
                    else:
                        # Handle primitive list items
                        child_element = etree.SubElement(parent_element, tag_name)
                        child_element.text = str(item)
            elif isinstance(value, XMLPydantifyModel):
                # Create element for nested model
                value_ns = value.namespace if hasattr(value, 'namespace') else None
                
                # Only add nsmap if namespace differs from parent
                if value_ns and value_ns != parent_ns:
                    nsmap = {None: value_ns}
                    child_element = etree.SubElement(parent_element, tag_name, nsmap=nsmap)
                else:
                    child_element = etree.SubElement(parent_element, tag_name)
                
                # Recursively add the nested model's children
                self._add_model_children(child_element, value)
            else:
                # Handle primitive values
                child_element = etree.SubElement(parent_element, tag_name)
                child_element.text = str(value)

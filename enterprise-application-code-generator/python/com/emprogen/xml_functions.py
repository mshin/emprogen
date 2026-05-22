#!/usr/bin/env python3
import xml.etree.ElementTree as et
from typing import List, Dict


def remove_xml_element(
    file_path: str,
    namespace: str,
    path_to_element_list: List[str],
    element_identifier_dict: Dict[str, str]
) -> None:
    """
    Removes an XML element identified by a path and identifier values.

    Args:
        file_path: Path to the XML file.
        namespace: XML namespace URI.
        path_to_element_list: List of element names leading to the target element.
        element_identifier_dict: Dict of {element names:their identifying values}.
    Notes:
        path_to_element_list does not contain the element identifier elements,
        only everything up to that point.
    """
    et.register_namespace('', namespace)

    parser = et.XMLParser(target=et.TreeBuilder(insert_comments=True))
    tree = et.parse(file_path, parser) #ElementTree
    root = tree.getroot() #Element
    ns = {'x': namespace}

    # Build XPath to the parent of the target element
    xpath = '.'
    for e in path_to_element_list:
        xpath += '/x:' + e
    for e, value in element_identifier_dict.items():
        xpath += f"/x:{e}[.='{value}']/.."

    elem = root.find(xpath, ns)
    if elem is None:
        raise ValueError(f"Element not found for path: {xpath}")

    parent_elem = root.find(xpath + '/..', ns)
    if parent_elem is None:
        raise ValueError(f"Parent element not found for path: {parent_path}")

    parent_elem.remove(elem)

    et.indent(tree, space="    ", level=0)
    tree.write(file_path, encoding="utf-8", xml_declaration=True)


def add_xml_element(
    file_path: str,
    namespace: str,
    path_to_element_list: List[str],
    element_to_add_dict: Dict[str, str]
) -> None:
    """
    Adds new XML subelements under a specified parent element.

    Args:
        file_path: Path to the XML file.
        namespace: XML namespace URI.
        path_to_element_list: List of element names leading to the parent.
        element_to_add_dict: Dict of {tag names:their text values} to add.
    Notes:
        path_to_element_list does not contain the element identifier elements,
        only everything up to that point.
    """
    parser = et.XMLParser(target=et.TreeBuilder(insert_comments=True))
    tree = et.parse(file_path, parser) #ElementTree
    root = tree.getroot() #Element
    ns = {'x': namespace}

    path_to_element = '.'
    for e in path_to_element_list:
        path_to_element += f'/x:{e}'

    parent_elem = root.find(path_to_element, ns)
    if parent_elem is not None:
        for e, value in element_to_add_dict.items():
            et.SubElement(parent_elem, e).text = value

        et.indent(tree, space="    ", level=0)
        et.register_namespace('', namespace)
        tree.write(file_path)

#!/usr/bin/env python3
import re
from typing import Optional


def get_property(prop: str, file_path: str) -> Optional[str]:
    """
    Retrieves the value of a property from a file with 'key=value' lines.

    Args:
        prop: The property name to search for.
        file_path: Path to the file.

    Returns:
        The property value as a string, or None if not found.
    Notes:
        Not efficient for getting multiple properties. Ok for getting 1 property.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith(f"{prop}="):
                return line.split('=', 1)[1].strip()
    return None


def load_properties_as_dict(properties_file_url: str) -> dict:
    """
    Given a url to .properties file, return the key=value items in a dict.

    Args:
        properties_file_url: Path to the .properties file.

    Returns:
        The property values as a dict.
    """
    properties_dict = {}

    # key is ([^=]+) aka one or more characters starting at the beginning of line that are not equals sign.
    # value is (.*) aka any characters after the first equals sign until the end of the line.
    pattern = re.compile('^([^=]+)=(.*)$')

    with open(properties_file_url, encoding='utf-8') as f:
        key_value_list = f.read().split('\n')

        for line in key_value_list:
            if not line: continue
            if line and line[0] == '#':
                print("got rid of comment: " + str(line))
                continue

            match = re.match(pattern, line)
            if match:
                key = match.group(1).strip()
                value = match.group(2).strip()
                properties_dict[key] = value
            else:
                e = Exception('Property was not in format k=v.')
                print('file: ' + str(properties_file_url) + '| prop: ' + str(p))
                raise e
    print('properties_dict: ' + str(properties_dict))
    return properties_dict

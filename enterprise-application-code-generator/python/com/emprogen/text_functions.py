#!/usr/bin/env python3
import re


def lower_first(s: str) -> str:
    """
    Return the string with its first character lowercased.
    """
    if not s:
        return s
    return s[0].lower() + s[1:]


CTS_PATTERN = re.compile(r'(?<!^)(?=[A-Z])')

def camel_to_snake(camel_string: str) -> str:
    """
    Convert a camelCase or PascalCase string to snake_case.
    """
    return CTS_PATTERN.sub('_', camel_string).lower()


def to_camel(s: str, is_lower_first: bool = True) -> str:
    """
    Converts snake_case, kebab-case, and space case to camelCase.
    """
    if not re.search(r'[_\- ]', s):
        if is_lower_first and s:
            s = s[0].lower() + s[1:]
        return s
    word_list = filter(None, re.split(r'[_\- ]', s))
    s = ''.join(word.title() for word in word_list)
    if is_lower_first and s:
        s = s[0].lower() + s[1:]
    return s


def clean_text(text: str) -> str:
    """
    Cleans up text by removing carriage returns, joining hyphenated line breaks,
    replacing newlines with spaces, and stripping leading/trailing whitespace.

    Args:
        text: The input string to clean.

    Returns:
        The cleaned string.
    """
    # Currently useful for cleaning up descriptions in openapi specs.
    return text.replace('\r', '').replace('-\n', '-').replace('\n', ' ').strip()

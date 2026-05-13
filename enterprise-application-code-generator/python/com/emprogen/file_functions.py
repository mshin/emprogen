#!/usr/bin/env python3
import re
import os
import pathlib
import shutil
from typing import Optional, List, Dict


def copy_file(src: str, dst: str) -> None:
    """
    Copy a file from src to dst, creating the destination directory if needed.
    """
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)


def make_file(path: str, filename: str, *, file_content: Optional[str] = None) -> None:
    """
    Create a file at the specified path with optional content.
    Ensures the directory exists.
    """
    full_path = os.path.join(path, filename)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w') as f:
        if file_content is not None:
            f.write(file_content)


def get_file_path(file_path: str) -> str:
    """
    Return the absolute path to the directory containing the given file.
    __file__
    """
    return str(pathlib.Path(file_path).parent.resolve())


def replace_file_contents(content: str, file_path: str) -> None:
    """
    Replace the contents of the file at file_path with the given content.
    """
    with open(file_path, 'w') as f:
        f.write(content)


def delete_file(path: str):
    """
    Delete the file at the given path if it exists.
    """
    print(f"Deleting file {path}...")
    pathlib.Path(path).unlink(missing_ok=True)


def delete_directory(path: str) -> None:
    """
    Delete the directory at the given path if it exists.
    """
    print(f"Deleting directory {path}...")
    shutil.rmtree(pathlib.Path(path), ignore_errors=True)


def replace_text_in_file_multi(search_to_replace: Dict[str, str], file_path: str, *, count: int = 0) -> None:
    """
    Replace multiple patterns in a file with their corresponding replacements.

    Args:
        search_to_replace: Dictionary mapping search patterns to replacement strings.
        file_path: Path to the file to modify.
        count: Maximum number of pattern occurrences to replace for each pattern (0 = replace all).
    """
    with open(file_path, 'r+', encoding='utf-8') as f:
        # Opening the file in read and write mode
        content = f.read()
        # Replacing the pattern with the string in the file data for each item in the dict
        for search_text, replace_text in search_to_replace.items():
            content = re.sub(search_text, replace_text, content, count=count)
        # Setting the position to the top of the page to insert data
        f.seek(0)
        f.write(content)
        # Delete the current content of the file before writing.
        f.truncate()


def replace_text_in_file(
    search_text: str,
    replace_text: str,
    file_path: str,
    *,
    count: int = 0
) -> None:
    """
    Replace occurrences of a regex pattern in a file with the given replacement text.

    Args:
        search_text: Regex pattern to search for.
        replace_text: Replacement string.
        file_path: Path to the file to modify.
        count: Maximum number of pattern occurrences to replace (0 = replace all).
    """
    replace_text_in_file_multi({search_text: replace_text}, file_path, count=count)


def get_in_file(regex_find: str, file_path: str) -> Optional[str]:
    """
    Searches for the first occurrence of a regex pattern in a file.

    Args:
        regex_find: The regex pattern to search for.
        file_path: Path to the file to search.

    Returns:
        The matched string if found, otherwise None.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        file_string = f.read()
        match = re.search(regex_find, file_string, re.MULTILINE)
        if match:
            return match.group()
    return None


def get_files_from_path(dir_path: str) -> List[str]:
    """
    Recursively collects all file paths from the given directory.

    Args:
        dir_path: Path to the directory.

    Returns:
        A list of absolute file paths found within the directory.
    """
    print(f'dirPath: {dir_path}')
    file_list = []
    for root, _, files in os.walk(dir_path):
        for name in files:
            file_list.append(os.path.join(root, name))
    return file_list

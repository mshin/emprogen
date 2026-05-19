#!/usr/bin/env python3
import os
import re
import shutil
from pathlib import Path
from typing import Optional, List, Dict


def copy_file(src: str | Path, dst: str | Path) -> None:
    """
    Copy a file from src to dst, creating the destination directory if needed.
    """
    src_path = Path(src)
    dst_path = Path(dst)
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_path, dst_path)


def make_file(file: str | Path, *, file_content: Optional[str] = None) -> None:
    """
    Create a file at the specified path with optional content.
    Ensures the directory exists.
    """
    file_path = Path(file)
    os.makedirs(file_path.parent, exist_ok=True)
    with file_path.open('w') as f:
        if file_content is not None:
            f.write(file_content)

# TODO deprecated
# def make_file(path: str, filename: str, *, file_content: Optional[str] = None) -> None:
#     """
#     Create a file at the specified path with optional content.
#     Ensures the directory exists.
#     """
#     full_path = os.path.join(path, filename)
#     make_file(full_path, file_content=file_content)


def get_file_path(file_path: str | Path) -> Path:
    """
    Return the absolute path to the directory containing the given file.
    Pass __file__ into this method.
    """
    return Path(file_path).parent.resolve()


def replace_file_contents(content: str, file_path: str | Path) -> None:
    """
    Replace the contents of the file at file_path with the given content.
    """
    path_obj = Path(file_path)
    with path_obj.open('w') as f:
        f.write(content)


def delete_file(path: str | Path) -> None:
    """
    Delete the file at the given path if it exists.
    """
    path_obj = Path(path)
    print(f"Deleting file {path_obj}...")
    path_obj.unlink(missing_ok=True)


def delete_directory(path: str | Path) -> None:
    """
    Delete the directory at the given path if it exists.
    """
    path_obj = Path(path)
    print(f"Deleting directory {path_obj}...")
    shutil.rmtree(path_obj, ignore_errors=True)


def replace_text_in_file_multi(
    search_to_replace: Dict[str, str],
    file_path: str | Path,
    *,
    count: int = 0
) -> None:
    """
    Replace multiple patterns in a file with their corresponding replacements.

    Args:
        search_to_replace: Dictionary mapping search patterns to replacement strings.
        file_path: Path to the file to modify.
        count: Maximum number of pattern occurrences to replace for each pattern (0 = replace all).
    """
    path_obj = Path(file_path)
    content = path_obj.read_text(encoding='utf-8')
    for search_text, replace_text in search_to_replace.items():
        content = re.sub(search_text, replace_text, content, count=count)
    path_obj.write_text(content, encoding='utf-8')


def replace_text_in_file(
    search_text: str,
    replace_text: str,
    file_path: str | Path,
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


def get_in_file(regex_find: str, file_path: str | Path) -> Optional[str]:
    """
    Searches for the first occurrence of a regex pattern in a file.

    Args:
        regex_find: The regex pattern to search for.
        file_path: Path to the file to search.

    Returns:
        The matched string if found, otherwise None.
    """
    path_obj = Path(file_path)
    file_string = path_obj.read_text(encoding='utf-8')
    match = re.search(regex_find, file_string, re.MULTILINE)
    if match:
        return match.group()
    return None


def get_files_from_path(dir_path: str | Path) -> List[str]:
    """
    Recursively collects all file paths from the given directory.

    Args:
        dir_path: Path to the directory.

    Returns:
        A list of absolute file paths found within the directory.
    """
    dir_path = str(dir_path)
    print(f'dirPath: {dir_path}')
    file_list = []
    for root, _, files in os.walk(dir_path):
        for name in files:
            file_list.append(os.path.join(root, name))
    return file_list


def get_files_list_by_extension_dict(dir_path: str | Path) -> dict:
    """
    Return a dict mapping file extensions to lists of file paths.
    """
    ext_to_file_list_dict = {}
    files_list = get_files_from_path(dir_path)  # get all files in the project path
    for file_path in files_list:
        ext = os.path.splitext(file_path)[1]  # get file extension
        if ext not in ext_to_file_list_dict:
            ext_to_file_list_dict[ext] = []
        ext_to_file_list_dict[ext].append(file_path)
    ext_to_file_list_dict['.*'] = files_list  # wildcard for all files
    print('extToFileListDict:', ext_to_file_list_dict)
    return ext_to_file_list_dict
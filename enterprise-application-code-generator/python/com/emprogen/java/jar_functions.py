#!/usr/bin/env python3
import os
import zipfile
from typing import Optional, List

import com.emprogen.subprocess_functions as spf


def get_files_from_jar(
    jar_path: str,
    *,
    exclude_folders: bool = True,
    extension_filter: Optional[str] = None
) -> List[str]:
    """
    Returns a list of files from a JAR file, optionally excluding folders and filtering by extension.

    Args:
        jar_path: Path to the JAR file.
        exclude_folders: If True, exclude folder entries.
        extension_filter: If set, only include files with this extension.

    Returns:
        List of file paths in the JAR.
    """
    files_from_jar = []
    with zipfile.ZipFile(jar_path, 'r') as jar:
        for file in jar.namelist():
            files_from_jar.append(file)
    if exclude_folders:
        files_from_jar = [file for file in files_from_jar if not file.endswith('/')]
    if extension_filter:
        files_from_jar = [file for file in files_from_jar if file.endswith(extension_filter.strip())]
    return files_from_jar


def read_content_from_jar_class(jar_path: str, class_name: str) -> str:
    """
    Returns the output of running 'javap -v' on a class from a JAR file.

    Args:
        jar_path: Path to the JAR file.
        class_name: Fully qualified class name.

    Returns:
        Output from the javap command as a string.
    """
    print(f'pwd: {os.getcwd()}')
    return spf.run_subprocess_capture_output(['javap', '-v', '-cp', jar_path, class_name])

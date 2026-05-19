#!/usr/bin/env python3
import glob
import os
import yaml

import com.emprogen.file_functions as FILEF
# input yaml from descriptor file; basically a dict of licensePath to file extensions.

# input the set of all the project files and put them into a dict based on file extension. ext to file list.

# iterate over the licenses
#     get the text of the license
#     iterate over the file extensions
#         for each file of that file extension, prepend the license text to the file.


def prepend_licenses(yaml_dict: dict, project_path: str | Path, descriptor_path: str | Path) -> None:
    """
    Parse licenses from yaml and prepend them to project files.
    """
    license_list = yaml_dict.get('license', [])  # get the list of licenses from yaml
    print('licenseList:', license_list)
    license_to_ext_dict = {}
    for license_item in license_list:
        k = license_item.get('licenseFile', None)  # license file path
        v = license_item.get('fileTypes', None)    # list of file extensions
        if k is not None and v is not None:
            license_to_ext_dict[k] = v
    print('licenseToExtDict:', license_to_ext_dict)
    process_licenses(license_to_ext_dict, project_path, descriptor_path)


def process_licenses(license_to_ext_dict: dict, dir_path: str | Path, descriptor_path: str | Path) -> None:
    """
    For each license, prepend its text to all files matching its extensions.
    """
    descriptor_path_str = str(descriptor_path)
    # get the set of all the project files and put them into a dict based on file extension
    ext_to_file_list_dict = FILEF.get_files_list_by_extension_dict(dir_path)

    print('pwd:', os.getcwd())
    # iterate over the licenses
    for license_path, file_ext_list in license_to_ext_dict.items():
        # get the text of the license
        with open(os.path.join(descriptor_path_str, license_path), 'r') as f:
            print(f'descriptorPath: {descriptor_path_str}')
            license_text = f.read()

        # iterate over the file extensions
        for file_ext in file_ext_list:
            # for each file of that file extension, prepend the license text to the file
            for file_path in ext_to_file_list_dict.get(str(file_ext).strip(), []):
                prepend_license(file_path, license_text)


def prepend_license(file_path: str | Path, license_text: str) -> None:
    """
    Prepend the license text to the given file.
    """
    file_path_str = str(file_path)
    with open(file_path_str, 'r+') as f:
        content = f.read()
        f.seek(0)
        f.write(license_text + '\n' + content)
        f.truncate()

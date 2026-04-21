#!/usr/bin/env python3

import yaml
import glob
import os

# input yaml from descriptor file; basically a dict of licensePath to file extensions.

# input the set of all the project files and put them into a dict based on file extension. ext to file list.

# iterate over the licenses
    # get the text of the license
    # iterate over the file extensions
        # for each file of that file extension, prepend the license text to the file.

def prependLicenses(yaml: 'dict', projectPath: 'str', descriptorPath: 'str') -> None:
    licenseList = yaml.get('license', [])
    print('licenseList: ' + str(licenseList))
    licenseToExtDict = {}
    for license in licenseList:
        k = license.get('licenseFile', None)
        v = license.get('fileTypes', None)
        if k is not None and v is not None:
            licenseToExtDict[k] = v
    print('licenseToExtDict: ' + str(licenseToExtDict))
    processLicenses(licenseToExtDict, projectPath, descriptorPath)

def processLicenses(licenseToExtDict: 'dict', dirPath: 'str', descriptorPath: 'str') -> None:
    # get the set of all the project files and put them into a dict based on file extension. ext to file list.
    extToFileListDict = getFilesListByExtensionDict(dirPath)

    print('pwd: ' + str(os.getcwd()))
    # iterate over the licenses
    for licensePath, fileExtList in licenseToExtDict.items():
        # get the text of the license
        with open(descriptorPath + '/' + licensePath, 'r') as f:
            print('descriptorPath: ' + str(descriptorPath))
            licenseText = f.read()

        # iterate over the file extensions
        for fileExt in fileExtList:
            # for each file of that file extension, prepend the license text to the file.
            for filePath in extToFileListDict.get(fileExt, []):
                prependLicense(filePath, licenseText)

def prependLicense(filePath: 'str', licenseText: 'str') -> None:
    with open(filePath, 'r+') as f:
        content = f.read()
        f.truncate(0)
        f.seek(0)
        f.write(licenseText + '\n' + content)

def getFilesListByExtensionDict(dirPath: 'str') -> 'dict':
    # get all of the files in generated code so we can process them.
    extToFileListDict = {}
    files_list = getFilesList(dirPath)
    for filePath in files_list:
        ext = os.path.splitext(filePath)[1]
        if ext not in extToFileListDict:
            extToFileListDict[ext] = []
        extToFileListDict[ext].append(filePath)
    print('extToFileListDict: ' + str(extToFileListDict))
    return extToFileListDict

def getFilesList(dirPath: 'str') -> 'list':
    # get all of the files in generated code so we can process them.
    print('dirPath: ' + str(dirPath))
    file_list = []
    for root, dirs, files in os.walk(dirPath):
        for name in files:
            file_list.append(os.path.join(root, name))
    return file_list

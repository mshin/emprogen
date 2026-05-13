import re
import subprocess
import os
import xml.etree.ElementTree as ET
import glob
import pathlib
import shutil
import importlib
import zipfile
from deprecated import deprecated
from com.emprogen.java.maven.models import Gav
import com.emprogen.java.maven.java_maven_functions as jmf


def eclipse_formatter_validate(path_to_pom: 'str; path to project pom') -> None:
    validate = 'net.revelc.code.formatter:formatter-maven-plugin:2.23.0:validate'
    print('running maven plugin eclipse formatter:validate at path: ' + path_to_pom)

    opts = {'configFile': get_java_maven_path() + '/mshin_formatter_java.xml'}
    callMvnWithOptions(**opts, goal=validate, file=path_to_pom)


def eclipse_formatter(path_to_pom: 'str; path to project pom') -> None:
    formatter = 'net.revelc.code.formatter:formatter-maven-plugin:2.23.0:format'
    print(f'running maven plugin eclipse formatter:format at path: {path_to_pom}')

    opts = {'configFile': get_java_maven_path() + '/mshin_formatter_java.xml'}
    callMvnWithOptions(**opts, goal=formatter, file=path_to_pom)


def beautify_imports(path_to_pom: str) -> None:
    """
    Beautifies Java imports using the AndroMDA Maven plugin and removes carriage returns from Java files.

    Args:
        path_to_pom: Path to the project's pom.xml file.
    """
    beautify = 'org.andromda.maven.plugins:andromda-beautifier-plugin:3.4:beautify-imports'
    print(f'Beautifying imports at path: {path_to_pom}')
    callMvnWithOptions(goal=beautify, file=path_to_pom)

    # get all java files
    pom_path = str(pathlib.Path(path_to_pom).parent.resolve())
    print(f'pom_path: {pom_path}')
    java_files = glob.glob('**/*.java', root_dir=pom_path, recursive=True)
    print(f'java_files: {java_files}')

    # need to clean \r from all java files due to andromda beautifier
    print('Removing carriage return from files..')
    for java_file in java_files:
        file_path = pom_path / java_file
        with open(file_path, 'r+', encoding='utf-8') as f:
            data = f.read().replace('\r', '')
            f.seek(0)
            f.write(data)
            f.truncate()

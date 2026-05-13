#!/usr/bin/env python3

import os
import pathlib
import xml.etree.ElementTree as ET
import zipfile

from typing import Optional, List, Dict

import com.emprogen.file_functions as FILEF
import com.emprogen.subprocess_functions as SPF
import com.emprogen.xml_functions as XMLF
from com.emprogen.java.maven.models import Gav

POM_NAMESPACE = 'http://maven.apache.org/POM/4.0.0'


def get_java_maven_path() -> str:
    """
    Returns the absolute path to the directory containing this file.
    """
    return str(pathlib.Path(__file__).parent.resolve())


def get_model_path(gav: 'Gav') -> str:
    """
    Constructs the model path for a given GAV object.

    Args:
        gav: GAV object with group_id and artifact_id.

    Returns:
        The model path as a string.
    """
    group_path = gav.group_id.replace('.', os.sep)
    artifact_path = gav.artifact_id.replace('-', os.sep)
    return os.path.join(
        gav.artifact_id,
        'src', 'main', 'java',
        group_path,
        artifact_path
    )


def get_package(gav: 'Gav') -> str:
    """
    Returns the Java package name for the given GAV object.

    Args:
        gav: GAV object with group_id and artifact_id.

    Returns:
        The package name as a string.
    """
    artifact_part = gav.artifact_id.replace('-', '.')
    return f"{gav.group_id}.{artifact_part}"


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


def generate_maven_project(
    arch_gav: 'Gav',
    gen_gav: 'Gav',
    author: str = None,
    *,
    file: str = None,
    **options: dict
) -> None:
    """
    Generates a Maven project using the specified archetype and project GAVs.

    Args:
        arch_gav: Archetype GAV object.
        gen_gav: Project GAV object.
        author: Optional author name.
        file: Path to the pom.xml file.
        options: Additional Maven options.
    """
    pkg=get_package(gen_gav)
    opts=dict(options)
    opts['archetypeGroupId']=arch_gav.group_id
    opts['archetypeArtifactId']=arch_gav.artifact_id
    opts['archetypeVersion']=arch_gav.version
    opts['groupId']=gen_gav.group_id
    opts['artifactId']=gen_gav.artifact_id
    opts['package']=pkg
    if author:
        opts['author']=author
    if gen_gav.version:
        opts['version']=gen_gav.version

    call_mvn_with_options(**opts, file=file)


def call_mvn_with_options(*, goal: str = 'archetype:generate', file: str = None, **options):
    """
    Constructs and runs a Maven command with the given options.

    Args:
        goal: The Maven goal to execute.
        file: Optional path to the pom.xml file.
        options: Additional Maven options and -D properties.
    """
    call = 'mvn {} -B'.format(goal)
    mvn_options = options.pop('mvn_options', [])
    for mvn_option in mvn_options:
        call += ' ' + mvn_option
    if file:
        call +=' -f {}'.format(file)
    arg_list = call.split()
    for k, v in options.items():
        arg_str = '-D{key}={value}'.format(key=k, value=v)
        arg_list.append(arg_str)
    print(f'maven call: {arg_list}')
    SPF.run_subprocess(arg_list)


def add_dependency(pom_path: str, gav: Optional['Gav'] = None) -> None:
    """
    Adds a dependency to a Maven POM file based on the provided GAV.

    Args:
        pom_path: Path to the pom.xml file.
        gav: Gav object with group_id, artifact_id, and optional version.
    """
    if gav is None:
        gav = Gav(None, None, None)

    parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
    tree = ET.parse(pom_path, parser) #ElementTree
    root = tree.getroot() #Element
    ns = {'x': POM_NAMESPACE}
    dependencies_elem = root.find('./x:dependencies', ns)

    if dependencies_elem is None:
        dependencies_elem = ET.SubElement(root, 'dependencies')

    dep_elem = ET.Element('dependency')

    group_id_elem = ET.SubElement(dep_elem, 'groupId')
    group_id_elem.text = gav.group_id

    artifact_id_elem = ET.SubElement(dep_elem, 'artifactId')
    artifact_id_elem.text = gav.artifact_id

    if gav.version:
        version_elem = ET.SubElement(dep_elem, 'version')
        version_elem.text = gav.version

    dependencies_elem.append(dep_elem)

    ET.indent(tree, space="    ", level=0)
    ET.register_namespace('', ns['x'])
    tree.write(pom_path)


def remove_dependency(pom_path: str, gav: Optional['Gav'] = None) -> None:
    """
    Removes a dependency from a Maven POM file based on the provided GAV.

    Args:
        pom_path: Path to the pom.xml file.
        gav: Gav object with group_id, artifact_id, and optional version.
    """
    if gav is None:
        gav = Gav(None, None, None)

    parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
    tree = ET.parse(pom_path, parser) #ElementTree
    root = tree.getroot() #Element
    ns = {'x': POM_NAMESPACE}
    # ./project/dependencies/dependency/groupId[.='io.swagger']/../artifactId[.='swagger-annotations']/..
    # elem = root.find(r"./x:dependencies/x:dependency/x:groupId[.='io.swagger']/../x:artifactId/..", ns)
    xpath = (
        f"./x:dependencies/x:dependency/"
        f"x:groupId[.='{gav.group_id}']/../"
        f"x:artifactId[.='{gav.artifact_id}']/.."
    )
    if gav.version:
        xpath += f"/x:version[.='{gav.version}']/.."
    
    elem = root.find(xpath, ns)
    parent_elem = root.find('./x:dependencies', ns)
    if elem is not None and parent_elem is not None:
        parent_elem.remove(elem)

    ET.indent(tree, space="    ", level=0)
    ET.register_namespace('', ns['x'])
    tree.write(pom_path)


def remove_pom_properties(pom_path: str, properties_list: List[str]) -> None:
    """
    Removes specified properties from the properties section of a Maven POM file.

    Args:
        pom_path: Path to the pom.xml file.
        properties_list: List of property names to remove.
    """
    for prop in properties_list:
        XMLF.remove_xml_element(pom_path, POM_NAMESPACE, ['properties', prop], {})
        print(f'removed pom property {prop} in pom {pom_path}')


def add_pom_properties(pom_path: str, properties_dict: Dict[str, str]) -> None:
    """
    Adds properties to the properties section of a Maven POM file.

    Args:
        pom_path: Path to the pom.xml file.
        properties_dict: Dictionary of property names and values to add.
    """
    for prop, value in properties_dict.items():
        XMLF.add_xml_element(pom_path, POM_NAMESPACE, ['properties'], {prop: value})
        print(f'added pom property {prop} in pom {pom_path}')


def remove_pom_plugin(pom_path: str, gav: Optional['Gav'] = None) -> None:
    """
    Removes a plugin from the build/plugins section of a Maven POM file by artifactId.

    Args:
        pom_path: Path to the pom.xml file.
        gav: Gav object with artifact_id set; group_id is ignored because some plugins don't include them.
    """
    if gav is None:
        gav = Gav(None, None, None)

    XMLF.remove_xml_element(pom_path, POM_NAMESPACE, ['build', 'plugins', 'plugin'], {'artifactId': gav.artifact_id})
    print(f'removed pom plugin {gav} in pom {pom_path}')


def remove_pom_profile(pom_path: str, profile_id: str) -> None:
    """
    Removes a profile from the profiles section of a Maven POM file by profile id.

    Args:
        pom_path: Path to the pom.xml file.
        profile_id: The id of the profile to remove.
    """
    XMLF.remove_xml_element(pom_path, POM_NAMESPACE, ['profiles', 'profile'], {'id': profile_id})
    print(f'removed pom profile {profile_id} in pom {pom_path}')


def remove_pom_dependency_management(pom_path: str) -> None:
    """
    Removes the dependencyManagement section from a Maven POM file.

    Args:
        pom_path: Path to the pom.xml file.
    """
    XMLF.remove_xml_element(pom_path, POM_NAMESPACE, ['dependencyManagement'], {})
    print(f'removed dependencyManagement in pom {pom_path}')


def add_java_imports(imports: str, file_path: str) -> None:
    """
    Adds Java import statements to the specified file after the first line.

    Args:
        imports: The import statements to add.
        file_path: Path to the Java source file.
    """
    print(f'adding imports to file: {file_path}')
    search_text = '\n'
    FILEF.replace_text_in_file(search_text, '\n\n' + imports + '\n', file_path, count = 1)


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
    return SPF.run_subprocess_capture_output(['javap', '-v', '-cp', jar_path, class_name])


def gav_to_path(gav: str) -> str:
    """
    Converts a Maven GAV string to the absolute path of the corresponding JAR in the local Maven repository.

    Args:
        gav: Maven coordinates in the format 'group:artifact:version'.

    Returns:
        Absolute path to the JAR file.
    """
    group_id, artifact_id, version = gav.split(':')
    group_path = group_id.replace('.', '/')
    repo_base = os.path.expanduser('~/.m2/repository')
    jar_path = f'{repo_base}/{group_path}/{artifact_id}/{version}/{artifact_id}-{version}.jar'
    return os.path.abspath(jar_path)


print('loaded ' + __file__)

if __name__ == '__main__':
    # test code here
    #call_mvn_with_options(**{'A': 'a', 'B': 'b', 'C': 'c'}, goal='version')
    cwd=os.getcwd()
    print('cwd:' + cwd)
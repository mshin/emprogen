#!/usr/bin/env python3
import os
import pathlib
import xml.etree.ElementTree as et
from pathlib import Path
from typing import Optional, List, Dict

import com.emprogen.file_functions as filef
import com.emprogen.subprocess_functions as spf
import com.emprogen.xml_functions as xmlf
from com.emprogen.java.maven.models import Gav

POM_NAMESPACE = 'http://maven.apache.org/POM/4.0.0'


def get_java_maven_path() -> Path:
    """
    Returns the absolute path to the directory containing this file.
    """
    return Path(__file__).parent.resolve()


def get_model_path(gav: Gav) -> Path:
    """
    Constructs the model path for a given GAV object.

    Args:
        gav: GAV object with group_id and artifact_id.

    Returns:
        The model path as a string.
    """
    group_path = Path(*gav.group_id.split('.'))
    artifact_path = Path(*gav.artifact_id.split('-'))
    return Path(gav.artifact_id) / 'src' / 'main' / 'java' / group_path / artifact_path


def get_test_model_path(gav: Gav) -> Path:
    """
    Constructs the test model path for a given GAV object.

    Args:
        gav: GAV object with group_id and artifact_id.

    Returns:
        The test model path as a string.
    """
    group_path = Path(*gav.group_id.split('.'))
    artifact_path = Path(*gav.artifact_id.split('-'))
    return Path(gav.artifact_id) / 'src' / 'test' / 'java' / group_path / artifact_path


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


def generate_maven_project(
    arch_gav: 'Gav',
    gen_gav: 'Gav',
    author: str = None,
    *,
    file: str | Path = None,
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


def call_mvn_with_options(*, goal: str = 'archetype:generate', file: str | Path = None, **options):
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
        file_str = str(file)
        call +=' -f {}'.format(file_str)
    arg_list = call.split()
    for k, v in options.items():
        arg_str = '-D{key}={value}'.format(key=k, value=v)
        arg_list.append(arg_str)
    print(f'maven call: {arg_list}')
    spf.run_subprocess(arg_list)


def add_dependency(pom_path: str | Path, gav: Optional['Gav'] = None) -> None:
    """
    Adds a dependency to a Maven POM file based on the provided GAV.

    Args:
        pom_path: Path to the pom.xml file.
        gav: Gav object with group_id, artifact_id, and optional version.
    """
    if gav is None:
        gav = Gav(None, None, None)
    pom_path_str = str(pom_path)

    parser = et.XMLParser(target=et.TreeBuilder(insert_comments=True))
    tree = et.parse(pom_path_str, parser) #ElementTree
    root = tree.getroot() #Element
    ns = {'x': POM_NAMESPACE}
    dependencies_elem = root.find('./x:dependencies', ns)

    if dependencies_elem is None:
        dependencies_elem = et.SubElement(root, 'dependencies')

    dep_elem = et.Element('dependency')

    group_id_elem = et.SubElement(dep_elem, 'groupId')
    group_id_elem.text = gav.group_id

    artifact_id_elem = et.SubElement(dep_elem, 'artifactId')
    artifact_id_elem.text = gav.artifact_id

    if gav.version:
        version_elem = et.SubElement(dep_elem, 'version')
        version_elem.text = gav.version

    dependencies_elem.append(dep_elem)

    et.indent(tree, space="    ", level=0)
    et.register_namespace('', ns['x'])
    tree.write(pom_path_str)


def remove_dependency(pom_path: str | Path, gav: Optional['Gav'] = None) -> None:
    """
    Removes a dependency from a Maven POM file based on the provided GAV.

    Args:
        pom_path: Path to the pom.xml file.
        gav: Gav object with group_id, artifact_id, and optional version.
    """
    if gav is None:
        gav = Gav(None, None, None)
    pom_path_str = str(pom_path)

    parser = et.XMLParser(target=et.TreeBuilder(insert_comments=True))
    tree = et.parse(pom_path_str, parser) #ElementTree
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

    et.indent(tree, space="    ", level=0)
    et.register_namespace('', ns['x'])
    tree.write(pom_path_str)


def remove_pom_properties(pom_path: str | Path, properties_list: List[str]) -> None:
    """
    Removes specified properties from the properties section of a Maven POM file.

    Args:
        pom_path: Path to the pom.xml file.
        properties_list: List of property names to remove.
    """
    pom_path_str = str(pom_path)

    for prop in properties_list:
        try:
            xmlf.remove_xml_element(pom_path_str, POM_NAMESPACE, ['properties', prop], {})
            print(f'removed pom property {prop} in pom {pom_path_str}')
        except Exception as e:
            print(f'Could not remove property {prop} from pom {pom_path_str}: {e}')


def add_pom_properties(pom_path: str, properties_dict: Dict[str, str]) -> None:
    """
    Adds properties to the properties section of a Maven POM file.

    Args:
        pom_path: Path to the pom.xml file.
        properties_dict: Dictionary of property names and values to add.
    """
    pom_path_str = str(pom_path)

    for prop, value in properties_dict.items():
        xmlf.add_xml_element(pom_path_str, POM_NAMESPACE, ['properties'], {prop: value})
        print(f'added pom property {prop} in pom {pom_path_str}')


def remove_pom_plugin(pom_path: str | Path, gav: Optional['Gav'] = None) -> None:
    """
    Removes a plugin from the build/plugins section of a Maven POM file by artifactId.

    Args:
        pom_path: Path to the pom.xml file.
        gav: Gav object with artifact_id set; group_id is ignored because some plugins don't include them.
    """
    if gav is None:
        gav = Gav(None, None, None)
    pom_path_str = str(pom_path)

    try:
        xmlf.remove_xml_element(pom_path_str, POM_NAMESPACE, ['build', 'plugins', 'plugin'], {'artifactId': gav.artifact_id})
        print(f'removed pom plugin {gav} in pom {pom_path_str}')
    except Exception as e:
        print(f'Could not remove plugin {gav} from pom {pom_path_str}: {e}')


def remove_pom_profile(pom_path: str | Path, profile_id: str) -> None:
    """
    Removes a profile from the profiles section of a Maven POM file by profile id.

    Args:
        pom_path: Path to the pom.xml file.
        profile_id: The id of the profile to remove.
    """
    pom_path_str = str(pom_path)

    try:
        xmlf.remove_xml_element(pom_path_str, POM_NAMESPACE, ['profiles', 'profile'], {'id': profile_id})
        print(f'removed pom profile {profile_id} in pom {pom_path_str}')
    except Exception as e:
        print(f'Could not remove profile {profile_id} from pom {pom_path_str}: {e}')

def remove_pom_dependency_management(pom_path: str | Path) -> None:
    """
    Removes the dependencyManagement section from a Maven POM file.

    Args:
        pom_path: Path to the pom.xml file.
    """
    pom_path_str = str(pom_path)

    try:
        xmlf.remove_xml_element(pom_path_str, POM_NAMESPACE, ['dependencyManagement'], {})
        print(f'removed dependencyManagement in pom {pom_path_str}')
    except Exception as e:
        print(f'Could not remove dependencyManagement from pom {pom_path_str}: {e}')

def add_java_imports(imports: str, file_path: str | Path) -> None:
    """
    Adds Java import statements to the specified file after the first line.

    Args:
        imports: The import statements to add.
        file_path: Path to the Java source file.
    """
    file_path_str = str(file_path)

    print(f'adding imports to file: {file_path_str}')
    search_text = '\n'
    filef.replace_text_in_file(search_text, '\n\n' + imports + '\n', file_path_str, count = 1)


def gav_to_jar_local_abs_path_str(gav: str | Gav) -> str:
    """
    Converts a Maven GAV string to the absolute path of the corresponding JAR in the local Maven repository.
    Old gav_to_path method.

    Args:
        gav: Maven coordinates in the format 'group:artifact:version'.

    Returns:
        Absolute path to the JAR file.
    """
    gav_str = str(gav)
    group_id, artifact_id, version = gav_str.split(':')
    group_path = Path(*group_id.split('.'))
    repo_base = Path.home() / '.m2' / 'repository'
    mvn_jar_name = f'{artifact_id}-{version}.jar'
    jar_path = repo_base / group_path / artifact_id / version / mvn_jar_name
    return str(jar_path.resolve())

print('loaded ' + __file__)

if __name__ == '__main__':
    # test code here
    #call_mvn_with_options(**{'A': 'a', 'B': 'b', 'C': 'c'}, goal='version')
    cwd=os.getcwd()
    print('cwd:' + cwd)

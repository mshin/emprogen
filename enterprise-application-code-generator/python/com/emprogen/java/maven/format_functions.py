#!/usr/bin/env python3
import glob
import pathlib

# Have to import like this due to dashes in the script name.
rgjf = importlib.import_module("com.emprogen.java.run-google-java-format")

import com.emprogen.java.maven.java_maven_functions as JMF

FORMATTER_MAVEN_PLUGIN_GAV = 'net.revelc.code.formatter:formatter-maven-plugin:2.23.0'
ANDROMEDA_BEAUTIFIER_PLUGIN_GAV = 'org.andromda.maven.plugins:andromda-beautifier-plugin:3.4'

def eclipse_formatter_validate(path_to_pom: str) -> None:
    """
    Validates Java formatting using the Eclipse formatter Maven plugin.
    """
    validate = f"{FORMATTER_MAVEN_PLUGIN_GAV}:validate"
    print('running maven plugin eclipse formatter:validate at path: ' + path_to_pom)

    opts = {'configFile': str(pathlib.Path(JMF.get_java_maven_path()) / 'mshin_formatter_java.xml')}
    JMF.call_mvn_with_options(**opts, goal=validate, file=path_to_pom)


def eclipse_formatter(path_to_pom: str) -> None:
    formatter = f"{FORMATTER_MAVEN_PLUGIN_GAV}:format"
    print(f'running maven plugin eclipse formatter:format at path: {path_to_pom}')

    opts = {'configFile': str(pathlib.Path(JMF.get_java_maven_path()) / 'mshin_formatter_java.xml')}
    JMF.call_mvn_with_options(**opts, goal=formatter, file=path_to_pom)


def beautify_imports(path_to_pom: str) -> None:
    """
    Beautifies Java imports using the AndroMDA Maven plugin and removes carriage returns from Java files.

    Args:
        path_to_pom: Path to the project's pom.xml file.
    """
    beautify = f"{ANDROMEDA_BEAUTIFIER_PLUGIN_GAV}:beautify-imports"
    print(f'Beautifying imports at path: {path_to_pom}')
    JMF.call_mvn_with_options(goal=beautify, file=path_to_pom)

    # get all java files
    pom_path = str(pathlib.Path(path_to_pom).parent.resolve())
    print(f'pom_path: {pom_path}')
    java_files = glob.glob('**/*.java', root_dir=pom_path, recursive=True)
    print(f'java_files: {java_files}')

    # need to clean \r from all java files due to andromda beautifier
    print('Removing carriage return from files..')
    for java_file in java_files:
        file_path = pathlib.Path(pom_path) / java_file
        try:
            with open(file_path, 'r+', encoding='utf-8') as f:
                data = f.read().replace('\r', '')
                f.seek(0)
                f.write(data)
                f.truncate()
        except Exception as e:
            logging.error(f"Error processing {file_path}: {e}")


# google java format
def gjf(java_files: list) -> None:
    for java_file in java_files:
        rgjf.run(java_file)
    print('finished formatting ' + str(len(java_files)) + ' java files.')


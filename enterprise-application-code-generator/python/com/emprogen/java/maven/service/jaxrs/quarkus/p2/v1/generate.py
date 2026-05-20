import glob
import re
from pathlib import Path

import com.emprogen.file_functions as filef
import com.emprogen.java.jar_functions as jarf
import com.emprogen.java.maven.format_functions as formatf
import com.emprogen.java.maven.java_maven_functions as jmf
import com.emprogen.java.maven.yaml_functions as yf
import com.emprogen.java.maven.service.jaxrs.service_impl_functions as sif
import com.emprogen.prepend_license as pl
import com.emprogen.subprocess_functions as spf
from com.emprogen.java.maven.models import Gav


def generate(
    descriptor: dict,
    archetype_gav: Gav = Gav(
        'com.emprogen',
        'service-jaxrs-quarkus-p1-archetype',
        '0.0.2'
    ),
    *,
    files_path: str | Path = None,
    java_version: str = '17',
    **kwargs
) -> None:
    print('in service.jaxrs.quarkus.p2.v1.generate.py')
    print(f'java_version: {java_version}')

    # define maven archetype used for this generator within script.
    arch_gav = archetype_gav

    # the maven groupId:artifactId:version for the code module to be generated
    proj_gav = yf.get_generated_project_gav(descriptor)

    # the gav for the maven module containing the jaxrs Interface from which the service will be generated.
    service_interface_gav_string = descriptor['serviceInterfaceGav']
    api_gav = yf.get_gav(service_interface_gav_string)

    # the directory of the maven pom for the generated code. Usually at the directory root of project.
    proj_pom_path = Path(proj_gav.artifact_id) / 'pom.xml'

    author = descriptor.get('author', sif.AUTHOR_DEFAULT)

    # Geneate Maven project.
    # Set Maven archetype generation options.
    opts = {}
    opts['api_groupId'] = api_gav.group_id
    opts['api_artifactId'] = api_gav.artifact_id
    opts['api_version'] = api_gav.version
    opts['jaxrs_service_interface'] = 'Template'
    opts['jaxrs_service_package'] = 'does.not.matter'
    print(f'service opts: {opts}')

    #Enable mvn opts from command line
    mvn_options = spf.capture_contextual_command_line_options(kwargs.get('command_args', []), 'mvn')
    mvn_opts = {'mvn_options': mvn_options}
    opts.update(mvn_opts)

    print(f'mvn_options: {mvn_options}')
    print(f'opts: {opts}')

    # Actually generate the maven project
    jmf.generate_maven_project(arch_gav, proj_gav, author, **opts)
    print(f'Generated maven project with archetype: {arch_gav} and projGav: {proj_gav}')

    # get the java files, then winnow to ApiDefinition files.
    api_definition_files = []

    # get the gav from the serviceInterfaceGav (apiGav) and load the jar.
    # return a list of java class files in the jar that match the apiGav.
    api_gav_path = jmf.gav_to_jar_local_abs_path_str(api_gav)
    api_gav_class_files = jarf.get_files_from_jar(api_gav_path, extension_filter='.class')
    api_gav_class_file_contents = {}
    print(f'api_gav_class_files: {api_gav_class_files}')

    # Create a dictionary mapping from the java class name to the content of the class file for each java class file in the apiGav jar.
    for api_gav_class_file in api_gav_class_files:
        java_class_name = api_gav_class_file.replace('/', '.').replace('.class', '')
        print(f'java_class_name: {java_class_name}')
        content_from_jar_class = jarf.read_content_from_jar_class(api_gav_path, java_class_name)
        print(f'content_from_jar_class: {content_from_jar_class}')
        api_gav_class_file_contents[java_class_name] = content_from_jar_class
    #print(f'api_gav_class_file_contents: {api_gav_class_file_contents}')

    # Iterate over the java class file contents and find the ones that are ApiDefinition files.
    for class_name, class_file_content in api_gav_class_file_contents.items():
        print(f'Checking if class is API definition: {class_name}')
        if sif.is_class_file_an_api_definition(class_file_content):
            print(f'Found API definition: {class_name}')
            api_definition_files.append(class_name)

    print(f'api_definition_files: {api_definition_files}')

    # process the API definition files to generate the service Impl and service classes.
    service_implementation_classpath = sif.process_api_interfaces(api_gav, proj_gav, api_definition_files, author=author)

    # add addtl dependencies to the pom.
    # if no items in optional dependencyGav, default {} for null safety
    for dependency in descriptor.get('dependencyGav', {}):
        print(f'adding dependency to pom: {dependency}')
        jmf.add_dependency(proj_pom_path, yf.get_gav(dependency))

    # set java version to java_version
    maven_compiler_source = 'maven.compiler.source'
    maven_compiler_target = 'maven.compiler.target'
    jmf.remove_pom_properties(proj_pom_path, [maven_compiler_source, maven_compiler_target])
    jmf.add_pom_properties(proj_pom_path, {maven_compiler_source: java_version, maven_compiler_target: java_version})

    # set jaxrs package and java version based on the openapi3 module
    if None != re.search('javax.ws.rs.javax.ws.rs-api', service_implementation_classpath):
        print('Using javax in API definition module. Reducing Quarkus version in impl module to use javax instad of jakarta code packages. Reducing java version to 8.')
        # Fix java imports
        java_files = filef.get_files_list_by_extension_dict(Path(proj_gav.artifact_id) / 'src').get('.java', [])
        for java_file in java_files:
            filef.replace_text_in_file('import jakarta.', 'import javax.', java_file)
        # Reduce Quarkus version
        jmf.remove_pom_properties(proj_pom_path, ['version.quarkus'])
        jmf.add_pom_properties(proj_pom_path, {'version.quarkus': '2.16.8.Final'})

        # Reduce Java version to 8
        jmf.remove_pom_properties(proj_pom_path, [maven_compiler_source, maven_compiler_target])
        jmf.add_pom_properties(proj_pom_path, {maven_compiler_source: '8', maven_compiler_target: '8'})

        # Reduce rest impl library from quarkus-rest-jackson to quarkus-resteasy-reactive-jackson.
        jmf.remove_dependency(proj_pom_path, Gav('io.quarkus', 'quarkus-rest-jackson', None))
        jmf.remove_dependency(proj_pom_path, Gav('io.quarkus', 'quarkus-resteasy-reactive-jackson', None))
        jmf.add_dependency(proj_pom_path, Gav('io.quarkus', 'quarkus-resteasy-reactive-jackson', None))

    elif None != re.search('jakarta.ws.rs.jakarta.ws.rs-api', service_implementation_classpath):
        print('Using jakarta code packages in API definition module.')
    else:
        print('Did not find javax or jakarta code packages in API definition module.')

    # update imports
    formatf.beautify_imports(proj_pom_path)

    # add licenses to files
    pl.prepend_licenses(descriptor, proj_gav.artifact_id, files_path)

    # verify it compiles
    jmf.call_mvn_with_options(**mvn_opts, goal='clean install', file=proj_pom_path)
    jmf.call_mvn_with_options(**mvn_opts, goal='clean', file=proj_pom_path)

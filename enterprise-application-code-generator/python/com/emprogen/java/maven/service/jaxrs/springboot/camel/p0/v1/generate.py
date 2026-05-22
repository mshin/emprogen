#!/usr/bin/env python3
import re
from pathlib import Path

import com.emprogen.file_functions as filef
import com.emprogen.java.maven.format_functions as formatf
import com.emprogen.java.maven.java_maven_functions as jmf
import com.emprogen.java.maven.yaml_functions as yf
import com.emprogen.java.maven.field_functions as ff
import com.emprogen.prepend_license as pl
import com.emprogen.properties_functions as propf
import com.emprogen.subprocess_functions as spf
from com.emprogen.java.maven.models import Gav

SCRIPT_VERSION = 'com.emprogen.java.maven.service.jaxrs.springboot.camel.p0.v1.generate.py'

# TODO change name of generated class from Bean to Impl
# TODO enable generation for interfaces with multiple definition class files
def generate(
    descriptor: dict,
    archetype_gav: Gav = Gav(
        'com.emprogen',
        'service-jaxrs-springboot-camel-p0-archetype',
        '0.0.1'
    ),
    *,
    files_path: str = None,
    **kwargs
) -> None:
    print(f'in {SCRIPT_VERSION}')
    # Do all 1 time loads and calculations up front.

    # define maven archetype used for this generator within script.
    arch_gav = archetype_gav

    # the maven groupId:artifactId:version for the code module to be generated
    proj_gav = yf.get_generated_project_gav(descriptor)

    # the gav for the maven module containing the jaxrs Interface from which the service will be generated.
    service_interface_gav_string = descriptor['serviceInterfaceGav']
    api_gav = yf.get_gav(service_interface_gav_string)

    # the java package for the project to be generated.
    generated_package = jmf.get_package(proj_gav)

    # the directory of the maven pom for the generated code. Usually at the directory root of project.
    proj_path = Path(proj_gav.artifact_id)
    proj_pom_path = proj_path / 'pom.xml'
    # the directory of the java code.
    model_path = jmf.get_model_path(proj_gav)

    # the package.Classname for the jaxrs Interface from which the service will be generatd.
    service_interface_string = descriptor['serviceInterface']
    # the Classname only for the jaxrs Interface from which the service will be generated.
    service_interface_name = service_interface_string.split('.')[-1]
    # the package only for the jaxrs Interface from which the service will be generated.
    service_interface_package = service_interface_string.replace('.' + service_interface_name, '')

    # the template java bean class file.
    service_template_impl_file = model_path / str(service_interface_name + 'Bean.java')
    # the template java camel routes class file.
    routes_template_file = model_path / str(service_interface_name + 'Routes.java')
    # the template java spring application class file.
    application_template_file =  model_path / 'Application.java'

    this_files_path = filef.get_file_path(__file__)

    # the directory com/emprogen/java/maven
    java_maven_dir = jmf.get_java_maven_path()
    # the location of the java properties file mapping tpe to package.type.
    typ_to_pkg_typ = propf.load_properties_as_dict(java_maven_dir / 'java_type.properties')

    # the location of the script that gets maven dependencies for calling from classpath context
    maven_cp_py = java_maven_dir / 'maven_cp.py'
    # the location of the properties file with snippets used to create a camel route in java dsl.
    camel_route_choice_url = this_files_path / 'camel_route_choice.properties'
    # the spring annotation for defining a spring managed bean.
    spring_component_ann = "@org.springframework.stereotype.Component"
    # the package.Classname of a tool used to generate a java impl Class given a java Interface.
    gen_impl_class = "com.emprogen.generate.impl.GenerateImplService"
    # the maven gav for the GenerateImplService tool.
    generate_impl_gav = "com.emprogen:generate-impl:0.0.2"

    # Geneate Maven project.
    opts = {}
    opts['api_groupId'] = api_gav.group_id
    opts['api_artifactId'] = api_gav.artifact_id
    opts['api_version'] = api_gav.version
    opts['jaxrs_service_interface'] = service_interface_name
    opts['jaxrs_service_package'] = service_interface_package

    mvn_options = spf.capture_contextual_command_line_options(kwargs.get('command_args', []), 'mvn')
    mvn_opts = {'mvn_options': mvn_options}
    opts.update(mvn_opts)

    print(f'mvn_options: {mvn_options}')
    print(f'opts: {opts}')

    jmf.generate_maven_project(arch_gav, proj_gav, descriptor['author'], **opts)

    # get the maven dependencies for the module containing the jaxrs Interface from which the service will be generated.
    service_implementation_classpath = spf.run_subprocess_capture_output([maven_cp_py, service_interface_gav_string]).strip()
    # get the maven dependencies for the module containing the tool used to generate a java impl Class given a java Interface.
    generate_impl_classpath = spf.run_subprocess_capture_output([maven_cp_py, generate_impl_gav]).strip()
    # print(f'service_implementation_classpath: {service_implementation_classpath}')
    # print(f'generate_impl_classpath: {generate_impl_classpath}')
    # print(f'generated_package: {generated_package}')
    # print(f'service_interface_string: {service_interface_string}')

    # run the tool to get the generated code from the jaxrs Interface.
    generated_impl = spf.run_subprocess_capture_output(['java', '-cp', 
            service_implementation_classpath + ':' + generate_impl_classpath, gen_impl_class, 
            service_interface_string, generated_package])
    print(str(generated_impl))

    # Overwrite content of service bean impl with new content.
    filef.replace_file_contents(generated_impl, service_template_impl_file)

    # Write "@org.springframework.stereotype.Component\n" before "public class"
    annotation = spring_component_ann + '\npublic class'
    filef.replace_text_in_file('public class', annotation, service_template_impl_file)

    # update Routes class with interface methods

    #get methods
    # methods will be \s methodName[\s zero or more whitespace, then left parentheses. (]
    pattern = re.compile(r'(?<=\s)([a-zA-Z0-9$_]+)(?=\s*\()')
    matches = re.finditer(pattern, generated_impl)
    match_list = [match.group() for match in matches]
    #print (f'match_list: {match_list}')

    # build .when() string
    when_string = propf.get_property('when', camel_route_choice_url)
    print(f'when_string: {when_string}')

    # for each method, append a new when string, replacing %0 placeholder with method name.
    route_string = ''
    for api_method in match_list:
        route_string += when_string.replace('%', api_method)
    semicolon = propf.get_property('semicolon', camel_route_choice_url)
    route_string += semicolon

    # replace '^' with \n
    route_string = route_string.replace('^', '\n')
    print(f'route_string: {route_string}')

    # remove existing route choice options & replace with built route string.
    rerco_pattern = r'(?<=\.choice\(\)\n)((.|\n)+;)'
    filef.replace_text_in_file(rerco_pattern, route_string, routes_template_file)

    # add addtl dependencies to the pom.
    # if no items in optional dependencyGav, default {} for null safety
    for dependency in descriptor.get('dependencyGav', {}):
        print(f'adding dependency to pom: {dependency}')
        jmf.add_dependency(proj_pom_path, yf.get_gav(dependency))

    # update lombok version so it compiles.
    jmf.remove_dependency(proj_pom_path, yf.get_gav('org.projectlombok:lombok'))
    jmf.add_dependency(proj_pom_path, yf.get_gav('org.projectlombok:lombok:1.18.30'))

    # update imports
    formatf.beautify_imports(proj_pom_path)

    # add licenses to files
    pl.prepend_licenses(descriptor, proj_path, files_path)

    # verify it compiles
    jmf.call_mvn_with_options(**mvn_opts, goal='clean install', file=proj_pom_path)
    jmf.call_mvn_with_options(**mvn_opts, goal='clean', file=proj_pom_path)

    print(f'Finished generation for script {SCRIPT_VERSION}.')

#!/usr/bin/env python3
from pathlib import Path

import com.emprogen.file_functions as filef
import com.emprogen.java.maven.field_functions as ff
import com.emprogen.java.maven.format_functions as formatf
import com.emprogen.java.maven.java_maven_functions as jmf
import com.emprogen.java.maven.yaml_functions as yf
import com.emprogen.prepend_license as pl
import com.emprogen.properties_functions as propf
import com.emprogen.subprocess_functions as spf
from com.emprogen.java.maven.models import Gav

SCRIPT_VERSION = 'com.emprogen.java.maven.model.lombok.jaxrs.p0.v1.generate.py'


def generate(
    descriptor: dict,
    archetype_gav: Gav = Gav(
        'com.emprogen',
        'model-lombok-jaxrs-p0-archetype',
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

    # the directory of the maven pom for the generated code. Usually at the directory root of project.
    proj_path = Path(proj_gav.artifact_id)
    proj_pom_path = proj_path / 'pom.xml'

    # the directory of the java code.
    model_path = jmf.get_model_path(proj_gav)

    # the template java model class file.
    template_file = model_path / 'class0.java'

    # the location of the java properties file mapping tpe to package.type.
    typ_to_pkg_typ = propf.load_properties_as_dict(jmf.get_java_maven_path() / 'java_type.properties')

    this_files_path = filef.get_file_path(__file__)

    # the location of the java properties file mapping field to annotation.
    field_annotations = propf.get_property('field', this_files_path / 'jaxrs_field_annotation.properties')

    # Geneate Maven project.
    opts = {}
    opts['class0'] = 'class0'
    opts['fields'] = 'fields'

    mvn_options = spf.capture_contextual_command_line_options(kwargs.get('command_args', []), 'mvn')
    mvn_opts = {'mvn_options': mvn_options}
    opts.update(mvn_opts)

    print(f'mvn_options: {mvn_options}')
    print(f'opts: {opts}')

    jmf.generate_maven_project(arch_gav, proj_gav, descriptor['author'], **opts)

    # for each model file
    for model in descriptor['model']:

        new_class_name = model['name']
        new_file_name = model_path / str(new_class_name + '.java')
        # create the file, replace name
        filef.copy_file(template_file, new_file_name)
        # set the class name in the file to the correct value.
        filef.replace_text_in_file('class0', new_class_name, new_file_name)

        # replace fields with field string
        field_to_type = yf.get_fields_and_types(model)
        field_list = field_to_type.keys()
        field_to_pkg_typ = ff.map_fields_to_qualified_types(field_to_type, typ_to_pkg_typ)
        field_string = ff.create_field_string(field_to_pkg_typ, True)
        #print(f'field_string: {field_string}')

        for field in field_list:
            # replace field in annotation
            field_annotation = field_annotations.replace('%', field)
            # replace replacement content in with annotation.
            field_string = field_string.replace('&%' + field + '&%', field_annotation)
        field_string = field_string.replace('^', '\n')
        #print(f'field_string: {field_string}')
        # replace annotation
        filef.replace_text_in_file('    fields', field_string, new_file_name)

    # delete placeholder model
    filef.delete_file(template_file)

    # add addtl dependencies to the pom.
    # if no items in optional dependencyGav, default {} for null safety
    for dependency in descriptor.get('dependencyGav', {}):
        print(f'adding dependency to pom: {dependency}')
        jmf.add_dependency(proj_pom_path, yf.get_gav(dependency))

    # Update  lombok version to 1.18.30 to get latest features and fixes.
    jmf.remove_dependency(proj_pom_path, Gav('org.projectlombok', 'lombok', None))
    jmf.add_dependency(proj_pom_path, Gav('org.projectlombok', 'lombok', '1.18.30'))

    # update imports
    formatf.beautify_imports(proj_pom_path)

    # get all of the java files in generated code so we can process them.
    java_file_list = filef.get_files_list_by_extension_dict(
        proj_path / 'src' / 'main' / 'java'
    ).get('.java', [])
    print(f'java_file_list: {java_file_list}')

    formatf.gjf(java_file_list)

    # add licenses to files
    pl.prepend_licenses(descriptor, proj_path, files_path)

    # verify it compiles
    jmf.call_mvn_with_options(**mvn_opts, goal='clean install', file=proj_pom_path)
    jmf.call_mvn_with_options(**mvn_opts, goal='clean', file=proj_pom_path)

    print(f'Finished generation for script {SCRIPT_VERSION}.')

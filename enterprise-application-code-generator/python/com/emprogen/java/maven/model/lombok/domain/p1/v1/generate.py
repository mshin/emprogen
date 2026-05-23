#!/usr/bin/env python3
import re
from pathlib import Path

import com.emprogen.file_functions as filef
import com.emprogen.java.maven.field_functions as fieldf
import com.emprogen.java.maven.format_functions as formatf
import com.emprogen.java.maven.java_maven_functions as jmf
import com.emprogen.java.maven.yaml_functions as yf
import com.emprogen.prepend_license as pl
import com.emprogen.properties_functions as propf
import com.emprogen.subprocess_functions as spf
from com.emprogen.java.maven.models import Gav

SCRIPT_VERSION = 'com.emprogen.java.maven.model.lombok.domain.p1.v1.generate.py'


def generate(
    descriptor: dict,
    archetype_gav: Gav = Gav('com.emprogen', 'model-lombok-domain-p1-archetype', '0.0.1'),
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

    # the template java enum class file.
    enum_template_file = model_path / 'class1.java'

    # the location of the java properties file mapping tpe to package.type.
    typ_to_pkg_typ = propf.load_properties_as_dict(jmf.get_java_maven_path() / 'java_type.properties')

    # Geneate Maven project.
    opts = {}
    opts['class0'] = 'class0'
    opts['class1'] = 'class1'
    opts['fields'] = 'fields'
    opts['enumerations'] = 'enumerations'

    mvn_options = spf.capture_contextual_command_line_options(kwargs.get('command_args', []), 'mvn')
    mvn_opts = {'mvn_options': mvn_options}
    opts.update(mvn_opts)

    print(f'mvn_options: {mvn_options}')
    print(f'opts: {opts}')

    jmf.generate_maven_project(arch_gav, proj_gav, descriptor['author'], **opts)

    # for each model file
    for model in descriptor.get('model', {}):

        new_class_name = model['name']
        new_file_name = model_path / str(new_class_name + '.java')
        # create the file, replace name
        filef.copy_file(template_file, new_file_name)
        # set the class name in the file to the correct value.
        filef.replace_text_in_file('class0', new_class_name, new_file_name)

        # replace fields with field string
        field_to_type = yf.get_fields_and_types(model)
        field_to_pkg_typ = fieldf.map_fields_to_qualified_types(field_to_type, typ_to_pkg_typ)
        field_string = fieldf.create_field_string(field_to_pkg_typ, False)
        print(f'field_string: {field_string}')
        filef.replace_text_in_file('    fields', field_string, new_file_name)

        is_abstract = model.get('abstract', False)
        extends = model.get('extends', None)
        implements = model.get('implements', None)

        abstract_string = 'abstract ' if is_abstract else ''
        find_string = '\npublic ' + abstract_string + 'class ' + new_class_name + ' '

        if is_abstract:
            print(f'is_abstract: {is_abstract}')
            filef.replace_text_in_file('\npublic class', '\npublic abstract class', new_file_name)
        if extends:
            print(f'extends: {extends}')
            replace_string = find_string + 'extends ' + extends + ' '
            filef.replace_text_in_file(find_string, replace_string, new_file_name)
        if implements:
            print(f'implements: {implements}')
            new_find_string = find_string + 'implements Serializable'
            replace_string = new_find_string + ', ' + implements
            filef.replace_text_in_file(new_find_string, replace_string, new_file_name)

    # delete placeholder model
    filef.delete_file(template_file)

    for enum in descriptor.get('enum', {}):

        new_class_name = enum['name']
        new_file_name = model_path / str(new_class_name + '.java')
        # create the file, replace name
        filef.copy_file(enum_template_file, new_file_name)
        # set the class name in the file to the correct value.
        filef.replace_text_in_file('class1', new_class_name, new_file_name)

        # Get enum content.
        enum_fields = enum.get('fields', []) 
        enum_values = enum.get('values', [])
        enum_str = ''

        # if fields present, split enum types from the values set for each enum type.
        enums = []
        enum_vals = []
        for enum_value in enum_values:
            enum_array = [s for s in re.split(r'[^a-zA-Z0-9_$"\']', enum_value) if s]
            print(f'enum_array: {enum_array}')
            enums.append(enum_array[0])

            enum_val = enum_array[1:]
            if len(enum_val) > 0:
                enum_vals.append(enum_val)
        print(f'enums: {enums}')
        print(f'enum_vals: {enum_vals}')

        # if there are fields set by enum values, add the enum values to the enumerated list items.
        if len(enum_vals) > 0:
            for i, enumm in enumerate(enums):
                vals = enum_vals[i] if i < len(enum_vals) else []
                enums[i] = enumm + '(' + ', '.join(vals) + ')'

        # if there are enums, add them to the enum string.
        if len(enums) > 0:
            enum_str += '    ' + ', '.join(str(a) for a in enums ) + ';\n'

        # if fields present, declare them and add them to the enum string.
        if enum_fields:
            field_to_type = yf.get_fields_and_types(enum)
            field_to_pkg_typ = fieldf.map_fields_to_qualified_types(field_to_type, typ_to_pkg_typ)
            field_string = fieldf.create_field_string(field_to_pkg_typ, False)
            print(f'field_string: {field_string}')
            enum_str += field_string + '\n'

        # replace enum paceholder with generated enum values.
        filef.replace_text_in_file(r'    enumerations', enum_str, new_file_name)

    # delete placeholder enum
    filef.delete_file(enum_template_file)

    # add addtl dependencies to the pom.
    # if no items in optional dependencyGav, default {} for null safety
    for dependency in descriptor.get('dependencyGav', {}):
        print(f'adding dependency to pom: {dependency}')
        jmf.add_dependency(proj_pom_path, yf.get_gav(dependency))

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

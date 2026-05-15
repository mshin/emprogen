#!/usr/bin/env python3
import glob

import com.emprogen.file_functions as FILEF
import com.emprogen.java.maven.field_functions as FIELDF
import com.emprogen.properties_functions as PROPF
import com.emprogen.java.maven.format_functions as FORMATF
import com.emprogen.java.maven.java_maven_functions as JMF
import com.emprogen.java.maven.yaml_functions as YF
from com.emprogen.java.maven.models import Gav


def generate(descriptor: dict, archetype_gav: Gav = Gav('com.emprogen', 'model-lombok-domain-p1-archetype', '0.0.1'),
       *, files_path: str = None, **kwargs) -> None:

    # Do all 1 time loads and calculations up front.

    # define maven archetype used for this generator within script.
    arch_gav = archetype_gav

    # the maven groupId:artifactId:version for the code module to be generated
    proj_gav = YF.get_generated_project_gav(descriptor)

    # the directory of the maven pom for the generated code. Usually at the directory root of project.
    proj_pom_path = proj_gav.artifact_id + '/pom.xml'

    # the directory of the java code.
    model_path = JMF.get_model_path(proj_gav)

    # the template java model class file.
    template_file = model_path + '/class0.java'

    # the template java enum class file.
    enum_template_file = model_path + '/class1.java'

    # the location of the java properties file mapping tpe to package.type.
    typ_to_pkg_typ = PROPF.load_properties_as_dict(JMF.get_java_maven_path() + '/java_type.properties')

    # Geneate Maven project.
    opts = {}
    opts['class0'] = 'class0'
    opts['class1'] = 'class1'
    opts['fields'] = 'fields'
    opts['enumerations'] = 'enumerations'
    JMF.generate_maven_project(arch_gav, proj_gav, descriptor['author'], **opts)

    # for each model file
    for model in descriptor.get('model', {}):

        new_class_name = model['name']
        new_file_name = model_path + '/' + new_class_name + '.java'
        # create the file, replace name
        FILEF.copy_file(template_file, new_file_name)
        # set the class name in the file to the correct value.
        FILEF.replace_text_in_file('class0', new_class_name, new_file_name)

        # replace fields with field string
        field_to_type = YF.get_fields_and_types(model)
        field_to_pkg_typ = FIELDF.map_fields_to_qualified_types(field_to_type, typ_to_pkg_typ)
        field_string = FIELDF.create_field_string(field_to_pkg_typ, False)
        print('field_string: ' + field_string)
        FILEF.replace_text_in_file('    fields', field_string, new_file_name)

        is_abstract = model.get('abstract', False)
        extends = model.get('extends', None)
        implements = model.get('implements', None)

        abstract_string = 'abstract ' if is_abstract else ''
        find_string = '\npublic ' + abstract_string + 'class ' + new_class_name + ' '

        if is_abstract:
            print('is_abstract: ' + str(is_abstract))
            FILEF.replace_text_in_file('\npublic class', '\npublic abstract class', new_file_name)
        if extends:
            print('extends: ' + str(extends))
            replace_string = find_string + 'extends ' + extends + ' '
            FILEF.replace_text_in_file(find_string, replace_string, new_file_name)
        if implements:
            print('implements: ' + str(implements))
            new_find_string = find_string + 'implements Serializable'
            replace_string = new_find_string + ', ' + implements
            FILEF.replace_text_in_file(new_find_string, replace_string, new_file_name)

    # delete placeholder model
    FILEF.delete_file(template_file)

    for enum in descriptor.get('enum', {}):

        new_class_name = enum['name']
        new_file_name = model_path + '/' + new_class_name + '.java'
        # create the file, replace name
        FILEF.copy_file(enum_template_file, new_file_name)
        # set the class name in the file to the correct value.
        FILEF.replace_text_in_file('class1', new_class_name, new_file_name)

        # Get enum content.
        enum_fields = enum.get('fields', []) 
        enum_values = enum.get('values', [])
        enum_str = ''

        # if fields present, split enum types from the values set for each enum type.
        enums = []
        enum_vals = []
        for enum_value in enum_values:
            enum_array = enum_value.split(',')
            enums.append(enum_array[0])

            enum_val = enum_array[1:]
            if len(enum_val) > 0:
                enum_vals.append(enum_val)

        # if there are fields set by enum values, add the enum values to the enumerated list items.
        if len(enum_vals) > 0:
            for i, enumm in enumerate(enums):
                enums[i] = enumm + '(' + ', '.join(enum_vals[i]) + ')'

        # if there are enums, add them to the enum string.
        if len(enums) > 0:
            enum_str += '    ' + ', '.join(str(a) for a in enums ) + ';\n'

        # if fields present, declare them and add them to the enum string.
        if enum_fields:
            field_to_type = YF.get_fields_and_types(enum)
            field_to_pkg_typ = FIELDF.map_fields_to_qualified_types(field_to_type, typ_to_pkg_typ)
            field_string = FIELDF.create_field_string(field_to_pkg_typ, False)
            print('field_string: ' + field_string)
            enum_str += field_string + '\n'

        # replace enum paceholder with generated enum values.
        FILEF.replace_text_in_file(r'    enumerations', enum_str, new_file_name)

    # delete placeholder enum
    FILEF.delete_file(enum_template_file)

    # add addtl dependencies to the pom.
    # if no items in optional dependencyGav, default {} for null safety
    for dependency in descriptor.get('dependencyGav', {}):
        print('adding dependency to pom: ' + dependency)
        JMF.add_dependency(proj_pom_path, YF.get_gav(dependency))

    # update imports
    FORMATF.beautify_imports(proj_pom_path)

    # get all of the java files in generated code so we can process them.
    java_file_list = glob.glob(proj_gav.artifact_id + '/src/main/java/**/*.java', recursive=True)
    print('java_file_list: ' + str(java_file_list))
    FORMATF.gjf(java_file_list)

    # verify it compiles
    JMF.call_mvn_with_options(goal='clean install', file=proj_pom_path)

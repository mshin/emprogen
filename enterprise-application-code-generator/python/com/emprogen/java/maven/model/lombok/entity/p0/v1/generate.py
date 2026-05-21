#!/usr/bin/env python3
from pathlib import Path

import com.emprogen.file_functions as filef
import com.emprogen.java.maven.field_functions as fieldf
import com.emprogen.java.maven.format_functions as formatf
import com.emprogen.java.maven.java_maven_functions as jmf
import com.emprogen.java.maven.yaml_functions as yf
import com.emprogen.prepend_license as pl
import com.emprogen.properties_functions as propf
import com.emprogen.subprocess_functions as spf
import com.emprogen.text_functions as textf
from com.emprogen.java.maven.models import Gav
from com.emprogen.java.maven.models import JoinInstruction
from com.emprogen.java.maven.models import TableRelationship

SCRIPT_VERSION = 'com.emprogen.java.maven.model.lombok.entity.p0.v1.generate.py'


def get_join_instruction(join_desc: str) -> JoinInstruction:
    # Format: "- ${Entity.class} **-** ${OtherEntity.class}"
    # Where first * is <|- second * is 1|n third * is 1|n and fourth * is >|-.
    # Example: FormEntity <1-1> AccountEntity

    join_desc_list = str(join_desc).split()
    ent_name_left = join_desc_list[0]
    ent_name_right = join_desc_list[2]
    join_str = join_desc_list[1]
    is_ref_left = True
    is_ref_right = True
    is_owner_right = True
    mapping = None

    if join_str[0] == '-':
        is_ref_left = False
    if join_str[4] == '-':
        is_ref_right = False

    if join_str[1] == 'n':
        if join_str[3] == 'n':
            mapping = TableRelationship.MANY_TO_MANY
        else:
            mapping = TableRelationship.MANY_TO_ONE
    else:
        if join_str[3] == 'n':
            mapping = TableRelationship.ONE_TO_MANY
        else:
            mapping = TableRelationship.ONE_TO_ONE

    if not is_ref_right or mapping == TableRelationship.MANY_TO_ONE:
        is_owner_right = False

    return JoinInstruction(
        ent_name_left,
        ent_name_right,
        mapping,
        is_ref_left,
        is_ref_right,
        is_owner_right
    )


def replace_vars_in_annotation(
    annotation: str,
    refing_type: str,
    refing_type_var: str,
    refing_type_pk_var: str,
    refing_type_pk_var_snake: str,
    other_pk_var_snake: str,
    owning_type: str,
    owning_type_var: str
) -> str:
    annotation = annotation.replace(r'%0', refing_type)
    annotation = annotation.replace(r'%1', refing_type_var)
    annotation = annotation.replace(r'%4pk', refing_type_pk_var)
    annotation = annotation.replace(r'%5pksql', refing_type_pk_var_snake)
    annotation = annotation.replace(r'%6opksql', other_pk_var_snake)
    annotation = annotation.replace(r'%2', owning_type)
    annotation = annotation.replace(r'%3', owning_type_var)
    return annotation


def generate(
    descriptor: dict,
    archetype_gav: Gav = Gav(
        'com.emprogen',
        'model-lombok-entity-p0-archetype',
        '0.0.1'
    ),
    *,
    files_path: str = None,
    java_version: str = '17',
    **kwargs
) -> None:
    print(f'in {SCRIPT_VERSION}')

    # Do all 1 time loads and calculations up front.

    # define maven archetype used for this generator within script.
    arch_gav = archetype_gav

    # the maven groupId:artifactId:version for the code module to be generated
    proj_gav = yf.get_generated_project_gav(descriptor)

    proj_path = Path(proj_gav.artifact_id)
    # the directory of the maven pom for the generated code. Usually at the directory root of project.
    proj_pom_path = proj_path / 'pom.xml'

    # the directory of the java code.
    model_path = jmf.get_model_path(proj_gav)

    # the template java entity class file.
    template_file = model_path / 'class0.java'

    # the location of the java properties file mapping tpe to package.type.
    typ_to_pkgtyp = propf.load_properties_as_dict(jmf.get_java_maven_path() / 'java_type.properties')

    this_files_path = filef.get_file_path(__file__)

    # the locations of additional properties files.
    jpa_type_annotation_dict = propf.load_properties_as_dict(this_files_path / 'jpa_type_annotation.properties')
    jpa_join_annotation_dict = propf.load_properties_as_dict(this_files_path / 'jpa_join_annotation.properties')
    dep_gav_url = this_files_path / 'dep_gav.properties'

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

    # some of the time types used in the jpa type annotations require additional dependencies.
    needs_converter_dependency = False

    # for each model file from descriptor
    for model in descriptor['model']:

        # by convention, all entity classes end in the word 'Entity'
        new_class_name = model['name']
        if not new_class_name.endswith('Entity'):
            new_class_name += 'Entity'

        # by convention, columns in database use snake case.
        new_class_name_snake = textf.camel_to_snake(new_class_name)

        # get the primary key value out of the descriptor file.
        pk = model['pk']

        # calculate the model class name to be created
        new_file_name = model_path / str(new_class_name + '.java')

        # create the class file; replace name
        filef.copy_file(template_file, new_file_name)

        # set the class name in the file to the correct value.
        filef.replace_text_in_file('class0', new_class_name, new_file_name)

        # calculate the raw field string for the class file
        # first, get the field to type dictionary
        field_to_type = yf.get_fields_and_types(model)
        # then, get the raw field list
        field_list = field_to_type.keys()
        # next, calculate the field to package.type dictionary.
        field_to_pkgtyp = fieldf.map_fields_to_qualified_types(field_to_type, typ_to_pkgtyp)
        # finally, generate the raw field string with annotation placeholders.
        field_string = fieldf.create_field_string(field_to_pkgtyp, True)
        #print('field_string: ' + field_string)

        # for each entry in the field to package.type dictionary
        for field, typ in field_to_pkgtyp.items():

            # get the snake case version of each field, because databases require snake case not camel case.
            field_snake = textf.camel_to_snake(field)
            # the property key defaults to the type, but if it's the primary key, get the primary key property.
            prop_key = typ
            # in most cases the anntation replacement string will be the field in snake case.
            replacement_string = field_snake
            # fi the field is the primary key,
            if field == pk:
                # the property we want is the primary key one
                prop_key = 'pk'
                # the replacement string is classname instead of field name.
                replacment_string = new_class_name_snake
            # get the annotation based on tye propKey. If it's not there, use the default annotation.
            ann = jpa_type_annotation_dict.get(prop_key, '    @javax.persistence.Column( name = \"%\" )')
            # replace placeholders in annotation with replacementString
            ann = ann.replace('%', replacement_string)

            # add the processed annotation to the corresponding field in fieldString.
            field_string = field_string.replace('&%' + field + '&%', ann)

        # replace all caret symbols with newlines.
        # Some of the annotations are stored as properties and use caret instead of newline.
        field_string = field_string.replace('^', '\n')
        print(f'field_string: {field_string}')
        # replace contents of class file. 'fields' placeholder replaced with generated fields.
        filef.replace_text_in_file('    fields', field_string, new_file_name)

        # if certain types are used for fields, add a new dependency.
        # code: if set intersection of set('LocalDate', 'LocalDateTime') and set(type)
        if {'LocalDate', 'LocalDateTime'} & set(field_to_type.values()):
            needs_converter_dependency = True

    # get model to pk dictionary
    model_name_to_pk_dict = {}
    for model in descriptor['model']:
        model_name_to_pk_dict[model.get('name')] = model.get('pk')

    # get joins dictionary
    # create list of the join instructions
    join_instruction_list = []
    for join in descriptor['joins']:
        join_instruction = get_join_instruction(join)
        join_instruction_list.append(join_instruction)

    # build the annotation and write it to file.
    for join_instruction in join_instruction_list:

        # set owner/not owner as either left or right entity
        if join_instruction.is_owner_right:
            owner = join_instruction.ent_name_right
            not_owner = join_instruction.ent_name_left
        else:
            owner = join_instruction.ent_name_left
            not_owner = join_instruction.ent_name_right

        # set variables needed for placeholder replacement in join annotation.
        owning_type = owner
        owning_type_var = textf.lower_first(owner)
        refing_type = not_owner
        refing_type_var = textf.lower_first(not_owner)
        refing_type_pk_var = model_name_to_pk_dict.get(refing_type)
        refing_type_pk_var_snake = textf.camel_to_snake(refing_type_pk_var)
        other_pk_var = model_name_to_pk_dict.get(owning_type) # not used in annotation
        other_pk_var_snake = textf.camel_to_snake(other_pk_var)

        # start with left Entity
        if join_instruction.is_ref_left:
            # get the template annotation. Adding caret to the beginning to be replaced with newline.
            ann_prop = join_instruction.get_annotation_key_left()
            ann = '^' + jpa_join_annotation_dict.get(ann_prop.name)

            # build annotation by replacing placeholders.
            ann = replace_vars_in_annotation(ann, refing_type, refing_type_var, refing_type_pk_var, refing_type_pk_var_snake, other_pk_var_snake, owning_type, owning_type_var)
            # we're going to replace the class's closing bracket with annotation, so must add it back in.
            ann += '^^}^'
            # caret for newline.
            ann = ann.replace('^', '\n')

            # make the path for entity to write to.
            entity_file_path = model_path / str(join_instruction.ent_name_left + '.java')
            # write the annotation to the respective file by appending it to the end.
            filef.replace_text_in_file('\n}', ann, entity_file_path)

        # then do right Entity
        if join_instruction.is_ref_right:
            # get the template annotation
            ann_prop = join_instruction.get_annotation_key_right()
            ann = jpa_join_annotation_dict.get(ann_prop.name)

            # build annotation by replacing placeholders.
            ann = replace_vars_in_annotation(
                ann,
                refing_type,
                refing_type_var,
                refing_type_pk_var,
                refing_type_pk_var_snake,
                other_pk_var_snake,
                owning_type,
                owning_type_var
            )
            # we're going to replace the class's closing bracket with annotation, so must add it back in.
            ann += '^^}^'
            # caret for newline.
            ann = ann.replace('^', '\n')

            # make the path for entity to write to.
            entity_file_path = model_path / str(join_instruction.ent_name_right + '.java')
            # write the annotation to the respective file by appending it to the end.
            filef.replace_text_in_file('\n}', ann, entity_file_path)

    # delete placeholder model
    filef.delete_file(template_file)

    # If converter in files, then add that dependency.
    if needs_converter_dependency:
        type_converter_gav_string = propf.get_property('typeConverterGav', dep_gav_url)
        tc_gav = yf.get_gav(type_converter_gav_string)
        print(f'adding dependency to pom: {type_converter_gav_string}')
        jmf.add_dependency(proj_pom_path, tc_gav)

    # add addtl dependencies to the pom.
    # if no items in optional dependencyGav, default {} for null safety
    for dependency in descriptor.get('dependencyGav', {}):
        print(f'adding dependency to pom: {dependency}')
        jmf.add_dependency(proj_pom_path, yf.get_gav(dependency))

    # set java version to javaVersion
    maven_compiler_source = 'maven.compiler.source'
    maven_compiler_target = 'maven.compiler.target'
    jmf.remove_pom_properties(proj_pom_path, [maven_compiler_source, maven_compiler_target])
    jmf.add_pom_properties(proj_pom_path, {maven_compiler_source: java_version, maven_compiler_target: java_version})

    # update lombok version so it compiles.
    jmf.remove_dependency(proj_pom_path, yf.getGav('org.projectlombok:lombok'))
    jmf.add_dependency(proj_pom_path, yf.getGav('org.projectlombok:lombok:1.18.30'))

    # update imports
    formatf.beautify_imports(proj_pom_path)

    # add licenses to files
    pl.prepend_licenses(descriptor, proj_path, files_path)

    # verify it compiles
    jmf.call_mvn_with_options(**mvn_opts, goal='clean install', file=proj_pom_path)
    jmf.call_mvn_with_options(**mvn_opts, goal='clean', file=proj_pom_path)

    print(f'Finished generation for script {SCRIPT_VERSION}.')

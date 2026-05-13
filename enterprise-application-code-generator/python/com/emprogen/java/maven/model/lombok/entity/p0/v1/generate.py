import com.emprogen.java.maven.functions as jmf
import com.emprogen.java.maven.yaml_functions as yf
import com.emprogen.java.maven.field_functions as ff
from com.emprogen.java.maven.models import Gav
from com.emprogen.java.maven.models import JoinInstruction
from com.emprogen.java.maven.models import TableRelationship

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

def generate(descriptor: 'dict', archetypeGav: 'Gav' = Gav('com.emprogen', 'model-lombok-entity-p0-archetype', '0.0.1'),
        *, filesPath: 'str' = None, javaVersion: 'str' = '17', **kwargs) -> None:

    # Do all 1 time loads and calculations up front.

    # define maven archetype used for this generator within script.
    arch_gav = archetypeGav

    # the maven groupId:artifactId:version for the code module to be generated
    proj_gav = yf.getGeneratedProjectGav(descriptor)

    # the directory of the maven pom for the generated code. Usually at the directory root of project.
    proj_pom_path = proj_gav.artifact_id + '/pom.xml'

    # the directory of the java code.
    model_path = jmf.getModelPath(proj_gav)

    # the template java entity class file.
    template_file = model_path + '/class0.java'

    # the location of the java properties file mapping tpe to package.type.
    typ_to_pkgtyp = ff.loadPropertiesAsDict(jmf.getJavaMavenPath() + '/java_type.properties')

    this_files_path = str(jmf.getFilePath(__file__))

    # the locations of additional properties files.
    jpa_type_annotation_dict = ff.loadPropertiesAsDict(this_files_path + '/jpa_type_annotation.properties')
    jpa_join_annotation_dict = ff.loadPropertiesAsDict(this_files_path + '/jpa_join_annotation.properties')
    dep_gav_url = this_files_path + '/dep_gav.properties'

    # Geneate Maven project.
    opts = {}
    opts['class0'] = 'class0'
    opts['fields'] = 'fields'
    jmf.generateMavenProject(arch_gav, proj_gav, descriptor['author'], **opts)

    # some of the time types used in the jpa type annotations require additional dependencies.
    needs_converter_dependency = False

    # for each model file from descriptor
    for model in descriptor['model']:

        # by convention, all entity classes end in the word 'Entity'
        new_class_name = model['name']
        if not new_class_name.endswith('Entity'):
            new_class_name += 'Entity'

        # by convention, columns in database use snake case.
        new_class_name_snake = jmf.camelToSnake(new_class_name)

        # get the primary key value out of the descriptor file.
        pk = model['pk']

        # calculate the model class name to be created
        new_file_name = model_path + '/' + new_class_name + '.java'

        # create the class file; replace name
        jmf.copyFile(template_file, new_file_name)

        # set the class name in the file to the correct value.
        jmf.replaceTextInFile('class0', new_class_name, new_file_name)

        # calculate the raw field string for the class file
        # first, get the field to type dictionary
        field_to_type = yf.getFieldsAndTypes(model)
        # then, get the raw field list
        field_list = field_to_type.keys()
        # next, calculate the field to package.type dictionary.
        field_to_pkgtyp = ff.mapFieldsToQualifiedTypes(field_to_type, typ_to_pkgtyp)
        # finally, generate the raw field string with annotation placeholders.
        field_string = ff.createFieldString(field_to_pkgtyp, True)
        #print('field_string: ' + field_string)

        # for each entry in the field to package.type dictionary
        for field, typ in field_to_pkgtyp.items():

            # get the snake case version of each field, because databases require snake case not camel case.
            field_snake = jmf.camelToSnake(field)
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
        print('fieldString: ' + field_string)
        # replace contents of class file. 'fields' placeholder replaced with generated fields.
        jmf.replaceTextInFile('    fields', field_string, new_file_name)

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
        owning_type_var = jmf.lower1st(owner)
        refing_type = not_owner
        refing_type_var = jmf.lower1st(not_owner)
        refing_type_pk_var = model_name_to_pk_dict.get(refing_type)
        refing_type_pk_var_snake = jmf.camelToSnake(refing_type_pk_var)
        other_pk_var = model_name_to_pk_dict.get(owning_type) # not used in annotation
        other_pk_var_snake = jmf.camelToSnake(other_pk_var)

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
            entity_file_path = model_path + '/' + join_instruction.ent_name_left + '.java'
            # write the annotation to the respective file by appending it to the end.
            jmf.replaceTextInFile('\n}', ann, entity_file_path)

        # then do right Entity
        if join_instruction.is_ref_right:
            # get the template annotation
            ann_prop = join_instruction.get_annotation_key_right()
            ann = jpa_join_annotation_dict.get(ann_prop.name)

            # build annotation by replacing placeholders.
            ann = replace_vars_in_annotation(ann, refing_type, refing_type_var, refing_type_pk_var, refing_type_pk_var_snake, other_pk_var_snake, owning_type, owning_type_var)
            # we're going to replace the class's closing bracket with annotation, so must add it back in.
            ann += '^^}^'
            # caret for newline.
            ann = ann.replace('^', '\n')

            # make the path for entity to write to.
            entity_file_path = model_path + '/' + join_instruction.ent_name_right + '.java'
            # write the annotation to the respective file by appending it to the end.
            jmf.replaceTextInFile('\n}', ann, entity_file_path)

    # delete placeholder model
    jmf.deleteFile(template_file)

    # If converter in files, then add that dependency.
    if needs_converter_dependency:
        type_converter_gav_string = jmf.getProperty('typeConverterGav', dep_gav_url)
        tc_gav = yf.getGav(type_converter_gav_string)
        print('adding dependency to pom: ' + type_converter_gav_string)
        jmf.addDependency(proj_pom_path, tc_gav)

    # add addtl dependencies to the pom.
    # if no items in optional dependencyGav, default {} for null safety
    for dependency in descriptor.get('dependencyGav', {}):
        print('adding dependency to pom: ' + dependency)
        jmf.addDependency(proj_pom_path, yf.getGav(dependency))

    # set java version to javaVersion
    maven_compiler_source = 'maven.compiler.source'
    maven_compiler_target = 'maven.compiler.target'
    jmf.removePomProperties(proj_pom_path, [maven_compiler_source, maven_compiler_target])
    jmf.addPomProperties(proj_pom_path, {maven_compiler_source: javaVersion, maven_compiler_target: javaVersion})

    # update lombok version so it compiles.
    jmf.removeDependency(proj_pom_path, yf.getGav('org.projectlombok:lombok'))
    jmf.addDependency(proj_pom_path, yf.getGav('org.projectlombok:lombok:1.18.30'))

    # update imports
    jmf.beautifyImports(proj_pom_path)

    # verify it compiles
    jmf.callMvnWithOptions(goal='clean install', file=proj_pom_path)

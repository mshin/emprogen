import com.emprogen.java.maven.functions as jmf
import com.emprogen.java.maven.yaml_functions as yf
import com.emprogen.java.maven.field_functions as ff
from com.emprogen.java.maven.models import Gav
import glob

def generate(descriptor: 'dict', archetypeGav: 'Gav' = Gav('com.emprogen', 'model-lombok-domain-p1-archetype', '0.0.1'),
       *, filesPath: 'str' = None) -> None:

    # Do all 1 time loads and calculations up front.

    # define maven archetype used for this generator within script.
    archGav = archetypeGav

    # the maven groupId:artifactId:version for the code module to be generated
    projGav = yf.getGeneratedProjectGav(descriptor)

    # the directory of the maven pom for the generated code. Usually at the directory root of project.
    projPomPath = projGav.artifactId + '/pom.xml'

    # the directory of the java code.
    modelPath = jmf.getModelPath(projGav)

    # the template java model class file.
    templateFile = modelPath + '/class0.java'

    # the template java enum class file.
    enumTemplateFile = modelPath + '/class1.java'

    # the location of the java properties file mapping tpe to package.type.
    typToPkgtyp = ff.loadPropertiesAsDict(jmf.getJavaMavenPath() + '/java_type.properties')

    # Geneate Maven project.
    opts = {}
    opts['class0'] = 'class0'
    opts['class1'] = 'class1'
    opts['fields'] = 'fields'
    opts['enumerations'] = 'enumerations'
    jmf.generateMavenProject(archGav, projGav, descriptor['author'], **opts)

    # for each model file
    for model in descriptor.get('model', {}):

        newClassName = model['name']
        newFileName = modelPath + '/' + newClassName + '.java'
        # create the file, replace name
        jmf.copyFile(templateFile, newFileName)
        # set the class name in the file to the correct value.
        jmf.replaceTextInFile('class0', newClassName, newFileName)

        # replace fields with field string
        fieldToType = yf.getFieldsAndTypes(model)
        fieldToPkgtyp = ff.mapFieldsToQualifiedTypes(fieldToType, typToPkgtyp)
        fieldString = ff.createFieldString(fieldToPkgtyp, False)
        print('fieldString: ' + fieldString)
        jmf.replaceTextInFile('    fields', fieldString, newFileName)

        is_abstract = model.get('abstract', False)
        extends = model.get('extends', None)
        implements = model.get('implements', None)

        abstract_string = 'abstract ' if is_abstract else ''
        find_string = '\npublic ' + abstract_string + 'class ' + newClassName + ' '

        if is_abstract:
            print('is_abstract: ' + str(is_abstract))
            jmf.replaceTextInFile('\npublic class', '\npublic abstract class', newFileName)
        if extends:
            print('extends: ' + str(extends))
            replace_string = find_string + 'extends ' + extends + ' '
            jmf.replaceTextInFile(find_string, replace_string, newFileName)
        if implements:
            print('implements: ' + str(implements))
            new_find_string = find_string + 'implements Serializable'
            replace_string = new_find_string + ', ' + implements
            jmf.replaceTextInFile(new_find_string, replace_string, newFileName)



    # delete placeholder model
    jmf.deleteFile(templateFile)

    for enum in descriptor.get('enum', {}):

        newClassName = enum['name']
        newFileName = modelPath + '/' + newClassName + '.java'
        # create the file, replace name
        jmf.copyFile(enumTemplateFile, newFileName)
        # set the class name in the file to the correct value.
        jmf.replaceTextInFile('class1', newClassName, newFileName)

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
            fieldToType = yf.getFieldsAndTypes(enum)
            fieldToPkgtyp = ff.mapFieldsToQualifiedTypes(fieldToType, typToPkgtyp)
            fieldString = ff.createFieldString(fieldToPkgtyp, False)
            print('fieldString: ' + fieldString)
            enum_str += fieldString + '\n'

        # replace enum paceholder with generated enum values.
        jmf.replaceTextInFile(r'    enumerations', enum_str, newFileName)

    # delete placeholder enum
    jmf.deleteFile(enumTemplateFile)

    # add addtl dependencies to the pom.
    # if no items in optional dependencyGav, default {} for null safety
    for dependency in descriptor.get('dependencyGav', {}):
        print('adding dependency to pom: ' + dependency)
        jmf.addDependency(projPomPath, yf.getGav(dependency))

    # update imports
    jmf.beautifyImports(projPomPath)

    # get all of the java files in generated code so we can process them.
    javaFileList = glob.glob(projGav.artifactId + '/src/main/java/**/*.java', recursive=True)
    print('javaFileList: ' + str(javaFileList))
    jmf.gjf(javaFileList)

    # verify it compiles
    jmf.callMvnWithOptions(goal='clean install', file=projPomPath)

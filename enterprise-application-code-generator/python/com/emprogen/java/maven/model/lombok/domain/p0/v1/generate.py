import com.emprogen.java.maven.functions as jmf
import com.emprogen.java.maven.yaml_functions as yf
import com.emprogen.java.maven.field_functions as ff
from com.emprogen.java.maven.models import Gav

def generate(descriptor: 'dict', archetypeGav: 'Gav' = Gav('com.emprogen', 'model-lombok-domain-p0-archetype', '0.0.1'),
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

    # delete placeholder model
    jmf.deleteFile(templateFile)

    for enum in descriptor.get('enum', {}):

        newClassName = enum['name']
        newFileName = modelPath + '/' + newClassName + '.java'
        # create the file, replace name
        jmf.copyFile(enumTemplateFile, newFileName)
        # set the class name in the file to the correct value.
        #TODO check class1 in file to ensure replaced correctly
        jmf.replaceTextInFile('class1', newClassName, newFileName)

        # if fieds present...
        #TODO set constructor and fields
        # for list of values, add the field values to each enumerated value

        # replace enum paceholder with generated enum values.
        enumValues = yf.getEnumValues(enum)
        enumStr = '    ' + ', '.join(str(a) for a in enumValues)
        jmf.replaceTextInFile(r'    enumerations', enumStr, newFileName)

    # delete placeholder enum
    jmf.deleteFile(enumTemplateFile)

    # add addtl dependencies to the pom.
    # if no items in optional dependencyGav, default {} for null safety
    for dependency in descriptor.get('dependencyGav', {}):
        print('adding dependency to pom: ' + dependency)
        jmf.addDependency(projPomPath, yf.getGav(dependency))

    # update imports
    jmf.beautifyImports(projPomPath)

    # verify it compiles
    jmf.callMvnWithOptions(goal='clean install', file=projPomPath)


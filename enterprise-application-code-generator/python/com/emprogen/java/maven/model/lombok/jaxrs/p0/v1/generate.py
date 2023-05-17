import com.emprogen.java.maven.functions as jmf
import com.emprogen.java.maven.yaml_functions as yf
import com.emprogen.java.maven.field_functions as ff
from com.emprogen.java.maven.models import Gav

def generate(descriptor: 'dict', archetypeGav: 'Gav' = Gav('com.emprogen', 'model-lombok-jaxrs-p0-archetype', '0.0.1')
        , *, filesPath: 'str' = None) -> None:

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

    # the location of the java properties file mapping tpe to package.type.
    typToPkgtyp = ff.loadPropertiesAsDict(jmf.getJavaMavenPath() + '/java_type.properties')

    thisFilesPath = str(jmf.getFilePath(__file__))

    # the location of the java properties file mapping field to annotation.
    fieldAnnotations = jmf.getProperty('field', thisFilesPath + '/jaxrs_field_annotation.properties')

    # Geneate Maven project.
    opts = {}
    opts['class0'] = 'class0'
    opts['fields'] = 'fields'
    jmf.generateMavenProject(archGav, projGav, descriptor['author'], **opts)

    # for each model file
    for model in descriptor['model']:

        newClassName = model['name']
        newFileName = modelPath + '/' + newClassName + '.java'
        # create the file, replace name
        jmf.copyFile(templateFile, newFileName)
        # set the class name in the file to the correct value.
        jmf.replaceTextInFile('class0', newClassName, newFileName)

        # replace fields with field string
        fieldToType = yf.getFieldsAndTypes(model)
        fieldList = fieldToType.keys()
        fieldToPkgtyp = ff.mapFieldsToQualifiedTypes(fieldToType, typToPkgtyp)
        fieldString = ff.createFieldString(fieldToPkgtyp, True)
        #print('fieldString: ' + fieldString)

        for field in fieldList:
            # replace field in annotation
            fieldAnnotation = fieldAnnotations.replace('%', field)
            # replace replacement content in with annotation.
            fieldString = fieldString.replace('&%' + field + '&%', fieldAnnotation)
        fieldString = fieldString.replace('^', '\n')
        #print('fieldString: ' + fieldString)
        # replace annotation
        jmf.replaceTextInFile('    fields', fieldString, newFileName)

    # delete placeholder model
    jmf.deleteFile(templateFile)

    # add addtl dependencies to the pom.
    # if no items in optional dependencyGav, default {} for null safety
    for dependency in descriptor.get('dependencyGav', {}):
        print('adding dependency to pom: ' + dependency)
        jmf.addDependency(projPomPath, yf.getGav(dependency))

    # update imports
    jmf.beautifyImports(projPomPath)

    # verify it compiles
    jmf.callMvnWithOptions(goal='clean install', file=projPomPath)


#!/usr/local/bin/python3

import com.emprogen.java.maven.functions as jmf
import com.emprogen.java.maven.yaml_functions as yf
import com.emprogen.java.maven.field_functions as ff
from com.emprogen.java.maven.models import Gav

# for each document in the yaml file
 # generate the Maven project (build existing java file url.)
 # create new models based on template
  # create the file in same directory as other file.
  # replace the .Java file name with model name
  # replace the fields with a new field string
  # TODO update imports for fields.
 # delete placeholder model


def generate(domainModelDescriptor: 'dict', archetypeGav: 'Gav' = Gav('com.emprogen', 'model-lombok-domain-p0-archetype', '0.0.1')) -> None:

    # Do all 1 time loads and calculations up front.
    # define archetype Gav used for this generator within script.
    archGav = archetypeGav
    # yf.getArchetypeGav(domainModelDescriptor)
    projGav = yf.getGeneratedProjectGav(domainModelDescriptor)
    projPomPath = projGav.artifactId + '/pom.xml'
    modelPath = jmf.getModelPath(projGav)
    templateFile = modelPath + '/class0.java'
    enumTemplateFile = modelPath + '/class1.java'
    typToPkgtyp = ff.getTypeToPkgtypeDict(str(jmf.getFilePath(__file__)) + '/../../../../../java_type.properties')
    # Geneate Maven project.
    jmf.generateMavenProject(archGav, projGav, domainModelDescriptor['author'])

    # for each model file
    for model in domainModelDescriptor['model']:

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

    for enum in domainModelDescriptor['enum']:

        newClassName = enum['name']
        newFileName = modelPath + '/' + newClassName + '.java'
        # create the file, replace name
        jmf.copyFile(enumTemplateFile, newFileName)
        # set the class name in the file to the correct value.
        #TODO check class1 in file to ensure replaced correctly
        jmf.replaceTextInFile('class1', newClassName, newFileName)

        # replace enum paceholder with generated enum values.
        enumValues = yf.getEnumValues(enum)
        enumStr = '    ' + ', '.join(str(a) for a in enumValues)
        jmf.replaceTextInFile(r'    enumerations', enumStr, newFileName)

    # delete placeholder enum
    jmf.deleteFile(enumTemplateFile)

    # update imports
    jmf.beautifyImports(projPomPath)

    # verify it compiles
    jmf.callMvnWithOptions(goal='clean install', file=projPomPath)


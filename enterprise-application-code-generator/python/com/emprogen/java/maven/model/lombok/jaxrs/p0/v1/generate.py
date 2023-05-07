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


def generate(descriptor: 'dict', archetypeGav: 'Gav' = Gav('com.emprogen', 'model-lombok-jaxrs-p0-archetype', '0.0.1')) -> None:

    # Do all 1 time loads and calculations up front.
    # define archetype Gav used for this generator within script.
    archGav = archetypeGav
    projGav = yf.getGeneratedProjectGav(descriptor)
    projPomPath = projGav.artifactId + '/pom.xml'
    modelPath = jmf.getModelPath(projGav)
    templateFile = modelPath + '/class0.java'
    typToPkgtyp = ff.getTypeToPkgtypeDict(jmf.getJavaMavenPath() + '/java_type.properties')
    fieldAnnotations = jmf.getProperty('field', str(jmf.getFilePath(__file__)) + '/jaxrs_field_annotation.properties')
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

    # update imports
    jmf.beautifyImports(projPomPath)

    # verify it compiles
    jmf.callMvnWithOptions(goal='clean install', file=projPomPath)


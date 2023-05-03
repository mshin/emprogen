#!/usr/local/bin/python3

import com.emprogen.java.maven.functions as jmf
import com.emprogen.java.maven.yaml_functions as yf
#import com.emprogen.java.maven.field_functions as ff
import os
import pathlib
from sys import argv
import importlib

if not len(argv) > 1:
    raise ValueError('Must pass yaml descriptor for generating code as arg.')

descriptor = argv[1]
# TODO if directory passed in, iterate over every .yaml and .yml file in the directory and get the documents out to scan.
yamlList= yf.loadYamlDocs(descriptor)

for documentDict in yamlList:
    pass
    # TODO check if the 1st document is a stack descriptor. If so, run
    # TODO validate each document against the schema.yaml.

for documentDict in yamlList:

    # if not a stack descriptor,
    # find the script to run and run it.
    scriptPath = documentDict['id'] + '.generate'
    script = importlib.import_module(scriptPath)
    script.generate(documentDict)
    #script.generate(documentDict, yf.getArchetypeGav(documentDict))


quit()

jmf.replaceTextInFile('abcd', '!!!!', str(getFilePath()) + '/testtmp.txt')
quit()
yamlList= yf.loadYamlDocs('descriptor.yaml')
docDict = yamlList[0]
fntDict0 = yf.getFieldsAndTypes(docDict, 0)
fntDict = yf.getFieldsAndTypes(docDict, modelName = 'JaxrsModel0')
typeToPkgtypeDict = ff.getTypesToPkgtypesDict(str(getFilePath()) + '/../java_type.properties')
print('fntDict: ' + str(fntDict))
fnqtDict = ff.mapFieldsToQualifiedTypes(fntDict, typeToPkgtypeDict)
print('fnqtDict: ' + str(fnqtDict))


print('has run')

x = jmf.lower1st('SPAM')

y = jmf.camelToSnake('MyCamelCase')
print(x)
print(y)

gav = jmf.Gav('g', 'a', 'v')

print(gav)

yamlList= yf.loadYamlDocs('descriptor.yaml')
docDict = yamlList[0]
print('docDict: ' + str(docDict))
archGav = yf.getArchetypeGav(docDict)
projGav = yf.getGeneratedProjectGav(docDict)

#jmf.generateMavenProject(archGav, projGav, docDict['author'])
cwd = os.getcwd()
print ('cwd: ' + str(cwd))
print ('fileDir: ' + str(getFilePath()))

#jmf.addDependency('poma.xml', jmf.Gav('a', 'b', 'c'))

modelPath = jmf.getModelPath(projGav)
print(modelPath)
jmf.beautifyImports(cwd, modelPath)
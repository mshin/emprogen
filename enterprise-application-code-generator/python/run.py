#!/usr/local/bin/python3

import com.emprogen.java.maven.functions as jmf
import com.emprogen.java.maven.yaml_functions as yf
#import com.emprogen.java.maven.field_functions as ff
import os
import pathlib
from sys import argv
import importlib
import com.emprogen.validate_scheama as vs

if not len(argv) > 1:
    raise ValueError('Must pass yaml descriptor for generating code as arg.')

descriptor = argv[1]
# TODO if directory passed in, iterate over every .yaml and .yml file in the directory and get the documents out to scan.
yamlList= yf.loadYamlDocs(descriptor)


# check if the 1st document is a stack descriptor. If so, run
firstDocumentIsStackDescriptor = False

for i, documentDict in enumerate(yamlList):
    # Validate yaml descriptors against their schemas.
    pwd = str(jmf.getFilePath(__file__)) + '/'
    schemaPath = documentDict['id'].replace('.', '/') + '/schema.yaml'
    print('schemaPath: ' + str(schemaPath))
    yamlList = yf.loadYamlDocs(pwd + schemaPath)
    schema = ''
    if yamlList and len(yamlList) > 0:
        schema = yamlList[0]
    # print ('schema: ' + str(schema))

    vs.validate(documentDict, schema)
    if i == 0 and documentDict['id'] == 'idForStackDescriptor':
        firstDocumentIsStackDescriptor = True

if firstDocumentIsStackDescriptor:
    pass
    # TODO run stack descriptor.
quit()
for documentDict in yamlList:
    # if not a stack descriptor,
    # find the script to run and run it.
    scriptPath = documentDict['id'] + '.generate'
    script = importlib.import_module(scriptPath)
    script.generate(documentDict)
    #script.generate(documentDict, yf.getArchetypeGav(documentDict))


quit()



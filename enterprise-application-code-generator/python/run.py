#!/usr/local/bin/python3

import com.emprogen.java.maven.functions as jmf
import com.emprogen.java.maven.yaml_functions as yf
#import com.emprogen.java.maven.field_functions as ff
import os
import pathlib
from sys import argv
import importlib
import com.emprogen.validate_schema as vs

if not len(argv) > 1:
    raise ValueError('Must pass yaml descriptor for generating code as arg.')

# pass 1 arg in to this script.
# Can pass in a single descriptor yaml file.
# Can pass in a directory containing artifacts and /descriptor directory containing yaml documents containing the definitions of the artifacts.
# /descriptor/order.yaml contains the order of the documents to be generated in.

descriptorPath = argv[1]
descriptorDir = descriptorPath + '/descriptor/'
yamlList = []
if os.path.isfile(descriptorPath):
    yamlList = yf.loadYamlDocs(descriptorPath)
# if directory passed in, iterate over every .yaml and .yml file in the directory and get the documents out to scan.
elif os.path.isdir(descriptorDir):
    # if there is an order.txt file, use that as the order in which to read the yaml documents.
    docList = None
    if os.path.isfile(descriptorDir + '/order.txt'):
        with open(descriptorDir + '/order.txt', 'r') as f:
            docList = [line.rstrip() for line in f]
    # get all the files from the directory and add them to the descriptor list.
    fileToPath = {}
    for f in os.listdir(descriptorDir):
        if os.path.isfile(descriptorDir + '/' + f):
            fileToPath[f] = descriptorDir + '/' + f
    # if there's an order.txt file, sort the documents based on that.
    if docList:
        tmpFileToPathDict = {}
        for doc in docList:
            tmpFileToPathDict[doc] = fileToPath.get(doc, None)
        fileToPath = tmpFileToPathDict

    # get the yaml docs and store them from all files into a combined yaml document list.
    for k, v in fileToPath.items(): # after CPython 3.6, dict maintains insertion order
        tmpYamlList = yf.loadYamlDocs(v)
        yamlList += tmpYamlList
else:
    print('Error while loading file descriptors. No descriptors found at expected locations: ' + descriptorPath + ' or: ' + descriptorDir)
    quit()

#print('yamlList: ' + str(yamlList))

# check if the 1st document is a stack descriptor. If so, run
firstDocumentIsStackDescriptor = False

for i, documentDict in enumerate(yamlList):
    # Validate yaml descriptors against their schemas.
    pwd = str(jmf.getFilePath(__file__)) + '/'
    schemaPath = documentDict['id'].replace('.', '/') + '/schema.yaml'
    print('schemaPath: ' + str(schemaPath))
    schemaYamlList = yf.loadYamlDocs(pwd + schemaPath)
    schema = ''
    if schemaYamlList and len(schemaYamlList) > 0:
        schema = schemaYamlList[0]
    # print ('schema: ' + str(schema))

    vs.validate(documentDict, schema)
    if i == 0 and documentDict['id'] == 'idForStackDescriptor':
        firstDocumentIsStackDescriptor = True

if firstDocumentIsStackDescriptor:
    pass
    # TODO run stack descriptor.

for documentDict in yamlList:
    # if not a stack descriptor,
    # find the script to run and run it.
    scriptPath = documentDict['id'] + '.generate'
    print('scriptPath: ' + scriptPath)
    script = importlib.import_module(scriptPath)
    script.generate(documentDict, filesPath = descriptorPath)
    #script.generate(documentDict, yf.getArchetypeGav(documentDict))

quit()



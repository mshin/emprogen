#!/usr/local/bin/python3
from com.emprogen.java.maven.models import Gav
import yaml
import json

def yamlToJson(yamlStr: 'str') -> 'str':
    return json.dumps(yaml.safe_load(yamlStr), indent=2)

def jsonToYaml(jsonStr: 'str') -> 'str':
    return yaml.dump(json.loads(jsonStr), default_flow_style=False)

def loadOpenApi3(docPath: 'str') -> 'dict':
    ext = docPath.split('.')[-1]
    print('ext: ' + ext)
    if ext == 'json':
        with open(docPath) as f:
            return json.load(f)
    elif ext == 'yaml' or ext == 'yml':
        with open(docPath) as f:
            return yaml.safe_load(f)

def loadYamlDocs(projDescLoc: 'str') -> 'list:dict': 
    with open(projDescLoc) as f:
        gen = yaml.safe_load_all(f)
        #file closes before can read all stuff out of gen, so turn to list
        return list(gen)

def getArchetypeGav(yaml: 'dict') -> 'Gav':
    gavStr = yaml['archetypeGAV']
    return getGav(gavStr)

def getGeneratedProjectGav(yaml: 'dict') -> 'Gav':
    gavStr = yaml['generatedGav']
    return getGav(gavStr)

"gavStr is groupId:artifactId:version"
def getGav(gavStr: 'str') -> 'Gav':
    gavList = gavStr.split(':')
    version = None
    if len(gavList) > 2:
        version = gavList[2]
    return Gav(gavList[0], gavList[1], version)

def getFieldsAndTypes(modelDict: 'dict') -> 'dict field:type':
    fieldsDict = {}
    if modelDict:
        fieldList = modelDict['fields']
        for f in fieldList:
            typeToField = f.split(':')
            fieldsDict[typeToField[1]] = typeToField[0]
    # print ('fieldsDict: ' + str(fieldsDict))
    return fieldsDict

def getEnumValues(enumDict: 'dict') -> 'list':
    enumValues = []
    if enumDict:
        enumValues = enumDict['values']
    return enumValues

# "if modelName given, use that. Otherwise, use index. If neither, index=0"
# def getFieldsAndTypes(yaml: 'dict', index: 'int' = 0, *, modelName: 'str' = None) -> 'dict field:type':
#     # get the model list out of the yaml document dictionary
#     modelList = yaml['model']
#
#     if not modelList or not len(modelList):
#         return {}
#     # get the fields list for the model with name modelName
#     modelDict = None
#     fieldsDict = {}
#     if modelName:
#         for d in modelList:
#             if d['name'] == modelName:
#                 modelDict = d
#                 break
#     else:
#         modelDict = modelList[index]
#     # convert the fields list to a dictionary field:type
#     if modelDict:
#         fieldList = modelDict['fields']
#         for f in fieldList:
#             typeToField = f.split(':')
#             fieldsDict[typeToField[1]] = typeToField[0]
#     # print ('fieldsDict: ' + str(fieldsDict))
#     return fieldsDict
# #    dict1 for dict1 in modelList
# #    d = {dict1 for dict1 in modelList if dict1['name'] == modelName}
# #    model = dict1 in modelList where dict1[name] == modelName

print('loaded ' + __file__)
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
        fieldList = modelDict.get('fields', [])
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

print('loaded ' + __file__)
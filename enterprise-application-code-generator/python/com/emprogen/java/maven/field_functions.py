#!/usr/local/bin/python3
import re

"Given a url to .properties file, return the key=value items in a dict."
def loadPropertiesAsDict(propertiesFileUrl: 'str') -> 'dict':

    propertiesDict = {}

    # key is ([^=]+) aka one or more characters starting at the beginning of line that are not equals sign.
    # value is (.*) aka any characters after the first equals sign until the end of the line.
    pattern = re.compile('^([^=]+)=(.*)$')

    with open(propertiesFileUrl) as f:
        keyValueList = f.read().split('\n')

        for line in keyValueList:
            if not line: continue
            if line and line[0] == '#':
                print("got rid of comment: " + str(line))
                continue

            match = re.match(pattern, line)
            if match:
                key = match.group(1)
                value = match.group(2)
                propertiesDict[key] = value
            else:
                e = Exception('Property was not in format k=v.')
                print('file: ' + str(propertiesFileUrl) + '| prop: ' + str(p))
                raise e
    print('propertiesDict: ' + str(propertiesDict))
    return propertiesDict

"Given the field:type and type:pkgtype dictionaries, return a field:pkgtype dict."
def mapFieldsToQualifiedTypes(fieldToType: 'dict', typeToPkgtype: 'dict') -> 'dict':
    output = fieldToType.copy()
    # for each field, get the types.
    for k, v in output.items():
        rawTypes = v.replace('<', ' ').replace('>', ' ').replace(',', ' ').split(' ')
        typesSet = set(rawTypes)
        typesSet.discard('')
        # For each type, map to the package info. 
        typesMap = {}
        for t in typesSet:
            # Make the type set. If it's not there, either:
            # the type doesn't require pkg or it's not in the properties file.
            if typeToPkgtype.__contains__(t):
                typesMap[t] = typeToPkgtype[t]
        # For each type for field, replace with pkgtype.
        # Sorted to prevent replacing parts of words.
        # replacing largest words first should help.
        print('typesMap: ' + str(typesMap))
        for ke in sorted(typesMap.keys(), key=len, reverse=True):
            #for first type in the type map, find occurances in fieldType, replace all.
            # lookahead/behind matches but doesn't include characters in match
            #(?!foo) negative lookahead (match if pattern immediately following is not foo)
            #(?<!foo) negative lookbehind (match if pattern immediately preceeding is not foo)
            #[a-zA-Z\.] match if not a character or a period.
            pattern = re.compile(r'(?<![a-zA-Z\.])(' + ke + r')(?![a-zA-Z])')
            # need to find the last item of all matches first, so replacement doesn't change indexes.
            while True:
                matchList = list(re.finditer(pattern, v))
                if not len(matchList):
                    break
                match = matchList[-1]
                # Replace the type with pkgtype
                v = v[:match.start()] + typesMap[ke] + v[match.end():]
        output[k] = v
    return output

"""Given the field:pkgtype dict, create field str for generated classes. 
Alternatively, add annotation placeholder that must be replaced later."""
def createFieldString(fieldToPkgtype: 'dict', isAddAnnotationPlaceholder: 'bool') -> 'str':
    outputStr = ''
    for field, pkgtype in fieldToPkgtype.items():
        fieldStr = '\n    private ' + pkgtype + ' ' + field + ';\n'
        if isAddAnnotationPlaceholder:
            annotationPlaceholderStr = '\n&%' + field + '&%'
            outputStr += annotationPlaceholderStr + fieldStr
        else:
            outputStr += fieldStr
    return outputStr

"Given fieldList, replace colon with space, add private and semicolon."
def createFieldString2():
    # can't fina a place where this method was called.
    pass

def createFieldStringWithAnnotations():
    # can't fina a place where this method was called.
    pass

print('loaded ' + __file__)
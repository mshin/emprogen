#!/usr/local/bin/python3
import re

"Given a url to the java_types.properties file, return the key=value items in a dict."
def getTypeToPkgtypeDict(javaTypesPropUrl: 'str') -> 'dict':
    # Get the package for each type. Put it in a dict type:pkg.type.
    typesDict = {}
    with open(javaTypesPropUrl) as f:
        rawTypesList = f.read().split('\n')
        print('rawTypesList: ' + str(rawTypesList))
        for p in rawTypesList:
            if not p: continue
            if p and p[0] == '#':
                print("got rid of comment: " + str(p))
                continue
            print(str(p))
            typPkgtyp = p.split('=')
            if len(typPkgtyp) == 2:
                typesDict[typPkgtyp[0]] = typPkgtyp[1]
            else:
                e = Exception('Property was not in format k=v.')
                print('file: ' + str(javaTypesPropUrl) + '| prop: ' + str(p))
                raise e
    print('typesDict: ' + str(typesDict))
    return typesDict

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
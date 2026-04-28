import com.emprogen.java.maven.functions as jmf
import re

def fixNestedEnumClasses(javaClassFiles: 'list') -> None:
    nestedEnumClasses = identifyNestedEnumClasses(javaClassFiles)
    for nestedEnumClassFile, nestedEnumClassContent in nestedEnumClasses.items():
        if isNestedEnumClassMissingClosingBracket(nestedEnumClassContent):
            print('Nested enum class: ' + str(nestedEnumClassFile) + ' ...is missing closing bracket.')
            fixedContents = fixNestedEnumClass(nestedEnumClassContent)
            print('Adding closing bracket to end of file ' + str(nestedEnumClassFile))
            with open(nestedEnumClassFile, 'w') as f:
                f.write(fixedContents)

def identifyNestedEnumClasses(javaClassFiles: 'list') -> 'dict':
    output = {}
    for javaClassFile in javaClassFiles:
        with open(javaClassFile, 'r') as f:
            contents = f.read()
            if jmf.getInFile('(?s)\npublic class .+\n\s*public enum ', javaClassFile):
                output[javaClassFile] = contents

    return output

def fixNestedEnumClass(nestedEnumClassContent: 'str') -> 'str':
    return nestedEnumClassContent + '\n}'

def isNestedEnumClassMissingClosingBracket(nestedEnumClassContent: 'str') -> bool:
    openCurlyBracketCount = len(re.findall(r'\{', nestedEnumClassContent, re.MULTILINE))
    closedCurlyBracketCount = len(re.findall(r'\}', nestedEnumClassContent, re.MULTILINE))
    if openCurlyBracketCount > closedCurlyBracketCount:
        return True
    else:
        return False
#!/usr/local/bin/python3
import re
import subprocess
import os
import xml.etree.ElementTree as et
import glob
import pathlib
import shutil
import importlib
#import com.emprogen.java.maven.yaml_functions as yml
from com.emprogen.java.maven.models import Gav

rgjf = importlib.import_module("com.emprogen.java.run-google-java-format")

def getJavaMavenPath() -> 'str':
    return str(pathlib.Path(__file__).parent.resolve())

def copyFile(src: 'str', dst: 'str') -> None:
    shutil.copy2(src, dst)

def getFilePath(file: '__file__') -> 'str':
    return pathlib.Path(file).parent.resolve()

def lower1st(x: 'str') -> 'str':
    return x[0].lower() + x[1:]

ctsPattern = re.compile(r'(?<!^)(?=[A-Z])')
def camelToSnake(camelString: 'str') -> 'str':
    return ctsPattern.sub('_', camelString).lower()

def getModelPath(gav: 'Gav') -> 'str':
    return gav.artifactId + '/src/main/java/' + gav.groupId.replace('.', '/') + '/' + gav.artifactId.replace('-', '/')

def gjf(javaFiles: 'list; .java files to be formatted with google-java-format') -> None:
    #pathOfCheckGoogleJavaFormatPy = str(pathlib.Path(__file__).parent.parent.resolve()) + '/run-google-java-format.py'
    #print ('pathOfCheckGoogleJavaFormatPy:' + str(pathOfCheckGoogleJavaFormatPy))
    for javaFile in javaFiles:
        rgjf.run(javaFile)
    print('finished formatting ' + str(len(javaFiles)) + ' java files.')

def eclipseFormatterValidate(pathToPom: 'str; path to project pom') -> None:
    validate = 'net.revelc.code.formatter:formatter-maven-plugin:2.23.0:validate'
    print('running maven plugin eclipse formatter:validate at path: ' + pathToPom)

    opts = {'configFile': getJavaMavenPath() + '/mshin_formatter_java.xml'}
    callMvnWithOptions(**opts, goal=validate, file=pathToPom)

def eclipseFormatter(pathToPom: 'str; path to project pom') -> None:
    formatter = 'net.revelc.code.formatter:formatter-maven-plugin:2.23.0:format'
    print('running maven plugin eclipse formatter:format at path: ' + pathToPom)

    opts = {'configFile': getJavaMavenPath() + '/mshin_formatter_java.xml'}
    callMvnWithOptions(**opts, goal=formatter, file=pathToPom)

def beautifyImports(pathToPom: 'str; path to project pom') -> None:
    beautify = 'org.andromda.maven.plugins:andromda-beautifier-plugin:3.4:beautify-imports'
    print('Beautifying imports at path: ' + pathToPom)
    callMvnWithOptions(goal=beautify, file=pathToPom)

    # get all java files
    pomPath = str(pathlib.Path(pathToPom).parent.resolve())
    print('pomPath: ' + pomPath)
    javaFilesList = glob.glob('**/*.java', root_dir=pomPath, recursive=True)
    print('javaFilesList: ' + str(javaFilesList))

    # need to clean \r from all java files due to andromda beautifier
    print('Removing carriage return from files..')
    for file in javaFilesList:
        with open(pomPath + '/' + file, 'r+') as f:
            data = f.read().replace('\r', '')
            f.seek(0)
            f.write(data)
            f.truncate()

def replaceFileContents(content: 'str', filePath: 'str') -> None:
    with open(filePath, 'r+') as f:
        f.seek(0)
        f.write(content)
        f.truncate()

def deleteFile(path: 'str'):
    print('deleting file ' + str(path) + '...')
    pathlib.Path(path).unlink(missing_ok=True)

def getPackage(gav: 'Gav') -> 'str':
    return gav.groupId + '.' + gav.artifactId.replace('-', '.')

"Not efficient for getting multiple properties. Ok for getting 1 property."
def getProperty(prop: 'str', filePath: 'str') -> 'the property; str':
    pattern = re.compile(r'(?<=' + prop + r'=)(.*)')
    output = None
    with open(filePath, 'r') as f:
        fileString = f.read()
        match = re.search(pattern, fileString)
        if match:
            output = match.group()
    return output

def generateMavenProject(archGav: 'Gav', genGav: 'Gav', author: 'str' = None, *, file: 'path to pom' = None,
         **options: 'dict') -> None:
    pkg=getPackage(genGav)
    opts=options
    opts['archetypeGroupId']=archGav.groupId
    opts['archetypeArtifactId']=archGav.artifactId
    opts['archetypeVersion']=archGav.version
    opts['groupId']=genGav.groupId
    opts['artifactId']=genGav.artifactId
    opts['package']=pkg
    if author:
        opts['author']=author
    if genGav.version:
        opts['version']=genGav.version

    callMvnWithOptions(**opts, file=file)

def callMvnWithOptions(*, goal='archetype:generate', file:'path to pom'=None, **options):
    call = 'mvn {} -B'.format(goal)
    if file:
        call +=' -f {}'.format(file)
    argList = call.split()
    for k, v in options.items():
        argStr = '-D{key}={value}'.format(key=k, value=v)
        argList.append(argStr)
    print('maven call: ' + str(argList))
    process = runSubprocess(argList)

def runSubprocess(argList: 'list') -> None:
    print('running subprocess.. \n    ' + str(argList))
    subprocess.run(argList, check=True, text=True)

def runSubprocessCaptureOutput(argList: 'list') -> 'whatever the subprocess would return':
    print('running subprocess.. \n    ' + str(argList))
    return subprocess.run(argList, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout

def addDependency(pomPath: 'str', gav: 'Gav' = Gav(None, None, None)) -> None:
    tree = et.parse(pomPath) #ElementTree
    root = tree.getroot() #Element
    ns = {'x': 'http://maven.apache.org/POM/4.0.0'}
    elem = root.find('./x:dependencies', ns)
    dep = et.Element('dependency')

    groupIdElement = et.Element('groupId')
    groupIdElement.text = gav.groupId
    dep.append(groupIdElement)
    artifactIdElement = et.Element('artifactId')
    artifactIdElement.text = gav.artifactId
    dep.append(artifactIdElement)
    if gav.version:
        versionElement = et.Element('version')
        versionElement.text = gav.version
        dep.append(versionElement)

    elem.append(dep)

    et.indent(tree, space="    ", level=0)
    et.register_namespace('', ns['x'])
    # print('root: ' + str(et.tostring(root)))
    tree.write(pomPath)

def removeDependency(pomPath: 'str', gav: 'Gav' = Gav(None, None, None)) -> None:
    tree = et.parse(pomPath) #ElementTree
    root = tree.getroot() #Element
    ns = {'x': 'http://maven.apache.org/POM/4.0.0'}
    # ./project/dependencies/dependency/groupId[.='io.swagger']/../artifactId[.='swagger-annotations']/..
    #elem = root.find(r"./x:dependencies/x:dependency/x:groupId[.='io.swagger']/../x:artifactId/..", ns)
    elem = root.find("./x:dependencies/x:dependency/x:groupId[.='" + gav.groupId + "']/../x:artifactId[.='" + gav.artifactId + "']/..", ns)
    if gav.version:
        elem = root.find("./x:dependencies/x:dependency/x:groupId[.='" + gav.groupId + "']/../x:artifactId[.='" + gav.artifactId + "']/../x:version[.='" + gav.version + "']/..", ns)

    parentElem = root.find('./x:dependencies', ns)
    parentElem.remove(elem)

    et.indent(tree, space="    ", level=0)
    et.register_namespace('', ns['x'])
    # print('root: ' + str(et.tostring(root)))
    tree.write(pomPath)

# pathToElementList does not contain the element identifier elements, only everything up to that point.
# elementIdentifierDict element:value
def removeXmlElement(filePath: 'str', namespace: 'str', pathToElementList: 'list', elementIdentifierDict: 'dict') -> None:
    tree = et.parse(filePath) #ElementTree
    root = tree.getroot() #Element
    ns = {'x': namespace}

    pathToElement = '.'
    elementIdentifiers = ''
    for e in pathToElementList:
        pathToElement += '/x:' + e
    for e, value in elementIdentifierDict.items():
        elementIdentifiers += '/x:' + e + "[.='" + value + "']/.."
    searchablePath = pathToElement + elementIdentifiers

    elem = root.find(searchablePath, ns)
    parentElem = root.find(searchablePath + '/..', ns)
    parentElem.remove(elem)

    et.indent(tree, space="    ", level=0)
    et.register_namespace('', ns['x'])
    tree.write(filePath)

def removePomProperties(pomPath: 'str', propertiesList: 'list') -> None:
    for prop in propertiesList:
        removeXmlElement(pomPath, 'http://maven.apache.org/POM/4.0.0', ['properties', prop], {})
        print ('removed pom property ' + prop + ' in pom ' + pomPath)

def removePomPlugin(pomPath: 'str', gav: 'Gav' = Gav(None, None, None)) -> None:
    # Not including groupId because some plugins don't include them
    removeXmlElement(pomPath, 'http://maven.apache.org/POM/4.0.0', ['build', 'plugins', 'plugin'], {'artifactId': gav.artifactId})
    print ('removed pom plugin ' + str(gav) + ' in pom ' + pomPath)

def removePomProfile(pomPath: 'str', profileId: 'str') -> None:
    removeXmlElement(pomPath, 'http://maven.apache.org/POM/4.0.0', ['profiles', 'profile'], {'id': profileId})
    print ('removed pom profile ' + profileId + ' in pom ' + pomPath)

def removePomDependencyManagement(pomPath: 'str') -> None:
    removeXmlElement(pomPath, 'http://maven.apache.org/POM/4.0.0', ['dependencyManagement'], {})
    print ('removed dependencyManagement in pom ' + pomPath)

def replaceTextInFileMulti(searchToReplace: 'dict', filePath: 'str path', *, count: 'int' = 0) -> None:
    # Opening the file in read and write mode
    with open(filePath,'r+') as f:

        # Reading the file data and store
        # it in a file variable
        file0 = f.read()

        # Replacing the pattern with the string in the file data for each item in the dict
        for searchText, replaceText in searchToReplace.items():
            file0 = re.sub(searchText, replaceText, file0, count = count)

        # Delete the current content of the file before writing.
        f.truncate(0)

        # Setting the position to the top
        # of the page to insert data
        f.seek(0)

        # Writing replaced data in the file
        f.write(file0)

def replaceTextInFile(searchText: 'str regex', replaceText: 'str', filePath: 'str path', *, count: 'int' = 0) -> None:
    replaceTextInFileMulti({searchText: replaceText}, filePath, count = count)

def addJavaImports(imports: 'str', filePath: 'str path') -> None:
    print('adding imports to file: ' + str(filePath))
    searchText = '\n'
    replaceTextInFile(searchText, '\n\n' + imports + '\n', filePath, count = 1)

def buildAnnotationAttributeReplacementListOfTriples(annotationToSearchToReplace: 'list') -> 'dict':
    output = {}
    for annotation, searchString, replaceString in annotationToSearchToReplace:
        # group 1 before attribute replaced.
        # group 2 after annotation replaced
        # annotation followed by 0 or more whitespace then left parentheses,
        # then 0 or more characters that are not right parentheses,
        # then the attribute to be replaced,
        # then 0 or more whitespace characters followed by '=' followed by 0 or more whitespaces,
        # then 0 or more characters that are not right parentheses, then right parentheses.
        item = '(' + annotation + '\s*\([^\)]*)' + searchString + '(\s*=\s*[^\)]*\))'
        output[item] = replaceString
    print('buildAnnotationAttributeReplacementListOfTriples: ' + str(output))
    return output

print('loaded ' + __file__)

if __name__ == '__main__':
    # test code here
    #callMvnWithOptions(**{'A': 'a', 'B': 'b', 'C': 'c'}, goal='version')
    cwd=os.getcwd()
    print('cwd:' + cwd)
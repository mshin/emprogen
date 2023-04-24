#!/usr/local/bin/python3
import re
import subprocess
import os
import xml.etree.ElementTree as et
import glob
import pathlib
import shutil
#import com.emprogen.java.maven.yaml_functions as yml
from com.emprogen.java.maven.models import Gav

def copyFile(src: 'str', dst: 'str') -> None:
    shutil.copy2(src, dst)

def getFilePath(file: '__file__') -> 'str':
    return pathlib.Path(file).parent.resolve()

def lower1st(x: 'str') -> 'str':
    return x[0].lower() + x[1:]

pattern = re.compile(r'(?<!^)(?=[A-Z])')
def camelToSnake(camelString: 'str') -> 'str':
    return pattern.sub('_', camelString).lower()

def getModelPath(gav: 'Gav') -> 'str':
    return gav.artifactId + '/src/main/java/' + gav.groupId.replace('.', '/') + '/' + gav.artifactId.replace('-', '/')

def beautifyImports(pathToPom: 'str; path to project pom') -> 'None':
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

def deleteFile(path: 'str'):
    print('deleting file ' + str(path) + '...')
    pathlib.Path(path).unlink(missing_ok=True)

def getPackage(gav: 'Gav') -> 'str':
    return gav.groupId + '.' + gav.artifactId.replace('-', '.')

def generateMavenProject(archGav: 'Gav', genGav: 'Gav', author: 'str'=None, 
        *, file:'path to pom'=None) -> None:
    pkg=getPackage(genGav)
    opts={}
    opts['archetypeGroupId']=archGav.groupId
    opts['archetypeArtifactId']=archGav.artifactId
    opts['archetypeVersion']=archGav.version
    opts['groupId']=genGav.groupId
    opts['artifactId']=genGav.artifactId
    opts['package']=pkg
    opts['class0']='class0'
    opts['class1']='class1'
    opts['fields']='fields'
    opts['enumerations']='enumerations'
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
    process = subprocess.run(argList, check=True, text=True)

def addDependency(pomPath: 'str', gav: 'Gav'=Gav(None, None, None)) -> None:
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

    et.indent(tree, space="    ", level=0)
    et.register_namespace('', ns['x'])
    tree.write(pomPath)

def replaceTextInFile(searchText: 'str regex', replaceText: 'str', filePath: 'str path') -> None:
    # Opening the file in read and write mode
    with open(filePath,'r+') as f:
  
        # Reading the file data and store
        # it in a file variable
        file = f.read()
          
        # Replacing the pattern with the string
        # in the file data
        file = re.sub(searchText, replaceText, file)
  
        # Setting the position to the top
        # of the page to insert data
        f.seek(0)
          
        # Writing replaced data in the file
        f.write(file)
  
        # Truncating the file size
        #f.truncate()

print('loaded ' + __file__)

if __name__ == '__main__':
    # test code here
    #callMvnWithOptions(**{'A': 'a', 'B': 'b', 'C': 'c'}, goal='version')
    cwd=os.getcwd()
    print('cwd:' + cwd)
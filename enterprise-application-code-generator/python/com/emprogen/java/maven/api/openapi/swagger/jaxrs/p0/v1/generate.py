import com.emprogen.java.maven.functions as jmf
import com.emprogen.java.maven.yaml_functions as yf
import com.emprogen.java.maven.field_functions as ff
import os
import shutil
from com.emprogen.java.maven.models import Gav
from com.emprogen.java.maven.models import JoinInstruction
from com.emprogen.java.maven.models import TableRelationship

def generate(descriptor: 'dict', *, filesPath: 'str' = None) -> None:

    print('in openapi.jaxrs.generate.py')

    mvnGenGav = Gav('com.emprogen', 'api-openapi-swagger-jaxrs-0-archetype', '0.0.1')

    genGav = yf.getGav(descriptor['generatedGav'])
    package = jmf.getPackage(genGav)
    pathToOpenApi = filesPath + '/' + descriptor['openApiUrl']
    author = descriptor['author']
    pathToPom = None
    # the directory of the java code.
    modelPath = jmf.getModelPath(genGav) + '/model'

    # the directory of the maven pom for the generated code. Usually at the directory root of project.
    projPomPath = genGav.artifactId + '/pom.xml'

    print('genGav: ' + str(genGav))
    print('package: ' + str(package))
    print('pathToOpenApi: ' + str(pathToOpenApi))
    print('pathToPom: ' + str(pathToPom))
    print('author: ' + str(author))
    print('modelPath: ' + str(modelPath))

    # Geneate Maven project.
    opts = {}
    opts['yamlName'] = pathToOpenApi
    opts['apiPackage'] = package
    opts['modelPackage'] = package + '.model'
    opts['generatedGroupId'] = genGav.groupId
    opts['generatedArtifactId'] = genGav.artifactId
    opts['generatedVersion'] = genGav.version
    #jmf.callMvnWithOptions(**opts, goal='clean package', file=pathToPom)
    jmf.generateMavenProject(mvnGenGav, genGav, descriptor['author'], **opts, file=pathToPom)

    print('finished generating generator project.')

    jmf.callMvnWithOptions(goal='clean install', file=projPomPath)

    print('finished generating project.')

    # remove generating pom (rename first)
    os.rename(genGav.artifactId + '/pom.xml', genGav.artifactId + '/pom.xml.generating')

    print('Renamed generating pom.')

    # copy contents to directory.
    genSourcesDir = genGav.artifactId + "/target/generated-sources/openapi"
    shutil.move(genSourcesDir + '/pom.xml', genGav.artifactId + '/pom.xml')
    shutil.move(genSourcesDir + '/src', genGav.artifactId + '/src')

    print('Moved generating sources.')

    # the jaxrs-spec generator is terrible, need to fix some code.
    # delete lines starting with @javax.annotation.Generated in all files.

    #for each model in the model dir
    if os.path.isdir(modelPath):
        for f in os.listdir(modelPath):
            print('file: ' + str(f))
            # get rid of 'false' at end of generated annotation line
            jmf.replaceTextInFile('\n@javax\.annotation\.Generated.*\n', '', modelPath + '/' + f)
            # get rid of broken toString
            with open(modelPath + '/' + f,'r+') as f2:

                print('opened file ' + str(f2))
                # Reading the file data and store
                # it in a file variable
                file0 = f2.read()

                print('file0 read in: ' + str(file0))

                index = file0.find('\n}\n')

                print('index: ' + str(index))
                # Replacing the pattern with the string
                # in the file data
                file0 = file0[:index + 3]

                print('new file0: ' + file0)

                # Setting the position to the top
                # of the page to insert data
                f2.seek(0)
                # Writing replaced data in the file
                f2.truncate()
                f2.write(file0)

    print('Rebuilding project.')
    jmf.callMvnWithOptions(goal='clean install', file=projPomPath)
    print('Finished rebuilding project.')

    print('Removing target directory.')
    jmf.callMvnWithOptions(goal='clean', file=projPomPath)
    print('Removed target directory.')



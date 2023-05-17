import com.emprogen.java.maven.functions as jmf
import com.emprogen.java.maven.yaml_functions as yf
import com.emprogen.java.maven.field_functions as ff
import os
import shutil
from com.emprogen.java.maven.models import Gav
from com.emprogen.java.maven.models import JoinInstruction
from com.emprogen.java.maven.models import TableRelationship

def generate(descriptor: 'dict', *, filesPath: 'str' = None) -> None:

    print('in openapi.java.generate.py')

    mvnGenGav = Gav('com.emprogen', 'api-openapi-java-0-archetype', '0.0.1')

    genGav = yf.getGav(descriptor['generatedGav'])
    package = jmf.getPackage(genGav)
    pathToOpenApi = filesPath + '/' + descriptor['openApiUrl']
    author = descriptor['author']
    pathToPom = None

    # the directory of the maven pom for the generated code. Usually at the directory root of project.
    projPomPath = genGav.artifactId + '/pom.xml'

    print('genGav: ' + str(genGav))
    print('package: ' + str(package))
    print('pathToOpenApi: ' + str(pathToOpenApi))
    print('pathToPom: ' + str(pathToPom))
    print('author: ' + str(author))


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

    print('Rebuilding project.')
    jmf.callMvnWithOptions(goal='clean install', file=projPomPath)
    print('Finished rebuilding project.')

    print('Removing target directory.')
    jmf.callMvnWithOptions(goal='clean', file=projPomPath)
    print('Removed target directory.')

    quit()


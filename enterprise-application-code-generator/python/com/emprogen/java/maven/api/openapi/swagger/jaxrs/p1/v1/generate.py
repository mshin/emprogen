import com.emprogen.java.maven.functions as jmf
import com.emprogen.java.maven.yaml_functions as yf
import com.emprogen.java.maven.field_functions as ff
import os
import shutil
import glob
from com.emprogen.java.maven.models import Gav
from com.emprogen.java.maven.models import JoinInstruction
from com.emprogen.java.maven.models import TableRelationship

# MShin 2023 07: I a stopping development on this. It's too much work to try to get this working.
# Switching over to microprofile annotations.
# Reverting code back to compilable Swagger 2.0. Abandoning OpenAPI 3.0 annotations.
def generate(descriptor: 'dict', *, filesPath: 'str' = None) -> None:

    print('in openapi.jaxrs.generate.py')

    #abandoned
    annotationReplacementDict = {
        r'@Api(?!\w)': '@OpenAPIDefinition',
        r'@ApiModelProperty(?!\w)': '@Schema',
        #r'@ApiModelProperty(?!\w)': '@SchemaProperty',
        r'@ApiModel(?!\w)': '@Schema',
        r'@ApiOperation(?!\w)': '@Operation',
        r'@ApiParam(?!\w)': '@Parameter',
        #r'^import io.swagger.annotations.*;$': '',
        r'import io\.swagger\.annotations\..*\n': ''}
        #r'io.swagger.annotations.[ApiModel;|ApiModelProperty;|Api;|ApiOperation;|ApiParam;]': ''}
    #annotationReplacementDict = {}

     #abandoned
    annotationImportsText = '''import io.swagger.v3.oas.annotations.OpenAPIDefinition;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
'''
#import io.swagger.v3.oas.annotations.media.SchemaProperty;
    
    #abandoned
    #  info = @Info(description = "APIs for booking and managing air flights",
    oneToOneTriples = [ ('@Schema', 'value', 'description'),
            ('ApiOperation', 'value', ''),
            ('ApiOperation', 'notes', ''),
            ('ApiResponse', 'code', '')]
    annotationAttributesReplacementDict = jmf.buildAnnotationAttributeReplacementListOfTriples(oneToOneTriples)

    #abandoned
    nestedTriples = []
        # Schema value description
        # OpenAPIDefinition description info.description
        # ApiOperation value
        # ApiOperation notes
        # ApiResponse code
        # ApiResponse message
        # ApiResponse response

    mvnGenGav = Gav('com.emprogen', 'api-openapi-swagger-jaxrs-0-archetype', '0.0.1')

    openApiGav = Gav('io.swagger.core.v3', 'swagger-annotations', '2.2.10')
    swaggerGav = Gav('io.swagger', 'swagger-annotations', None)

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

    # get all of the java files in generated code so we can process them.
    javaFileList = glob.glob(genGav.artifactId + '/src/main/java/**/*.java', recursive=True)
    print('javaFileList: ' + str(javaFileList))

    # the jaxrs-spec generator is terrible, need to fix some code.
    # delete lines starting with @javax.annotation.Generated in all files.
    for f in javaFileList:
        print('file: ' + str(f))
        # get rid of 'false' at end of generated annotation line
        jmf.replaceTextInFile('\n@javax\.annotation\.Generated.*\n', '',f)
        # get rid of broken toString
        with open(f,'r+') as f2:

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

    #for each model in the model dir
    # if os.path.isdir(modelPath):
    #     for f in os.listdir(modelPath):
    #         print('file: ' + str(f))
    #         # get rid of 'false' at end of generated annotation line
    #         jmf.replaceTextInFile('\n@javax\.annotation\.Generated.*\n', '', modelPath + '/' + f)
    #         # get rid of broken toString
    #         with open(modelPath + '/' + f,'r+') as f2:
    #
    #             print('opened file ' + str(f2))
    #             # Reading the file data and store
    #             # it in a file variable
    #             file0 = f2.read()
    #
    #             print('file0 read in: ' + str(file0))
    #
    #             index = file0.find('\n}\n')
    #
    #             print('index: ' + str(index))
    #             # Replacing the pattern with the string
    #             # in the file data
    #             file0 = file0[:index + 3]
    #
    #             print('new file0: ' + file0)
    #
    #             # Setting the position to the top
    #             # of the page to insert data
    #             f2.seek(0)
    #             # Writing replaced data in the file
    #             f2.truncate()
    #             f2.write(file0)



    # add dependency to pom.. already there?
    # adding up front so if we change annotations the formatter can find the correct jars on classpath.

#    jmf.addDependency(projPomPath, openApiGav)

    # if no items in optional dependencyGav, default {} for null safety
    for dependency in descriptor.get('dependencyGav', {}):
        print('adding dependency to pom: ' + dependency)
        jmf.addDependency(projPomPath, yf.getGav(dependency))

    print('Rebuilding project.')
    jmf.callMvnWithOptions(goal='clean install', file=projPomPath)
    print('Finished rebuilding project.')

    print('Removing target directory.')
    jmf.callMvnWithOptions(goal='clean', file=projPomPath)
    print('Removed target directory.')

    return

    for f in javaFileList:
        # replace swagger2 annotations with openapiAnnotations
        jmf.replaceTextInFileMulti(annotationReplacementDict, f)
        jmf.addJavaImports(annotationImportsText, f)

    #for each model in the model dir
    # if os.path.isdir(modelPath):
    #     for f in os.listdir(modelPath):
    #         # replace swagger2 annotations with openapiAnnotations
    #         jmf.replaceTextInFileMulti(annotationReplacementDict, modelPath + '/' + f)

    #remove swagger2 annotations dependency from pom
    jmf.removeDependency(projPomPath, swaggerGav)

    # if no items in optional dependencyGav, default {} for null safety
    for dependency in descriptor.get('dependencyGav', {}):
        print('adding dependency to pom: ' + dependency)
        jmf.addDependency(projPomPath, yf.getGav(dependency))

    # update imports
    jmf.gjf(javaFileList)
    #jmf.eclipseFormatter(projPomPath)
    #jmf.eclipseFormatterValidate(projPomPath)
    #jmf.beautifyImports(projPomPath)

    print('Rebuilding project 2.')
    jmf.callMvnWithOptions(goal='clean install', file=projPomPath)
    print('Finished rebuilding project 2.')
    exit()
    print('Removing target directory 2.')
    jmf.callMvnWithOptions(goal='clean', file=projPomPath)
    print('Removed target directory 2.')


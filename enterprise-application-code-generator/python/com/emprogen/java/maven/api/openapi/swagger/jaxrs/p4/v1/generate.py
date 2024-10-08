import com.emprogen.java.maven.functions as jmf
import com.emprogen.java.maven.yaml_functions as yf
import com.emprogen.java.maven.field_functions as ff
import os
import shutil
import glob
import re
from com.emprogen.java.maven.models import Gav
from com.emprogen.java.maven.models import JoinInstruction
from com.emprogen.java.maven.models import TableRelationship

def generate(descriptor: 'dict', *, filesPath: 'str' = None, javaVersion: 'str' = '8', jaxrs: 'str' = 'javax') -> None:

    print('in openapi.swagger.jaxrs.p4.v1.generate.py')

    # BEGIN CONSTANTS

    mvnGenGav = None
    javaxGenGav = Gav('com.emprogen', 'api-openapi-swagger-jaxrs-2-archetype', '0.0.2')
    jakartaGenGav = Gav('com.emprogen', 'api-openapi-swagger-jakarta-2-archetype', '0.0.1')

    if 'javax' == jaxrs:
        mvnGenGav = javaxGenGav
    elif 'jakarta' == jaxrs:
        mvnGenGav = jakartaGenGav
    else:
        print('Unsupported jaxrs: ' + str(jaxrs) + '. Must be javax or jakarta.')
        quit(1)

    # openApiGav = Gav('io.swagger.core.v3', 'swagger-annotations', '2.2.10')
    # jmf.addDependency(projPomPath, Gav('javax.annotation', 'javax.annotation-api', '1.3.2'))

    #add these for annotations
    microprofileGav = Gav('org.eclipse.microprofile.openapi', 'microprofile-openapi-api', '1.1.2')
    jakartaValidationGav = Gav('jakarta.validation', 'jakarta.validation-api', '2.0.2')
    jacksonAnnGav = Gav('com.fasterxml.jackson.core', 'jackson-annotations', '2.9.10')
    javaxRsGav = Gav('javax.ws.rs', 'javax.ws.rs-api', '2.1.1')

    microprofileGav2023 = Gav('org.eclipse.microprofile.openapi', 'microprofile-openapi-api', '3.1.1')
    jakartaValidationGav2022 = Gav('jakarta.validation', 'jakarta.validation-api', '3.0.2')
    jacksonAnnGav2023 = Gav('com.fasterxml.jackson.core', 'jackson-annotations', '2.16.1')
    jakartaRsGav2023 = Gav('jakarta.ws.rs', 'jakarta.ws.rs-api', '3.1.0')

    microprofileGav202409 = Gav('org.eclipse.microprofile.openapi', 'microprofile-openapi-api', '4.0')
    jakartaValidationGav202409 = Gav('jakarta.validation', 'jakarta.validation-api', '3.1.0')
    jacksonAnnGav202409 = Gav('com.fasterxml.jackson.core', 'jackson-annotations', '2.17.2')
    jakartaRsGav202409 = Gav('jakarta.ws.rs', 'jakarta.ws.rs-api', '4.0.0')

    jacksonDbndnbGav = Gav('org.openapitools', 'jackson-databind-nullable', '0.2.6')

    # remove these
    swaggerGav = Gav('io.swagger', 'swagger-annotations', None)
    quarkusJunitGav = Gav('io.quarkus', 'quarkus-junit5', None)
    restAssuredGav = Gav('io.rest-assured', 'rest-assured', None)
    quarkusResteasyGav = Gav('io.quarkus', 'quarkus-resteasy', None)
    quarkusSmallryeGav = Gav('io.quarkus', 'quarkus-smallrye-openapi', None)
    removeJavaxRsGav = Gav('javax.ws.rs', 'javax.ws.rs-api', None)
    removeJakartaRsGav = Gav('jakarta.ws.rs', 'jakarta.ws.rs-api', None)
    removeJavaxAnnGav = Gav('javax.annotation', 'javax.annotation-api', None)
    removeJakartaAnnGav = Gav('jakarta.annotation', 'jakarta.annotation-api', None)
    removeJsonNullableGav = Gav('org.openapitools', 'jackson-databind-nullable', None)

    quarkusMavenPluginGav = Gav('io.quarkus', 'quarkus-maven-plugin', None)
    mavenSurefirePluginGav = Gav(None, 'maven-surefire-plugin', None)
    buildHelperMavenPluginGav = Gav('org.codehaus.mojo', 'build-helper-maven-plugin', None)

    pomPropertiesToRemove = ['io.swagger.annotations.version', 'quarkus-plugin.version',
    'quarkus.platform.version', 'quarkus.platform.artifact-id', 'quarkus.platform.group-id',
    'surefire-plugin.version', 'maven.compiler.parameters', 'javax.annotation-api-version',
    'jakarta.annotation-api-version', 'javax.ws.rs-version', 'jakarta.ws.rs-version']

    javaVersionPomProperties = ['maven.compiler.source', 'maven.compiler.target']

    #swagger2 annotations

    swagger2AnnPrefix = 'io.swagger.annotations.'
    swagger2AnnPostfixList = ['Api', 'ApiImplicitParam', 'ApiImplicitParams', 'ApiKeyAuthDefinition',
                              'ApiModel', 'ApiModelProperty', 'ApiModelProperty.AccessMode', 'ApiOperation', 'ApiParam', 'ApiResponse', 
                              'ApiResponses', 'Authorization', 'AuthorizationScope', 'BasicAuthDefinition', 'Contact', 'Example', 'ExampleProperty', 
                              'Extension', 'ExtensionProperty', 'ExternalDocs', 'Info', 'License', 'OAuth2Definition',
                              'ResponseHeader', 'Scope', 'SecurityDefinition', 'SwaggerDefinition', 'Tag']
    swagger2FqdnAnnList = [ swagger2AnnPrefix + x for x in swagger2AnnPostfixList ]
    swagger2ShortAnnList = [ re.search('\w+$', x).group(0) for x in swagger2AnnPostfixList ]
    #print('swagger2FqdnAnnList: ' + str(swagger2FqdnAnnList))#2024
    #print('swagger2ShortAnnList: ' + str(swagger2ShortAnnList))#2024
    # swagger2AnnImportsList = [ 'import ' + x + ';\n' for x in swagger2FqdnAnnList ]
    # swagger2FqdnAnnToShortAnnToImportList = list(zip(swagger2FqdnAnnList, swagger2ShortAnnList, swagger2AnnImportsList))

    # TODO need to fix the swaggerAnnotationReplacemenList to accurately replace what the jaxrs-spec plugin generator generates.
    swaggerAnnotationReplacemenList = []
    for annotation in swagger2ShortAnnList:
        if 'Api' == annotation:
            swaggerAnnotationReplacemenList.append('@' + annotation + r'\(.*?\)')
            swaggerAnnotationReplacemenList.append('@' + annotation + r'\n')
        elif annotation in {'ApiParam', 'ApiImplicitParam'}:
            swaggerAnnotationReplacemenList.append('@' + annotation + r'\(.*?\)')
            swaggerAnnotationReplacemenList.append('@' + annotation)
        else:
            swaggerAnnotationReplacemenList.append('@' + annotation + r'\(*.*\)*\n')

    swaggerAnnotationReplacemenList.append(r'import io\.swagger\.annotations\..*\n')
    #for fqdnAnn in swagger2FqdnAnnList:
    #    swaggerAnnotationReplacemenList.append(fqdnAnn)

    emptyStringList = ['' for x in range(len(swaggerAnnotationReplacemenList))]
    swaggerAnnotationReplacementDict = dict(zip(swaggerAnnotationReplacemenList, emptyStringList))
    swaggerAnnotationReplacementDict[r'\}, tags=\{  \}\)\n'] = ''#2024 fixes an issue where including @Authorization breaks the pattern.
    #print('swaggerAnnotationReplacemenList:' + str(swaggerAnnotationReplacemenList))
    print('swaggerAnnotationReplacementDict:' + str(swaggerAnnotationReplacementDict))#2024

    # try not to use annotations that are not in both! standards split is not good.
    #media.ArraySchema (only in swagger, not microprofile)

    mpAnnPrefix = 'org.eclipse.microprofile.openapi.annotations.'
    mpAnnPostfixList = ['Extension', 'License', 'Components', 'ExternalDocumentation', 'OpenAPIDefinition',
    'Operation', 'callbacks.Callback', 'callbacks.CallbackOperation', 'callbacks.Callbacks',
    'enums.Explode', 'enums.ParameterIn', 'enums.ParameterStyle', 'enums.SchemaType',
    'enums.SecuritySchemeIn', 'enums.SecuritySchemeType', 'extensions.Extension',
    'extensions.Extensions', 'headers.Header', 'info.Contact', 'info.Info', 'info.License',
    'links.Link', 'links.LinkParameter', 'media.Schema.False', 'media.Schema.True', 'media.Content',
    'media.DiscriminatorMapping', 'media.Encoding', 'media.ExampleObject', 'media.Schema',
    'media.SchemaProperty', 'parameters.Parameter', 'parameters.Parameters', 'parameters.RequestBody',
    'parameters.RequestBodySchema', 'responses.APIResponse', 'responses.APIResponses',
    'responses.APIResponseSchema', 'security.OAuthFlow', 'security.OAuthFlows',
    'security.OAuthScope', 'security.SecurityRequirement', 'security.SecurityRequirements',
    'security.SecurityRequirementsSet', 'security.SecurityRequirementsSets', 'security.SecurityScheme',
    'security.SecuritySchemes', 'servers.Server', 'servers.Servers', 'servers.ServerVariable',
    'tags.Tag', 'tags.Tags']
    mpFqdnAnnList = [ mpAnnPrefix + x for x in mpAnnPostfixList ]
    mpShortAnnList = [ re.search('\w+$', x).group(0) for x in mpAnnPostfixList ]
    mpAnnImportsList = [ 'import ' + x + ';\n' for x in mpFqdnAnnList ]
    mpFqdnAnnToShortAnnToImportList = list(zip(mpFqdnAnnList, mpShortAnnList, mpAnnImportsList))

    # END CONSTANTS

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
    # delete lines starting with @javax.annotation.Generated (OR @jakarta.annotation.Generated) in all files.
    for f in javaFileList:
        print('file: ' + str(f))
        # get rid of 'false' at end of generated annotation line
        jmf.replaceTextInFile('\n@(javax|jakarta)\.annotation\.Generated.*\n', '',f)
        # get rid of broken toString
        with open(f,'r+') as f2:

            #print('opened file ' + str(f2))
            # Reading the file data and store
            # it in a file variable
            file0 = f2.read()

            #print('file0 read in: ' + str(file0))

            index = file0.find('\n}\n')

            #print('index: ' + str(index))
            # Replacing the pattern with the string
            # in the file data
            file0 = file0[:index + 3]

            #print('new file0: ' + file0)

            # Setting the position to the top
            # of the page to insert data
            f2.seek(0)
            # Writing replaced data in the file
            f2.truncate()
            f2.write(file0)

    # if no items in optional dependencyGav, default {} for null safety
    for dependency in descriptor.get('dependencyGav', {}):
        print('adding dependency to pom: ' + dependency)
        jmf.addDependency(projPomPath, yf.getGav(dependency))

    #add openapi microprofile (openapi3) annotations
    jmf.addDependency(projPomPath, microprofileGav)

    #add jackson-databind-nullable because generator likes to sometimes throw that in there for no reason.
    jmf.addDependency(projPomPath, jacksonDbndnbGav)

    # Delete old generating pom file.
    jmf.deleteFile(projPomPath + '.generating')

    print('Rebuilding project.')
    jmf.callMvnWithOptions(goal='clean install', file=projPomPath)
    print('Finished rebuilding project.')

    print('Removing target directory.')
    jmf.callMvnWithOptions(goal='clean', file=projPomPath)
    print('Removed target directory.')

    for f in javaFileList:
        # remove swagger2 annotations
        jmf.replaceTextInFileMulti(swaggerAnnotationReplacementDict, f)

    # collapse microprofile openapi annotations
    for f in javaFileList:
        with open(f,'r+') as fopen:

            # Reading the file data and store it in a file variable
            file0 = fopen.read()

            # Replacing the pattern with the string in the file data for each item in the dict
            for searchText, replaceText, importStatement in mpFqdnAnnToShortAnnToImportList:
                annSubResult = re.subn(searchText + r'(?!\w)', replaceText, file0, count = 0) # 0 means replace as many as you can find
                file0 = annSubResult[0]
                numberOfReplacementsMade = annSubResult[1]
                # if a replacement was made, insert the corresponding import statement at top of file.
                if numberOfReplacementsMade > 0:
                    print('file: ' + str(f) + ' ... annotation searched: ' + replaceText + ' ... results found: ' + str(numberOfReplacementsMade))
                    file0 = re.sub('\n', '\n' + importStatement, file0, count = 1)

            # Delete the current content of the file before writing.
            fopen.truncate(0)
            # Setting the position to the top of the page to insert data
            fopen.seek(0)
            # Writing replaced data in the file
            fopen.write(file0)

    # remove poorly generated content: tag stubs
    # add back in stripped OpenAPI3 data: info.description, securityRequirement.scopes, tags
    # load openapi spec doc and transverse to get content for reintroduction

    # remove any \n@Tag
    # remove any tags = stuff
    tagDict = {'\n@Tag.*\n': '\n', '@Tag.*\)\n': '{@%@}\n'}
    for f in javaFileList:
        jmf.replaceTextInFileMulti(tagDict, f)

    # get values from OpenAPI3 spec doc
    oa3dict = yf.loadOpenApi3(pathToOpenApi)

    infoTitle = oa3dict.get("info", {}).get("title", "")
    infoDescription = oa3dict.get("info", {}).get("description", "")
    tagsList = oa3dict.get("tags", "")
    # schemesList = []
    # securitySchemesDict = oa3dict.get("components", {}).get("securitySchemes", "")
    # if isinstance(securitySchemesDict, dict):
    #     schemesList = securitySchemesDict.keys()
    # pathMethodToExampleDict = {}
    methodSecuritySchemeScopes = [] #list:dict:list
    # print('oa3dict: ' + str(oa3dict))
    oas3HttpMethods = {'get', 'put', 'post', 'delete', 'options', 'head', 'patch', 'trace'}
    for k, v in oa3dict.get("paths", {}).items():
        for k2, v2 in v.items():
            if k2 in oas3HttpMethods:
                methodSecuritySchemeScopes.append({k + ' ' + k2: v2.get("security", "")})
                # examplesDict = v2.get("requestBody", {}).get("content", {}).get("application/json", {}).get("examples", {})
                # if len(examplesDict) > 0:
                    # pathMethodToExampleDict[k + ' ' + k2] = examplesDict

    # print('infoTitle: ' + str(infoTitle))
    # print('infoDescription: ' + str(infoDescription))
    # print('tagsList: ' + str(tagsList))
    # print('schemesList: ' + str(schemesList))
    # print('methodSecuritySchemeScopes: ' + str(methodSecuritySchemeScopes))
    # print('pathMethodToExampleDict: ' + str(pathMethodToExampleDict))

    # add title back in
    for f in javaFileList:
        jmf.replaceTextInFile('(@OpenAPIDefinition(\n|.)*@Info(\n|.)*title\s?=\s?)""', r'\g<1>"' + infoTitle + '"', f)
    # add openapidefinition info description back in
    for f in javaFileList:
        jmf.replaceTextInFile('(@OpenAPIDefinition(\n|.)*@Info(\n|.)*title\s?=\s?".*"(\n|.)*version\s?=\s?".*"(\n|.)*description\s?=\s?)""(?!\))', r'\g<1>"' + infoDescription + '"', f)

    # add tags back in
    tagAnnotations = ""
    for index, tag in enumerate(tagsList):
        tagAnnotations += '@Tag(name="' + tag.get("name", "") + '", description="' + tag.get("description", "") + '")'
        if index < len(tagsList) - 1:
            tagAnnotations += ', '

    for f in javaFileList:
        jmf.replaceTextInFile('(tags\s?=\s?\{)@%@\}', r'\g<1>' + tagAnnotations +  '}', f)


    # add security scopes in.

    # iterate over each of the methodSecuritySchemeScopes, if scheme scopes list > 0... find the annotations in java code and add scopes.
    for scope in methodSecuritySchemeScopes:
        for url_httpMethod, securitySchemeList in scope.items():
            url = url_httpMethod.split(' ')[0]
            httpMethod = url_httpMethod.split(' ')[1].upper()
            for securityScheme in securitySchemeList:
                for securitySchemeName, scopes in securityScheme.items():
                    if len(scopes) > 0:
                        for f in javaFileList:
                            fileString = ''
                            with open(f, 'r') as fil:
                                fileString = fil.read()
                            updateFile = False
                            rootPathAnnotation = jmf.getInFile('@Path\s*\(\s*"(.*)"\s*\)(\n|.)*public\s+(interface|class)', f)
                            rootPath = ''
                            if None != rootPathAnnotation:
                                print('rootPathAnnotation: ' + str(rootPathAnnotation) + ' in file: ' + str(f))
                                rootPathMatches = re.search('@Path\s*\(\s*"(.*)"\s*\)', rootPathAnnotation, re.MULTILINE)
                                if None != rootPathMatches:
                                    rootPath = rootPathMatches.group(1)
                                print('rootPath: ' + str(rootPath))
                            # for each method in the file, find path and httpMethod
                            matchIter = re.finditer('@(POST|PUT|GET|DELETE|PATCH|OPTIONS|HEAD|TRACE|CONNECT)\s+(@Path\s*\(\s*"(.*)"\s*\))?', fileString, re.MULTILINE)
                            for match in matchIter:
                                if None != match:
                                    #print('match: ' + repr(match))
                                    matchHttpMethod = match.group(1)
                                    matchRelativePath = match.group(3)
                                    matchRelativePath = matchRelativePath if matchRelativePath != None else ''
                                    matchPath = rootPath + matchRelativePath
                                    matchUrl_httpMethod = matchPath + ' ' + matchHttpMethod
                                    compareUrl_httpMethod = url + ' ' + httpMethod
                                    #print('matchUrl_httpMethod: ' + str(matchUrl_httpMethod))
                                    #print('compareUrl_httpMethod: ' + str(compareUrl_httpMethod))
                                    if matchUrl_httpMethod == compareUrl_httpMethod:
                                        print('matchUrl_httpMethod: ' + str(matchUrl_httpMethod) + ' == ' + str(compareUrl_httpMethod))
                                        # find the method with the url_httpMethod and add the scopes to the securityRequirement annotation.
                                        searchText = '(@' + matchHttpMethod + r'(\n|.)+' + matchRelativePath.replace('/', '\/') + r'(\n|.)*@SecurityRequirement\s?\(\s?name\s?=\s?"' + securitySchemeName + '"\s?)\)'
                                        print('searchText: ' + str(searchText))
                                        replaceText = r'\g<1>, scopes = {"' + '", "'.join(scopes) + '"})'
                                        print('replaceText: ' + str(replaceText))
                                        fileString = re.sub(searchText, replaceText, fileString, count = 1)
                                        updateFile = True

                            # write file to disk
                            if updateFile:
                                with open(f, 'w') as fil:
                                    fil.write(fileString)
                                    print('file updated: ' + str(f) + ' at ' + url_httpMethod + ' with scopes: ' + str(scopes))

    # TODO add examples back in


    # remove swagger2 annotations dependency from pom
    jmf.removeDependency(projPomPath, swaggerGav)
    # Trim down pom by removing all unnecessary transitive dependencies.
    # Only keep mandatory dependencies, mostly annotation libraries.
    jmf.removeDependency(projPomPath, quarkusJunitGav)
    jmf.removeDependency(projPomPath, restAssuredGav)
    jmf.removeDependency(projPomPath, quarkusResteasyGav)
    jmf.removeDependency(projPomPath, quarkusSmallryeGav)
    jmf.removeDependency(projPomPath, removeJavaxRsGav)
    jmf.removeDependency(projPomPath, removeJavaxAnnGav)
    jmf.removeDependency(projPomPath, removeJakartaAnnGav)
    jmf.removeDependency(projPomPath, removeJakartaRsGav)
    # removing json-nullable... hopefully never need.
    jmf.removeDependency(projPomPath, removeJsonNullableGav)

    # trim excess fat from generated pom, including properties, plugins and profiles.
    jmf.removePomPlugin(projPomPath, quarkusMavenPluginGav)
    jmf.removePomPlugin(projPomPath, mavenSurefirePluginGav)
    jmf.removePomPlugin(projPomPath, buildHelperMavenPluginGav)
    jmf.removePomProfile(projPomPath, 'native')
    jmf.removePomDependencyManagement(projPomPath)
    jmf.removePomProperties(projPomPath, pomPropertiesToRemove)
    jmf.removePomProperties(projPomPath, javaVersionPomProperties)

    # jmf.addDependency(projPomPath, jacksonDbndnbGav)
    # Find correct dependencies to add based on combination of jaxrs and java version
    if '17' == javaVersion:
        jmf.addDependency(projPomPath, microprofileGav202409)
        jmf.addDependency(projPomPath, jakartaValidationGav202409)
        jmf.addDependency(projPomPath, jacksonAnnGav202409)
        jmf.addDependency(projPomPath, jakartaRsGav202409)
    elif '11' == javaVersion:
        jmf.addDependency(projPomPath, microprofileGav2023)
        jmf.addDependency(projPomPath, jakartaValidationGav2022)
        jmf.addDependency(projPomPath, jacksonAnnGav2023)
        jmf.addDependency(projPomPath, jakartaRsGav2023)
    elif '8' == javaVersion:
        jmf.addDependency(projPomPath, microprofileGav)
        jmf.addDependency(projPomPath, jakartaValidationGav)
        jmf.addDependency(projPomPath, jacksonAnnGav)
    else:
        print('Unsupported java version: ' + str(javaVersion))
        quit(1)


    if 'javax' == jaxrs:
        jmf.addDependency(projPomPath, javaxRsGav)
        print('Only Java version 8 supported with javax jaxrs. Setting java version to 8 if it is not otherwise. If you want to use a different version of Java, you must use jakarta jaxrs.')
        javaVersion = '8'
    elif 'jakarta' == jaxrs:
        jmf.addDependency(projPomPath, jakartaRsGav2023)
        jmf.removeDependency(projPomPath, jakartaValidationGav)
        jmf.addDependency(projPomPath, jakartaValidationGav2022)
    else:
        print('Unsupported jaxrs: ' + str(jaxrs))
        quit(1)

    # set java version to javaVersion
    jmf.addPomProperties(projPomPath, dict(zip(javaVersionPomProperties, [javaVersion, javaVersion])))

    # update imports
    #jmf.gjf(javaFileList)
    jmf.eclipseFormatter(projPomPath)
    #jmf.eclipseFormatterValidate(projPomPath)
    #jmf.beautifyImports(projPomPath)

    # create src/main/resources/META-INF/beans.xml
    jmf.makeFile(genGav.artifactId + '/src/main/resources/META-INF/', 'beans.xml') 

    # remove docker folder
    jmf.deleteDirectory(genGav.artifactId + '/src/main/docker')

    # rename src/main/openapi/openapi.yaml to real doc name
    oapidocPath = genGav.artifactId + '/src/main/openapi'
    jmf.copyFile(oapidocPath + '/openapi.yaml', oapidocPath + '/' + os.path.basename(pathToOpenApi))
    jmf.deleteFile(oapidocPath + '/openapi.yaml')

    print('Rebuilding project 2.')
    jmf.callMvnWithOptions(goal='clean install', file=projPomPath)
    print('Finished rebuilding project 2.')

    print('Removing target directory 2.')
    jmf.callMvnWithOptions(goal='clean', file=projPomPath)
    print('Removed target directory 2.')

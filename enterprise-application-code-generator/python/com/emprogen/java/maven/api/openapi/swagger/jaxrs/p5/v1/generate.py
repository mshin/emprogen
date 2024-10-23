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

def generate(descriptor: 'dict', *, files_path: 'str' = None, java_version: 'str' = '8', jaxrs: 'str' = 'javax') -> None:

    print('in openapi.swagger.jaxrs.p5.v1.generate.py')

    # BEGIN CONSTANTS
    
    mvn_gen_gav = None
    javax_gen_gav = Gav('com.emprogen', 'api-openapi-swagger-jaxrs-2-archetype', '0.0.2')
    jakarta_gen_gav = Gav('com.emprogen', 'api-openapi-swagger-jakarta-3-archetype', '0.0.1')

    if 'javax' == jaxrs:
        mvn_gen_gav = javax_gen_gav
    elif 'jakarta' == jaxrs:
        mvn_gen_gav = jakarta_gen_gav
    else:
        print('Unsupported jaxrs: ' + str(jaxrs) + '. Must be javax or jakarta.')
        quit(1)

    #add these for annotations
    microprofile_gav = Gav('org.eclipse.microprofile.openapi', 'microprofile-openapi-api', '1.1.2')
    jakarta_validation_gav = Gav('jakarta.validation', 'jakarta.validation-api', '2.0.2')
    jackson_ann_gav = Gav('com.fasterxml.jackson.core', 'jackson-annotations', '2.9.10')
    javax_rs_gav = Gav('javax.ws.rs', 'javax.ws.rs-api', '2.1.1')

    microprofile_gav_2023 = Gav('org.eclipse.microprofile.openapi', 'microprofile-openapi-api', '3.1.1')
    jakarta_validation_gav_2022 = Gav('jakarta.validation', 'jakarta.validation-api', '3.0.2')
    jackson_ann_gav_2023 = Gav('com.fasterxml.jackson.core', 'jackson-annotations', '2.16.1')
    jakarta_rs_gav_2023 = Gav('jakarta.ws.rs', 'jakarta.ws.rs-api', '3.1.0')

    microprofile_gav_202409 = Gav('org.eclipse.microprofile.openapi', 'microprofile-openapi-api', '4.0')
    jakarta_validation_gav_202409 = Gav('jakarta.validation', 'jakarta.validation-api', '3.1.0')
    jackson_ann_gav_202409 = Gav('com.fasterxml.jackson.core', 'jackson-annotations', '2.17.2')
    jakarta_rs_gav_202409 = Gav('jakarta.ws.rs', 'jakarta.ws.rs-api', '4.0.0')

    jackson_dbndnb_gav = Gav('org.openapitools', 'jackson-databind-nullable', '0.2.6')

    # remove these
    swagger_gav = Gav('io.swagger', 'swagger-annotations', None)
    quarkus_junit_gav = Gav('io.quarkus', 'quarkus-junit5', None)
    rest_assured_gav = Gav('io.rest-assured', 'rest-assured', None)
    quarkus_resteasy_gav = Gav('io.quarkus', 'quarkus-resteasy', None)
    quarkus_smallrye_gav = Gav('io.quarkus', 'quarkus-smallrye-openapi', None)
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
    pathToOpenApi = files_path + '/' + descriptor['openApiUrl']
    author = descriptor['author']
    pathToPom = None
    # the directory of the java code.
    modelPath = jmf.getModelPath(genGav) + '/model'

    # the directory of the maven pom for the generated code. Usually at the directory root of project.
    projPomPath = genGav.artifactId + '/pom.xml'

    # load OpenAPI3 spec doc, so can get values out
    oa3dict = yf.loadOpenApi3(pathToOpenApi)

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
    jmf.generateMavenProject(mvn_gen_gav, genGav, descriptor['author'], **opts, file=pathToPom)

    print('finished generating generator project.')

    jmf.callMvnWithOptions(goal='clean install', file=projPomPath)

    print('finished generating project.')
    #quit(0)
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
    # TODO adding oldest version of microprofile annotations here; maybe check version needed before this point.
    jmf.addDependency(projPomPath, microprofile_gav)

    #add jackson-databind-nullable because generator likes to sometimes throw that in there for no reason.
    jmf.addDependency(projPomPath, jackson_dbndnb_gav)

    #fix oneOf interface generated class
    # if oneof in schema:
    # find class with oneOf
    # delete contents after public class declaration line.
    # change class to interface.
    # if descriminator, find and get description, name, type.
    # add annotations with name, description.
    # add public abstract method, with return type, with converted to camel case.
    # add closing class bracket (\n\n}\n)
    model_dict = oa3dict.get("components", {}).get("schemas", {})
    interfaces_dict = {}
    for model_name, model in model_dict.items():
        if 'oneOf' in model:
            print('model_name: ' + str(model_name))
            print('model: ' + str(model))
            interfaces_dict[model_name] = model
    
    # Get the list of the simple java file names
    java_file_simple_names = [os.path.basename(f) for f in javaFileList]
    java_file_simple_names_to_path = dict(zip(java_file_simple_names, javaFileList))
    # For each model that should be an interface, start making it an interface
    for model_name, model in interfaces_dict.items():
        # Get the file path for the model that should be an interface
        interface_file_path = java_file_simple_names_to_path[model_name + '.java']
        regex = r'public\s*?class\s*?' + model_name + r'\s*?\{\n(\n|.)+' # find the class declaration; match everything after it.
        replacement = 'public interface ' + model_name + ' {\n'
        model_description = model.get('description', None)
        print('model_description: ' + str(model_description))
        model_discriminator = model.get('discriminator', None)
        print('model_discriminator: ' + str(model_discriminator))
        model_subclasses = model.get('oneOf', [])
        print('model_subclasses: ' + str(model_subclasses))
        model_discriminator_name = None
        model_discriminator_type = None
        # If there is a discriminator, get info so an abstract method can be added to the interface.
        if model_discriminator:
            model_discriminator_name = model_discriminator.get('propertyName', None)
            model_subclass_path = model_subclasses[0].get('$ref', '')
            
            subclass0_name = model_subclass_path.split('/')[-1]

            print('subclass0_name: ' + str(subclass0_name))

            subclass0 = model_dict.get(subclass0_name, None)

            print('subclass0: ' + str(subclass0))
            print('model_subclasses[0]: ' + str(model_subclasses[0]))

            if subclass0:
                descriminator_property = subclass0.get('properties', {}).get(model_discriminator_name, {})
                discriminator_type = descriminator_property.get('type', None)
                descriminator_ref = descriminator_property.get('$ref', None)
                if descriminator_ref:
                    model_discriminator_type = descriminator_ref.split('/')[-1]
                elif discriminator_type:
                    model_discriminator_type = discriminator_type
                else:
                    print('Could not find discriminator ' + model_discriminator_name + ' type.')
                    quit(1)
            print('model_discriminator_name: ' + str(model_discriminator_name))

            replacement += '\n\n    @org.eclipse.microprofile.openapi.annotations.media.Schema(required = true)\n'
            replacement += '    @JsonProperty("' + model_discriminator_name + '")\n'
            replacement += '    @NotNull public abstract ' + model_discriminator_type + ' ' + 'get'
            replacement += jmf.toCamel(model_discriminator_name, False) + '();\n'

        replacement += '\n}\n'
        jmf.replaceTextInFile(regex, replacement, interface_file_path)

        # remove package imports from same package?!
        package_pattern = r'(?<=package\s).+(?=;)'
        package_string = jmf.getInFile(package_pattern, interface_file_path)
        jmf.replaceTextInFile('import ' + package_string + '.*;\n', '', interface_file_path)

    # comment out @ApplicationPath (causing quarkus error)
    rest_application_file = java_file_simple_names_to_path.get('RestApplication.java', {})
    jmf.replaceTextInFile(r'@ApplicationPath', r'//@ApplicationPath', rest_application_file)
    jmf.replaceTextInFile(r'extends Application \{', r'{ // extends Application', rest_application_file)
    print('rest_application_file: ' + str(rest_application_file))

    # Delete old generating pom file.
    jmf.deleteFile(projPomPath + '.generating')

    print('Rebuilding project.')
    jmf.callMvnWithOptions(goal='clean install', file=projPomPath)
    print('Finished rebuilding project.')

    print('Removing target directory.')
    jmf.callMvnWithOptions(goal='clean', file=projPomPath)
    print('Removed target directory.')

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
    jmf.removeDependency(projPomPath, swagger_gav)
    # Trim down pom by removing all unnecessary transitive dependencies.
    # Only keep mandatory dependencies, mostly annotation libraries.
    jmf.removeDependency(projPomPath, quarkus_junit_gav)
    jmf.removeDependency(projPomPath, rest_assured_gav)
    jmf.removeDependency(projPomPath, quarkus_resteasy_gav)
    jmf.removeDependency(projPomPath, quarkus_smallrye_gav)
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

    # must remove default microprofile_gav before adding version correct one.
    jmf.removeDependency(projPomPath, microprofile_gav)
    # jmf.addDependency(projPomPath, jackson_dbndnb_gav)
    # Find correct dependencies to add based on combination of jaxrs and java version
    if '17' == java_version:
        jmf.addDependency(projPomPath, microprofile_gav_202409)
        jmf.addDependency(projPomPath, jakarta_validation_gav_202409)
        jmf.addDependency(projPomPath, jackson_ann_gav_202409)
        jmf.addDependency(projPomPath, jakarta_rs_gav_202409)
    elif '11' == java_version:
        jmf.addDependency(projPomPath, microprofile_gav_2023)
        jmf.addDependency(projPomPath, jakarta_validation_gav_2022)
        jmf.addDependency(projPomPath, jackson_ann_gav_2023)
        jmf.addDependency(projPomPath, jakarta_rs_gav_2023)
    elif '8' == java_version:
        jmf.addDependency(projPomPath, microprofile_gav)
        jmf.addDependency(projPomPath, jakarta_validation_gav)
        jmf.addDependency(projPomPath, jackson_ann_gav)
    else:
        print('Unsupported java version: ' + str(java_version))
        quit(1)

    if 'javax' == jaxrs:
        jmf.addDependency(projPomPath, javax_rs_gav)
        print('Only Java version 8 supported with javax jaxrs. Setting java version to 8 if it is not otherwise. If you want to use a different version of Java, you must use jakarta jaxrs.')
        java_version = '8'
    elif 'jakarta' == jaxrs:
        None
    else:
        print('Unsupported jaxrs: ' + str(jaxrs))
        quit(1)

    # set java version to java_version
    jmf.addPomProperties(projPomPath, dict(zip(javaVersionPomProperties, [java_version, java_version])))

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

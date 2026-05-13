import com.emprogen.java.maven.functions as jmf
import com.emprogen.java.maven.yaml_functions as yf
import com.emprogen.java.maven.field_functions as ff
import com.emprogen.prepend_license as pl
import com.emprogen.java.maven.api.openapi.swagger.jaxrs.fix_nested_enum as fne
import os
import shutil
import glob
import re
from com.emprogen.java.maven.models import Gav
from com.emprogen.java.maven.models import JoinInstruction
from com.emprogen.java.maven.models import TableRelationship

def generate(descriptor: 'dict', *, files_path: 'str' = None, java_version: 'str' = '8', jaxrs: 'str' = 'javax', **kwargs) -> None:

    print('in openapi.swagger.jaxrs.p5.v1.generate.py')

    # BEGIN CONSTANTS

    mvn_gen_gav = None
    javax_gen_gav = kwargs.get('javax_gen_gav', Gav('com.emprogen', 'api-openapi-swagger-jaxrs-2-archetype', '0.0.2'))
    jakarta_gen_gav = kwargs.get('jakarta_gen_gav', Gav('com.emprogen', 'api-openapi-swagger-jakarta-3-archetype', '0.0.1'))

    if 'javax' == jaxrs:
        mvn_gen_gav = javax_gen_gav
    elif 'jakarta' == jaxrs:
        mvn_gen_gav = jakarta_gen_gav
    else:
        print('Unsupported jaxrs: ' + str(jaxrs) + '. Must be javax or jakarta.')
        quit(1)

    #add these for annotations (defaults are approx java 8 era versions)
    microprofile_gav = kwargs.get('microprofile_gav', Gav('org.eclipse.microprofile.openapi', 'microprofile-openapi-api', '1.1.2'))
    jakarta_validation_gav = kwargs.get('jakarta_validation_gav', Gav('jakarta.validation', 'jakarta.validation-api', '3.0.2'))
    jackson_ann_gav = kwargs.get('jackson_ann_gav', Gav('com.fasterxml.jackson.core', 'jackson-annotations', '2.9.10'))
    javax_rs_gav = kwargs.get('javax_rs_gav', Gav('javax.ws.rs', 'javax.ws.rs-api', '2.1.1'))
    jakarta_rs_gav = kwargs.get('jakarta_rs_gav', Gav('jakarta.ws.rs', 'jakarta.ws.rs-api', '3.1.0'))

    jackson_dbndnb_gav = kwargs.get('jackson_dbndnb_gav', Gav('org.openapitools', 'jackson-databind-nullable', '0.2.6'))

    # remove these
    swagger_gav = kwargs.get('swagger_gav', Gav('io.swagger', 'swagger-annotations', None))
    quarkus_junit_gav = kwargs.get('quarkus_junit_gav', Gav('io.quarkus', 'quarkus-junit5', None))
    rest_assured_gav = kwargs.get('rest_assured_gav', Gav('io.rest-assured', 'rest-assured', None))
    quarkus_resteasy_gav = kwargs.get('quarkus_resteasy_gav', Gav('io.quarkus', 'quarkus-resteasy', None))
    quarkus_smallrye_gav = kwargs.get('quarkus_smallrye_gav', Gav('io.quarkus', 'quarkus-smallrye-openapi', None))
    remove_javax_rs_gav = kwargs.get('removeJavaxRsGav', Gav('javax.ws.rs', 'javax.ws.rs-api', None))
    remove_jakarta_rs_gav = kwargs.get('removeJakartaRsGav', Gav('jakarta.ws.rs', 'jakarta.ws.rs-api', None))
    remove_javax_ann_gav = kwargs.get('removeJavaxAnnGav', Gav('javax.annotation', 'javax.annotation-api', None))
    remove_jakarta_ann_gav = kwargs.get('removeJakartaAnnGav', Gav('jakarta.annotation', 'jakarta.annotation-api', None))
    remove_json_nullable_gav = kwargs.get('removeJsonNullableGav', Gav('org.openapitools', 'jackson-databind-nullable', None))

    quarkus_maven_plugin_gav = kwargs.get('quarkusMavenPluginGav', Gav('io.quarkus', 'quarkus-maven-plugin', None))
    maven_surefire_plugin_gav = kwargs.get('mavenSurefirePluginGav', Gav(None, 'maven-surefire-plugin', None))
    build_helper_maven_plugin_gav = kwargs.get('buildHelperMavenPluginGav', Gav('org.codehaus.mojo', 'build-helper-maven-plugin', None))

    pom_properties_to_remove = ['io.swagger.annotations.version', 'quarkus-plugin.version',
    'quarkus.platform.version', 'quarkus.platform.artifact-id', 'quarkus.platform.group-id',
    'surefire-plugin.version', 'maven.compiler.parameters', 'javax.annotation-api-version',
    'jakarta.annotation-api-version', 'javax.ws.rs-version', 'jakarta.ws.rs-version']

    java_version_pom_properties = ['maven.compiler.source', 'maven.compiler.target']

    mp_ann_prefix = 'org.eclipse.microprofile.openapi.annotations.'
    mp_ann_post_fix_list = ['Extension', 'License', 'Components', 'ExternalDocumentation', 'OpenAPIDefinition',
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
    mp_fqdn_ann_list = [ mp_ann_prefix + x for x in mp_ann_post_fix_list ]
    mp_short_ann_list = [ re.search('\w+$', x).group(0) for x in mp_ann_post_fix_list ]
    mp_ann_imports_list = [ 'import ' + x + ';\n' for x in mp_fqdn_ann_list ]
    mp_fqdn_ann_to_short_ann_to_import_list = list(zip(mp_fqdn_ann_list, mp_short_ann_list, mp_ann_imports_list))

    # END CONSTANTS

    

    gen_gav = yf.getGav(descriptor['generatedGav'])
    package = jmf.getPackage(gen_gav)
    path_to_open_api = files_path + '/' + descriptor['openApiUrl']
    author = descriptor['author']
    path_to_pom = None
    # the directory of the java code.
    model_path = jmf.getModelPath(gen_gav) + '/model'

    # the directory of the maven pom for the generated code. Usually at the directory root of project.
    proj_pom_path = gen_gav.artifact_id + '/pom.xml'

    # load OpenAPI3 spec doc, so can get values out
    oa3dict = yf.loadOpenApi3(path_to_open_api)

    print('genGav: ' + str(gen_gav))
    print('package: ' + str(package))
    print('pathToOpenApi: ' + str(path_to_open_api))
    print('pathToPom: ' + str(path_to_pom))
    print('author: ' + str(author))
    print('modelPath: ' + str(model_path))

    # Geneate Maven project.
    opts = {}
    opts['yamlName'] = path_to_open_api
    opts['apiPackage'] = package
    opts['modelPackage'] = package + '.model'
    opts['generatedGroupId'] = gen_gav.group_id
    opts['generatedArtifactId'] = gen_gav.artifact_id
    opts['generatedVersion'] = gen_gav.version

    mvn_options = jmf.captureContextualCommandLineOptions(kwargs.get('command_args', []), 'mvn')
    mvn_opts = {'mvn_options': mvn_options}
    opts.update(mvn_opts)

    print('mvn_options: ' + str(mvn_options))
    print('opts: ' + str(opts))

    #jmf.callMvnWithOptions(**opts, goal='clean package', file=pathToPom)
    jmf.generateMavenProject(mvn_gen_gav, gen_gav, descriptor['author'], **opts, file=path_to_pom)

    print('finished generating generator project.')

    jmf.callMvnWithOptions(**mvn_opts, goal='clean install', file=proj_pom_path)

    print('finished generating project.')
    #quit(0)
    # remove generating pom (rename first)
    os.rename(gen_gav.artifact_id + '/pom.xml', gen_gav.artifact_id + '/pom.xml.generating')

    print('Renamed generating pom.')

    # copy contents to directory.
    gen_sources_dir = gen_gav.artifact_id + "/target/generated-sources/openapi"
    shutil.move(gen_sources_dir + '/pom.xml', gen_gav.artifact_id + '/pom.xml')
    shutil.move(gen_sources_dir + '/src', gen_gav.artifact_id + '/src')

    print('Moved generating sources.')

    # get all of the java files in generated code so we can process them.
    java_file_list = glob.glob(gen_gav.artifact_id + '/src/main/java/**/*.java', recursive=True)
    print('javaFileList: ' + str(java_file_list))

    # the jaxrs-spec generator is terrible, need to fix some code.
    # delete lines starting with @javax.annotation.Generated (OR @jakarta.annotation.Generated) in all files.
    for f in java_file_list:
        print('file: ' + str(f))
        # get rid of 'false' at end of generated annotation line
        jmf.replaceTextInFile('\n@(javax|jakarta)\.annotation\.Generated.*\n', '',f)
        # fix double quote escaping in generated code.
        jmf.replaceTextInFile(r'\\&quot;', r'\"', f)

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
        jmf.addDependency(proj_pom_path, yf.getGav(dependency))

    #add openapi microprofile (openapi3) annotations
    # TODO adding oldest version of microprofile annotations here; maybe check version needed before this point.
    jmf.addDependency(proj_pom_path, microprofile_gav)

    #add jackson-databind-nullable because generator likes to sometimes throw that in there for no reason.
    jmf.addDependency(proj_pom_path, jackson_dbndnb_gav)

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
    java_file_simple_names = [os.path.basename(f) for f in java_file_list]
    java_file_simple_names_to_path = dict(zip(java_file_simple_names, java_file_list))
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
    jmf.deleteFile(proj_pom_path + '.generating')

    # Fix potential nested public enum issue of missing closing bracket
    fne.fix_nested_enum_classes(java_file_list)

    print('Rebuilding project.')
    jmf.callMvnWithOptions(**mvn_opts, goal='clean install', file=proj_pom_path)
    print('Finished rebuilding project.')

    print('Removing target directory.')
    jmf.callMvnWithOptions(**mvn_opts, goal='clean', file=proj_pom_path)
    print('Removed target directory.')

    # collapse microprofile openapi annotations
    for f in java_file_list:
        with open(f,'r+') as fopen:

            # Reading the file data and store it in a file variable
            file0 = fopen.read()

            # Replacing the pattern with the string in the file data for each item in the dict
            for search_text, replace_text, import_statement in mp_fqdn_ann_to_short_ann_to_import_list:
                ann_sub_result = re.subn(search_text + r'(?!\w)', replace_text, file0, count = 0) # 0 means replace as many as you can find
                file0 = ann_sub_result[0]
                number_of_replacements_made = ann_sub_result[1]
                # if a replacement was made, insert the corresponding import statement at top of file.
                if number_of_replacements_made > 0:
                    print('file: ' + str(f) + ' ... annotation searched: ' + replace_text + ' ... results found: ' + str(number_of_replacements_made))
                    file0 = re.sub('\n', '\n' + import_statement, file0, count = 1)

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
    # don't want to match standalone @Tag like \n\s\s\s\s@Tag(name="pets")\n
    # don't remember what the 1st element in the list does, leaving for now 202603
    tag_dict = {'\n@Tag.*\n': '\n', '(?<=tags\s=\s)@Tag.*\)\n': '{@%@}\n'}
    print('before replacing tags.')
    for f in java_file_list:
        jmf.replaceTextInFileMulti(tag_dict, f)
    print('after replacing tags.')
    # get values from OpenAPI3 spec doc
    info_title = oa3dict.get("info", {}).get("title", "")
    info_description = oa3dict.get("info", {}).get("description", "")
    tags_list = oa3dict.get("tags", "")
    # schemesList = []
    # securitySchemesDict = oa3dict.get("components", {}).get("securitySchemes", "")
    # if isinstance(securitySchemesDict, dict):
    #     schemesList = securitySchemesDict.keys()
    # pathMethodToExampleDict = {}
    method_security_scheme_scopes = [] #list:dict:list
    # print('oa3dict: ' + str(oa3dict))
    oas3_http_methods = {'get', 'put', 'post', 'delete', 'options', 'head', 'patch', 'trace'}
    for k, v in oa3dict.get("paths", {}).items():
        for k2, v2 in v.items():
            if k2 in oas3_http_methods:
                method_security_scheme_scopes.append({k + ' ' + k2: v2.get("security", "")})
                # examplesDict = v2.get("requestBody", {}).get("content", {}).get("application/json", {}).get("examples", {})
                # if len(examplesDict) > 0:
                    # pathMethodToExampleDict[k + ' ' + k2] = examplesDict

    # add title back in
    for f in java_file_list:
        jmf.replaceTextInFile('(?s)(@OpenAPIDefinition.*@Info.*title\s?=\s?)""', r'\g<1>"' + jmf.clean_text(info_title) + '"', f)
    # add openapidefinition info description back in
    for f in java_file_list:
        jmf.replaceTextInFile('(?s)(@OpenAPIDefinition.*?@Info.*?title\s?=\s?".*?"\s?,.*?version\s?=\s?".*?"\s?,.*?description\s?=\s?)""(?!\))', r'\g<1>"' + jmf.clean_text(info_description) + '"', f)

    # add tags back in
    tag_annotations = ""
    for index, tag in enumerate(tags_list):
        tag_annotations += '@Tag(name="' + tag.get("name", "") + '", description="' + tag.get("description", "") + '")'
        if index < len(tags_list) - 1:
            tag_annotations += ', '

    for f in java_file_list:
        jmf.replaceTextInFile('(tags\s?=\s?\{)@%@\}', r'\g<1>' + tag_annotations +  '}', f)
        print('added tags back in. ')

    # add security scopes in.

    # iterate over each of the methodSecuritySchemeScopes, if scheme scopes list > 0... find the annotations in java code and add scopes.
    for scope in method_security_scheme_scopes:
        for url_http_method, security_scheme_list in scope.items():
            url = url_http_method.split(' ')[0]
            http_method = url_http_method.split(' ')[1].upper()
            for security_scheme in security_scheme_list:
                for security_scheme_name, scopes in security_scheme.items():
                    if len(scopes) > 0:
                        for f in java_file_list:
                            file_string = ''
                            with open(f, 'r') as fil:
                                file_string = fil.read()
                            update_file = False
                            root_path_annotation = jmf.getInFile('@Path\s*\(\s*"(.*)"\s*\)(\n|.)*public\s+(interface|class)', f)
                            root_path = ''
                            if None != root_path_annotation:
                                print('rootPathAnnotation: ' + str(root_path_annotation) + ' in file: ' + str(f))
                                root_path_matches = re.search('@Path\s*\(\s*"(.*)"\s*\)', root_path_annotation, re.MULTILINE)
                                if None != root_path_matches:
                                    root_path = root_path_matches.group(1)
                                print('rootPath: ' + str(root_path))
                            # for each method in the file, find path and httpMethod
                            match_iter = re.finditer('@(POST|PUT|GET|DELETE|PATCH|OPTIONS|HEAD|TRACE|CONNECT)\s+(@Path\s*\(\s*"(.*)"\s*\))?', file_string, re.MULTILINE)
                            for match in match_iter:
                                if None != match:
                                    #print('match: ' + repr(match))
                                    match_http_method = match.group(1)
                                    match_relative_path = match.group(3)
                                    match_relative_path = match_relative_path if match_relative_path != None else ''
                                    match_path = root_path + match_relative_path
                                    match_url_http_method = match_path + ' ' + match_http_method
                                    compare_url_http_method = url + ' ' + http_method
                                    if match_url_http_method == compare_url_http_method:
                                        print('matchUrl_httpMethod: ' + str(match_url_http_method) + ' == ' + str(compare_url_http_method))
                                        # find the method with the url_httpMethod and add the scopes to the securityRequirement annotation.
                                        search_text = '(@' + match_http_method + r'(\n|.)+' + match_relative_path.replace('/', '\/') + r'(\n|.)*@SecurityRequirement\s?\(\s?name\s?=\s?"' + security_scheme_name + '"\s?)\)'
                                        print('searchText: ' + str(search_text))
                                        replace_text = r'\g<1>, scopes = {"' + '", "'.join(scopes) + '"})'
                                        print('replaceText: ' + str(replace_text))
                                        file_string = re.sub(search_text, replace_text, file_string, count = 1)
                                        update_file = True

                            # write file to disk
                            if update_file:
                                with open(f, 'w') as fil:
                                    fil.write(file_string)
                                    print('file updated: ' + str(f) + ' at ' + url_http_method + ' with scopes: ' + str(scopes))

    # TODO add examples back in


    # remove swagger2 annotations dependency from pom
    jmf.removeDependency(proj_pom_path, swagger_gav)
    # Trim down pom by removing all unnecessary transitive dependencies.
    # Only keep mandatory dependencies, mostly annotation libraries.
    jmf.removeDependency(proj_pom_path, quarkus_junit_gav)
    jmf.removeDependency(proj_pom_path, rest_assured_gav)
    jmf.removeDependency(proj_pom_path, quarkus_resteasy_gav)
    jmf.removeDependency(proj_pom_path, quarkus_smallrye_gav)
    jmf.removeDependency(proj_pom_path, remove_javax_rs_gav)
    jmf.removeDependency(proj_pom_path, remove_javax_ann_gav)
    jmf.removeDependency(proj_pom_path, remove_jakarta_ann_gav)
    jmf.removeDependency(proj_pom_path, remove_jakarta_rs_gav)
    # removing json-nullable... hopefully never need.
    jmf.removeDependency(proj_pom_path, remove_json_nullable_gav)
    for java_file in java_file_list:
        jmf.replaceTextInFile(r'import org.openapitools.jackson.nullable.JsonNullable;\n', '', java_file)

    # trim excess fat from generated pom, including properties, plugins and profiles.
    jmf.removePomPlugin(proj_pom_path, quarkus_maven_plugin_gav)
    jmf.removePomPlugin(proj_pom_path, maven_surefire_plugin_gav)
    jmf.removePomPlugin(proj_pom_path, build_helper_maven_plugin_gav)
    jmf.removePomProfile(proj_pom_path, 'native')
    jmf.removePomDependencyManagement(proj_pom_path)
    jmf.removePomProperties(proj_pom_path, pom_properties_to_remove)
    jmf.removePomProperties(proj_pom_path, java_version_pom_properties)

    # must remove default microprofile_gav before adding version correct one.
    jmf.removeDependency(proj_pom_path, microprofile_gav)

    # Add annotation Gavs in. Defaulting to jakarta.
    jmf.addDependency(proj_pom_path, microprofile_gav)
    jmf.addDependency(proj_pom_path, jakarta_validation_gav)
    jmf.addDependency(proj_pom_path, jackson_ann_gav)
    jmf.addDependency(proj_pom_path, jakarta_rs_gav)

    if 'javax' == jaxrs:
        jmf.removeDependency(proj_pom_path, jakarta_rs_gav)
        jmf.addDependency(proj_pom_path, javax_rs_gav)
        for f in java_file_list:
            jmf.replaceTextInFileMulti({'jakarta\.ws\.rs': 'javax.ws.rs'}, f)
        print('Only Java version 8 supported with javax jaxrs. Setting java version to 8 if it is not otherwise. If you want to use a different version of Java, you must use jakarta jaxrs.')
        java_version = '8'
    elif 'jakarta' == jaxrs:
        None
    else:
        print('Unsupported jaxrs: ' + str(jaxrs))
        quit(1)

    # set java version to java_version
    jmf.addPomProperties(proj_pom_path, dict(zip(java_version_pom_properties, [java_version, java_version])))

    # update imports
    #jmf.gjf(javaFileList)
    jmf.eclipseFormatter(proj_pom_path)
    #jmf.eclipseFormatterValidate(projPomPath)
    #jmf.beautifyImports(projPomPath)

    # create src/main/resources/META-INF/beans.xml
    jmf.makeFile(gen_gav.artifact_id + '/src/main/resources/META-INF/', 'beans.xml') 

    # remove docker folder
    jmf.deleteDirectory(gen_gav.artifact_id + '/src/main/docker')

    # rename src/main/openapi/openapi.yaml to real doc name
    oapidoc_path = gen_gav.artifact_id + '/src/main/openapi'
    source_doc = oapidoc_path + '/openapi.yaml'
    target_doc = oapidoc_path + '/' + os.path.basename(path_to_open_api)
    if target_doc != source_doc:
        jmf.copyFile(source_doc, target_doc)
        jmf.deleteFile(oapidoc_path + '/openapi.yaml')
        print('Copied ' + oapidoc_path + '/openapi.yaml to ' + oapidoc_path + '/' + os.path.basename(path_to_open_api))

    pl.prepend_licenses(descriptor, gen_gav.artifact_id, files_path)

    print('Rebuilding project 2.')
    jmf.callMvnWithOptions(**mvn_opts, goal='clean install', file=proj_pom_path)
    print('Finished rebuilding project 2.')

    print('Removing target directory 2.')
    jmf.callMvnWithOptions(**mvn_opts, goal='clean', file=proj_pom_path)
    print('Removed target directory 2.')

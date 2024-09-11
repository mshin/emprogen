import com.emprogen.java.maven.functions as jmf
import com.emprogen.java.maven.yaml_functions as yf
import com.emprogen.java.maven.field_functions as ff
import re
#import subprocess
from com.emprogen.java.maven.models import Gav

#TODO change name of serviceImpl from ...ServiceBean to ...ServiceImpl

#def generate(descriptor: 'dict', archetypeGav: 'Gav' = Gav('com.github.mshin', 'jaxrms-springboot-camel-archetype', '1.0.1')) -> None:
def generate(descriptor: 'dict', archetypeGav: 'Gav' = Gav('com.emprogen', 'service-jaxrs-springboot-camel-p0-archetype', '0.0.1')
        , *, filesPath: 'str' = None) -> None:

    # Do all 1 time loads and calculations up front.

    # define maven archetype used for this generator within script.
    archGav = archetypeGav

    # the maven groupId:artifactId:version for the code module to be generated
    projGav = yf.getGeneratedProjectGav(descriptor)

    # the gav for the maven module containing the jaxrs Interface from which the service will be generated.
    serviceInterfaceGavString = descriptor['serviceInterfaceGav']
    apiGav = yf.getGav(serviceInterfaceGavString)

    # the java package for the project to be generated.
    generatedPackage = jmf.getPackage(projGav)

    # the directory of the maven pom for the generated code. Usually at the directory root of project.
    projPomPath = projGav.artifactId + '/pom.xml'
    # the directory of the java code.
    modelPath = jmf.getModelPath(projGav)

    # the package.Classname for the jaxrs Interface from which the service will be generatd.
    serviceInterfaceString = descriptor['serviceInterface']
    # the Classname only for the jaxrs Interface from which the service will be generated.
    serviceInterfaceName = serviceInterfaceString.split('.')[-1]
    # the package only for the jaxrs Interface from which the service will be generated.
    serviceInterfacePackage = serviceInterfaceString.replace('.' + serviceInterfaceName, '')

    # the template java bean class file.
    beanTemplateFile = modelPath + '/' + serviceInterfaceName + 'Bean.java'
    # the template java camel routes class file.
    routesTemplateFile = modelPath + '/' + serviceInterfaceName + 'Routes.java'
    # the template java spring application class file.
    applicationTemplateFile =  modelPath + '/Application.java'

    thisFilesPath = str(jmf.getFilePath(__file__))

    # the directory com/emprogen/java/maven
    javaMavenDir = jmf.getJavaMavenPath()
    # the location of the java properties file mapping tpe to package.type.
    typToPkgtyp = ff.loadPropertiesAsDict(javaMavenDir + '/java_type.properties')

    # the location of the script that gets maven dependencies for calling from classpath context
    cpPlUrl=javaMavenDir + '/maven-cp.pl'
    # the location of the properties file with snippets used to create a camel route in java dsl.
    camelRouteChoiceUrl = thisFilesPath + '/camel_route_choice.properties'
    # the spring annotation for defining a spring managed bean.
    springComponentAnn = "@org.springframework.stereotype.Component"
    # the package.Classname of a tool used to generate a java impl Class given a java Interface.
    genImplClass = "com.emprogen.generate.impl.GenerateImplService"
    # the maven gav for the GenerateImplService tool.
    generateImplGav = "com.emprogen:generate-impl:0.0.1"


    # Geneate Maven project.
    opts = {}
    opts['api_groupId'] = apiGav.groupId
    opts['api_artifactId'] = apiGav.artifactId
    opts['api_version'] = apiGav.version
    opts['jaxrs_service_interface'] = serviceInterfaceName
    opts['jaxrs_service_package'] = serviceInterfacePackage
    print('service opts: ' + str(opts))
    jmf.generateMavenProject(archGav, projGav, descriptor['author'], **opts)

    # get the maven dependencies for the module containing the jaxrs Interface from which the service will be generated.
    serviceImplementationClasspath = jmf.runSubprocessCaptureOutput([cpPlUrl, serviceInterfaceGavString]).strip()
    # get the maven dependencies for the module containing the tool used to generate a java impl Class given a java Interface.
    generateImplClasspath = jmf.runSubprocessCaptureOutput([cpPlUrl, generateImplGav]).strip()
    # print ('serviceImplementationClasspath: ' + str(serviceImplementationClasspath))
    # print ('generateImplClasspath: ' + str(generateImplClasspath))
    # print ('generatedPackage: ' + str(generatedPackage))
    # print ('serviceInterfaceString: ' + str(serviceInterfaceString))

    # run the tool to get the generated code from the jaxrs Interface.
    generatedImpl = jmf.runSubprocessCaptureOutput(['java', '-cp', 
            serviceImplementationClasspath + ':' + generateImplClasspath, genImplClass, 
            serviceInterfaceString, generatedPackage])
    # print (str(generatedImpl))

    # Overwrite content of service bean impl with new content.
    jmf.replaceFileContents(generatedImpl, beanTemplateFile)

    # Write "@org.springframework.stereotype.Component\n" before "public class"
    annotation = springComponentAnn + '\npublic class'
    jmf.replaceTextInFile('public class', annotation, beanTemplateFile)

    # update Routes class with interface methods

    #get methods
    # methods will be \s methodName[\s zero or more whitespace, then left parentheses. (]
    pattern = re.compile(r'(?<=\s)([a-zA-Z0-9$_]+)(?=\s*\()')
    matches = re.finditer(pattern, generatedImpl)
    matchList = [match.group() for match in matches]
    #print ('matchList: ' + str(matchList))

    # build .when() string
    whenString = jmf.getProperty('when', camelRouteChoiceUrl)
    print('whenString: ' + str(whenString))

    # for each method, append a new when string, replacing %0 placeholder with method name.
    routeString = ''
    for apiMethod in matchList:
        routeString += whenString.replace('%', apiMethod)
    semicolon = jmf.getProperty('semicolon', camelRouteChoiceUrl)
    routeString += semicolon

    # replace '^' with \n
    routeString = routeString.replace('^', '\n')
    print('routeString: ' + routeString)

    # remove existing route choice options & replace with built route string.
    rercoPattern = r'(?<=\.choice\(\)\n)((.|\n)+;)'
    jmf.replaceTextInFile(rercoPattern, routeString, routesTemplateFile)

    # add addtl dependencies to the pom.
    # if no items in optional dependencyGav, default {} for null safety
    for dependency in descriptor.get('dependencyGav', {}):
        print('adding dependency to pom: ' + dependency)
        jmf.addDependency(projPomPath, yf.getGav(dependency))

    # update imports
    jmf.beautifyImports(projPomPath)

    # verify it compiles
    jmf.callMvnWithOptions(goal='clean install', file=projPomPath)
    jmf.callMvnWithOptions(goal='clean', file=projPomPath)
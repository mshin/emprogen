#!/usr/local/bin/python3

import com.emprogen.java.maven.functions as jmf
import com.emprogen.java.maven.yaml_functions as yf
import com.emprogen.java.maven.field_functions as ff
import re
#import subprocess
from com.emprogen.java.maven.models import Gav

#TODO change name of serviceImpl from ...ServiceBean to ...ServiceImpl

#def generate(descriptor: 'dict', archetypeGav: 'Gav' = Gav('com.github.mshin', 'jaxrms-springboot-camel-archetype', '1.0.1')) -> None:
def generate(descriptor: 'dict', archetypeGav: 'Gav' = Gav('com.emprogen', 'service-jaxrs-springboot-camel-p0-archetype', '0.0.1')) -> None:


# generate the maven project (build existing java file url.)
# get jaxrs service interface
# make impl file.
  # generate impl class
  # delete existing service bean/impl
  # make new service impl .java file with generated content.
# replace Application.java placeholder for service interface name. (with package)
# update camel route with methods from impl.
# update bean test class names
# update route test class names and bean name.

# call formatter on project.
# build resultant project to verify compilation.

    # Do all 1 time loads and calculations up front.
    # define archetype Gav used for this generator within script.
    archGav = archetypeGav
    projGav = yf.getGeneratedProjectGav(descriptor)
    serviceInterfaceGavString = descriptor['serviceInterfaceGav']
    apiGav = yf.getGav(serviceInterfaceGavString)

    generatedPackage = jmf.getPackage(projGav)
    projPomPath = projGav.artifactId + '/pom.xml'
    modelPath = jmf.getModelPath(projGav)

    serviceInterfaceString = descriptor['serviceInterface']
    serviceInterfaceName = serviceInterfaceString.split('.')[-1]
    serviceInterfacePackage = serviceInterfaceString.replace('.' + serviceInterfaceName, '')

    beanTemplateFile = modelPath + '/' + serviceInterfaceName + 'Bean.java'
    routesTemplateFile = modelPath + '/' + serviceInterfaceName + 'Routes.java'
    applicationTemplateFile =  modelPath + '/Application.java'

    filePath = str(jmf.getFilePath(__file__))
    javaMavenDir = jmf.getJavaMavenPath()
    typToPkgtyp = ff.getTypeToPkgtypeDict(javaMavenDir + '/java_type.properties')
    cpPlUrl=javaMavenDir + '/maven-cp.pl'
    camelRouteChoiceUrl = filePath + '/camel_route_choice.properties'

    genImplClass = "com.emprogen.generate.impl.GenerateImplService"
    springComponentAnn = "@org.springframework.stereotype.Component"
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

    # generate impl class
    # delete existing service bean/impl
    # make new service impl .java file with generated content.

    #serviceImplementationClasspath = subprocess.run([cpPlUrl, serviceInterfaceString], check=True, text=True, capture_output=True).stdout
    serviceImplementationClasspath = jmf.runSubprocessCaptureOutput([cpPlUrl, serviceInterfaceGavString]).strip()
    generateImplClasspath = jmf.runSubprocessCaptureOutput([cpPlUrl, generateImplGav]).strip()

    #print ('serviceImplementationClasspath: ' + str(serviceImplementationClasspath))
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

    # add the dependency to the pom.
    for dependency in descriptor['dependencyGav']:
        jmf.addDependency(projPomPath, yf.getGav(dependency))
    # update imports
    jmf.beautifyImports(projPomPath)

    # verify it compiles
    jmf.callMvnWithOptions(goal='clean install', file=projPomPath)

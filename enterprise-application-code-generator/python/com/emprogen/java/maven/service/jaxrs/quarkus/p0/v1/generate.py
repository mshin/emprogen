import com.emprogen.java.maven.functions as jmf
import com.emprogen.java.maven.yaml_functions as yf
import com.emprogen.java.maven.field_functions as ff
import glob
import re

from com.emprogen.java.maven.models import Gav

def generate(descriptor: 'dict', archetypeGav: 'Gav' = Gav('com.emprogen', 'service-jaxrs-quarkus-p0-archetype', '0.0.1')
        , *, filesPath: 'str' = None, javaVersion: 'str' = '8') -> None:

    print('in service.jaxrs.quarkus.p0.v1.generate.py')
    print('javaVersion: ' + str(javaVersion))
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

    # the package.Classname for the jaxrs Interface from which the service will be generated.
    serviceInterfaceString = descriptor['serviceInterface']
    # the Classname only for the jaxrs Interface from which the service will be generated.
    serviceInterfaceName = serviceInterfaceString.split('.')[-1]
    # the package only for the jaxrs Interface from which the service will be generated.
    serviceInterfacePackage = serviceInterfaceString.replace('.' + serviceInterfaceName, '')

    # the template java bean class file.
    serviceTemplateFile = modelPath + '/' + serviceInterfaceName + 'Service.java'
    # the template java impl class file.
    implTemplateFile = modelPath + '/impl/' + serviceInterfaceName + 'Impl.java'

    thisFilesPath = str(jmf.getFilePath(__file__))

    # the directory com/emprogen/java/maven
    javaMavenDir = jmf.getJavaMavenPath()
    # the location of the java properties file mapping tpe to package.type.
    typToPkgtyp = ff.loadPropertiesAsDict(javaMavenDir + '/java_type.properties')
    # the location of the script that gets maven dependencies for calling from classpath context
    cpPlUrl=javaMavenDir + '/maven-cp.pl'

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
    print ('serviceImplementationClasspath: ' + str(serviceImplementationClasspath))
    # print ('generateImplClasspath: ' + str(generateImplClasspath))
    # print ('generatedPackage: ' + str(generatedPackage))
    # print ('serviceInterfaceString: ' + str(serviceInterfaceString))

    # run the tool to get the generated code from the jaxrs Interface.
    generatedImpl = jmf.runSubprocessCaptureOutput(['java', '-cp', 
            serviceImplementationClasspath + ':' + generateImplClasspath, genImplClass, 
            serviceInterfaceString, generatedPackage])
    print (str(generatedImpl))

    # get methods code from generated code
    pattern = re.compile(r'(\s{4}@Override(\n|.)+?})')
    matches = re.finditer(pattern, generatedImpl)
    matchList = [match.group() for match in matches]
    # print ('matchList: ' + str(matchList))

    # call service from Impl START

    # get method names from generated code
    # methods will be \s methodName[\s zero or more whitespace, then left parentheses. (]
    methodNamePattern = re.compile(r'(?<=\s)([a-zA-Z0-9$_]+)(?=\s*\()')
    methodNameMatches = re.finditer(methodNamePattern, generatedImpl)
    methodNameMatchList = [match.group() for match in methodNameMatches]
    # print ('methodNameMatchList: ' + str(methodNameMatchList))

    methodNameToMethodDict = dict(zip(methodNameMatchList, matchList))

    # get the arg list for each method
    argMatchList = []

    for methodName in methodNameMatchList:
        # get the arg list for the method
        argPattern = re.compile(r'(?<=\s)' + methodName + '\s*\((.*?)\)')
        argMatch = re.search(argPattern, generatedImpl)
        if None != argMatch:
            argMatchList.append(argMatch.group(1))
        # print ('argMatchList: ' + str(argMatchList))

    # dict of methodName:rawArgList
    methodToArgsDict = dict(zip(methodNameMatchList, argMatchList))
    print ('methodToArgsDict: ' + str(methodToArgsDict))

    # parse the args to remove types.
    for methodName, argList in methodToArgsDict.items():
        print ('argList: ' + argList)
        # get the arg type:value pairs
        argTypeVarList = argList.split(',')
        # print ('argTypeVarList: ' + str(argTypeVarList))
        # get the arg var names
        argVars = []
        for argTypeVar in argTypeVarList:
            argVars.append(argTypeVar.strip().split(' ')[1])
        # print ('argVars: ' + str(argVars))

        methodToArgsDict[methodName] = ', '.join(argVars)

    print ('methodToArgsDict2: ' + str(methodToArgsDict))

    modifiedMethodsList = []
    # replace methods' 'return null;' with 'return service.method(args)'.
    for methodName, methodString in methodNameToMethodDict.items():
        callString = 'service.' + methodName + '(' + methodToArgsDict[methodName] + ')'
        modifiedMethodsList.append(methodString.replace('null', callString))

    implMethods = '\n\n'.join(modifiedMethodsList) + '\n\n'
    # print ('implMethods: ' + str(implMethods))
    # call service from Impl END
    methods = '\n\n'.join(matchList) + '\n\n'
    # print ('methods: ' + str(methods))

    # write methods into Impl class
    jmf.replaceTextInFile('}', implMethods + '}', implTemplateFile)
    # strip @Overrides from generated code methods
    # write stripped methods into service class
    jmf.replaceTextInFile('}', methods.replace('@Override\n', '') + '}', serviceTemplateFile)

    # add addtl dependencies to the pom.
    # if no items in optional dependencyGav, default {} for null safety
    for dependency in descriptor.get('dependencyGav', {}):
        print('adding dependency to pom: ' + dependency)
        jmf.addDependency(projPomPath, yf.getGav(dependency))

    # set java version to javaVersion
    jmf.removePomProperties(projPomPath, ['maven.compiler.source', 'maven.compiler.target'])
    jmf.addPomProperties(projPomPath, {'maven.compiler.source': javaVersion, 'maven.compiler.target': javaVersion})

    # set jaxrs package and java version based on the openapi3 module
    if None != re.search('javax.ws.rs.javax.ws.rs-api', serviceImplementationClasspath):
        print('Using javax in API definition module. Reducing Quarkus version in impl module to use javax instad of jakarta code packages. Reducing java version to 8.')
        # Fix java imports
        javaFileList = glob.glob(projGav.artifactId + '/src/**/*.java', recursive=True)
        print('javaFileList: ' + str(javaFileList))
        for javaFile in javaFileList:
            jmf.replaceTextInFile('import jakarta.', 'import javax.', javaFile)
        # Reduce Quarkus version
        jmf.removePomProperties(projPomPath, ['version.quarkus'])
        jmf.addPomProperties(projPomPath, {'version.quarkus': '2.16.8.Final'})

        # Reduce Java version to 8
        jmf.removePomProperties(projPomPath, ['maven.compiler.source', 'maven.compiler.target'])
        jmf.addPomProperties(projPomPath, {'maven.compiler.source': '8', 'maven.compiler.target': '8'})

    elif None != re.search('jakarta.ws.rs.jakarta.ws.rs-api', serviceImplementationClasspath):
        print('Using jakarta code packages in API definition module.')
    else:
        print('Did not find javax or jakarta code packages in API definition module.')

    # update imports
    jmf.beautifyImports(projPomPath)

    # verify it compiles
    jmf.callMvnWithOptions(goal='clean install', file=projPomPath)
    jmf.callMvnWithOptions(goal='clean', file=projPomPath)
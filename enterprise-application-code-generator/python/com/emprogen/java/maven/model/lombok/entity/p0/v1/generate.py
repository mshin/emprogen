import com.emprogen.java.maven.functions as jmf
import com.emprogen.java.maven.yaml_functions as yf
import com.emprogen.java.maven.field_functions as ff
from com.emprogen.java.maven.models import Gav
from com.emprogen.java.maven.models import JoinInstruction
from com.emprogen.java.maven.models import TableRelationship

def getJoinInstruction(joinDesc: 'str') -> 'JoinInstruction':
    # Format is "- ${Entity.class} **-** ${OtherEntity.class}" Where first * is <|- second * is 1|n third * is 1|n and fourth star is >|-.
    # Example: FormEntity <1-1> AccountEntity

    joinDescList = str(joinDesc).split()
    entNameL = joinDescList[0]
    entNameR = joinDescList[2]
    joinStr = joinDescList[1]
    isRefL = True
    isRefR = True
    isOwnerR = True
    mapping = None

    if '-' == joinStr[0]:
        isRefL = False
    if '-' == joinStr[4]:
        isRefR = False

    if 'n' == joinStr[1]:
        if 'n' == joinStr[3]:
            mapping = TableRelationship.MANY_TO_MANY
        else:
            mapping = TableRelationship.MANY_TO_ONE
    else:
        if 'n' == joinStr[3]:
            mapping = TableRelationship.ONE_TO_MANY
        else:
            mapping = TableRelationship.ONE_TO_ONE

    if isRefR == False or mapping == TableRelationship.MANY_TO_ONE:
        isOwnerR = False

    return JoinInstruction(entNameL, entNameR, mapping, isRefL, isRefR, isOwnerR)

def replaceVarsInAnnotation(annotation: 'str', refingType: 'str', refingTypeVar: 'str', refingTypePkVar: 'str',
        refingTypePkVarSnake: 'str', otherPkVarSnake: 'str', owningType: 'str', owningTypeVar: 'str') -> 'str':
    annotation = annotation.replace(r'%0', refingType)
    annotation = annotation.replace(r'%1', refingTypeVar)
    annotation = annotation.replace(r'%4pk', refingTypePkVar)
    annotation = annotation.replace(r'%5pksql', refingTypePkVarSnake)
    annotation = annotation.replace(r'%6opksql', otherPkVarSnake)
    annotation = annotation.replace(r'%2', owningType)
    annotation = annotation.replace(r'%3', owningTypeVar)
    return annotation

def generate(descriptor: 'dict', archetypeGav: 'Gav' = Gav('com.emprogen', 'model-lombok-entity-p0-archetype', '0.0.1'),
        *, filesPath: 'str' = None) -> None:

    # Do all 1 time loads and calculations up front.

    # define maven archetype used for this generator within script.
    archGav = archetypeGav

    # the maven groupId:artifactId:version for the code module to be generated
    projGav = yf.getGeneratedProjectGav(descriptor)

    # the directory of the maven pom for the generated code. Usually at the directory root of project.
    projPomPath = projGav.artifactId + '/pom.xml'

    # the directory of the java code.
    modelPath = jmf.getModelPath(projGav)

    # the template java entity class file.
    templateFile = modelPath + '/class0.java'

    # the location of the java properties file mapping tpe to package.type.
    typToPkgtyp = ff.loadPropertiesAsDict(jmf.getJavaMavenPath() + '/java_type.properties')

    thisFilesPath = str(jmf.getFilePath(__file__))

    # the locations of additional properties files.
    jpaTypeAnnotationDict = ff.loadPropertiesAsDict(thisFilesPath + '/jpa_type_annotation.properties')
    jpaJoinAnnotationDict = ff.loadPropertiesAsDict(thisFilesPath + '/jpa_join_annotation.properties')
    depGavUrl = thisFilesPath + '/dep_gav.properties'

    # Geneate Maven project.
    opts = {}
    opts['class0'] = 'class0'
    opts['fields'] = 'fields'
    jmf.generateMavenProject(archGav, projGav, descriptor['author'], **opts)

    # some of the time types used in the jpa type annotations require additional dependencies.
    needsConverterDependency = False

    # for each model file from descriptor
    for model in descriptor['model']:

        # by convention, all entity classes end in the word 'Entity'
        newClassName = model['name']
        if not newClassName.endswith('Entity'):
            newClassName += 'Entity'

        # by convention, columns in database use snake case.
        new_class_name = jmf.camelToSnake(newClassName)

        # get the primary key value out of the descriptor file.
        pk = model['pk']

        # calculate the model class name to be created
        newFileName = modelPath + '/' + newClassName + '.java'

        # create the class file; replace name
        jmf.copyFile(templateFile, newFileName)

        # set the class name in the file to the correct value.
        jmf.replaceTextInFile('class0', newClassName, newFileName)

        # calculate the raw field string for the class file
        # first, get the field to type dictionary
        fieldToType = yf.getFieldsAndTypes(model)
        # then, get the raw field list
        fieldList = fieldToType.keys()
        # next, calculate the field to package.type dictionary.
        fieldToPkgtyp = ff.mapFieldsToQualifiedTypes(fieldToType, typToPkgtyp)
        # finally, generate the raw field string with annotation placeholders.
        fieldString = ff.createFieldString(fieldToPkgtyp, True)
        #print('fieldString: ' + fieldString)

        # for each entry in the field to package.type dictionary
        for field, typ in fieldToPkgtyp.items():

            # get the snake case version of each field, because databases require snake case not camel case.
            fieldSnake = jmf.camelToSnake(field)
            # the property key defaults to the type, but if it's the primary key, get the primary key property.
            propKey = typ
            # in most cases the anntation replacement string will be the field in snake case.
            replacementString = fieldSnake
            # fi the field is the primary key,
            if field == pk:
                # the property we want is the primary key one
                propKey = 'pk'
                # the replacement string is classname isntead of field name.
                replacmentString = new_class_name
            # get the annotation based on tye propKey. If it's not there, use the default annotation.
            ann = jpaTypeAnnotationDict.get(propKey, '    @javax.persistence.Column( name = \"%\" )')
            # replace placeholders in annotation with replacementString
            ann = ann.replace('%', replacementString)

            # add the processed annotation to the corresponding field in fieldString.
            fieldString = fieldString.replace('&%' + field + '&%', ann)

        # replace all caret symbols with newlines.
        # Some of the annotations are stored as properties and use caret instead of newline.
        fieldString = fieldString.replace('^', '\n')
        print('fieldString: ' + fieldString)
        # replace contents of class file. 'fields' placeholder replaced with generated fields.
        jmf.replaceTextInFile('    fields', fieldString, newFileName)

        # if certain types are used for fields, add a new dependency.
        # code: if set intersection of set('LocalDate', 'LocalDateTime') and set(type)
        if {'LocalDate', 'LocalDateTime'} & set(fieldToType.values()):
            needsConverterDependency = True

    # get model to pk dictionary
    modelNameToPkDict = {}
    for model in descriptor['model']:
        modelNameToPkDict[model.get('name')] = model.get('pk')

    # get joins dictionary
    # create list of the join instructions
    joinInstructionList = []
    for join in descriptor['joins']:
        joinInstruction = getJoinInstruction(join)
        joinInstructionList.append(joinInstruction)

    # build the annotation and write it to file.
    for joinInstruction in joinInstructionList:

        # set owner/not owner as either left or right entity
        if joinInstruction.isOwnerR:
            owner = joinInstruction.entNameR
            notOwner = joinInstruction.entNameL
        else:
            owner = joinInstruction.entNameL
            notOwner = joinInstruction.entNameR

        # set variables needed for placeholder replacement in join annotation.
        owningType = owner
        owningTypeVar = jmf.lower1st(owner)
        refingType = notOwner
        refingTypeVar = jmf.lower1st(notOwner)
        refingTypePkVar = modelNameToPkDict.get(refingType)
        refingTypePkVarSnake = jmf.camelToSnake(refingTypePkVar)
        otherPkVar = modelNameToPkDict.get(owningType) # not used in annotation
        otherPkVarSnake = jmf.camelToSnake(otherPkVar)

        # start with left Entity
        if joinInstruction.isRefL:
            # get the template annotation. Adding caret to the beginning to be replaced with newline.
            annProp = joinInstruction.getAnnotationKeyLeft()
            ann = '^' + jpaJoinAnnotationDict.get(annProp.name)

            # build annotation by replacing placeholders.
            ann = replaceVarsInAnnotation(ann, refingType, refingTypeVar, refingTypePkVar, refingTypePkVarSnake, otherPkVarSnake, owningType, owningTypeVar)
            # we're going to replace the class's closing bracket with annotation, so must add it back in.
            ann += '^^}^'
            # caret for newline.
            ann = ann.replace('^', '\n')

            # make the path for entity to write to.
            entityFilePath = modelPath + '/' + joinInstruction.entNameL + '.java'
            # write the annotation to the respective file by appending it to the end.
            jmf.replaceTextInFile('\n}', ann, entityFilePath)

        # then do right Entity
        if joinInstruction.isRefR:
            # get the template annotation
            annProp = joinInstruction.getAnnotationKeyRight()
            ann = jpaJoinAnnotationDict.get(annProp.name)

            # build annotation by replacing placeholders.
            ann = replaceVarsInAnnotation(ann, refingType, refingTypeVar, refingTypePkVar, refingTypePkVarSnake, otherPkVarSnake, owningType, owningTypeVar)
            # we're going to replace the class's closing bracket with annotation, so must add it back in.
            ann += '^^}^'
            # caret for newline.
            ann = ann.replace('^', '\n')

            # make the path for entity to write to.
            entityFilePath = modelPath + '/' + joinInstruction.entNameR + '.java'
            # write the annotation to the respective file by appending it to the end.
            jmf.replaceTextInFile('\n}', ann, entityFilePath)

    # delete placeholder model
    jmf.deleteFile(templateFile)

    # If converter in files, then add that dependency.
    if needsConverterDependency:
        typeConverterGavString = jmf.getProperty('typeConverterGav', depGavUrl)
        tcGav = yf.getGav(typeConverterGavString)
        print('adding dependency to pom: ' + typeConverterGavString)
        jmf.addDependency(projPomPath, tcGav)

    # add addtl dependencies to the pom.
    # if no items in optional dependencyGav, default {} for null safety
    for dependency in descriptor.get('dependencyGav', {}):
        print('adding dependency to pom: ' + dependency)
        jmf.addDependency(projPomPath, yf.getGav(dependency))

    # update imports
    jmf.beautifyImports(projPomPath)

    # verify it compiles
    jmf.callMvnWithOptions(goal='clean install', file=projPomPath)

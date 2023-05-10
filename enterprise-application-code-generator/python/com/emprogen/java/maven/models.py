from enum import Enum

class Gav:
    def __init__(self, groupId: 'str', artifactId: 'str', version: 'str'):
        self.groupId = groupId
        self.artifactId = artifactId
        self.version = version

    def __repr__(self):
        return '[%s %s:%s:%s]' % (self.__class__.__name__, 
        self.groupId, self.artifactId, self.version)

class TableRelationship(Enum):
    ONE_TO_ONE = 1
    MANY_TO_ONE = 2
    ONE_TO_MANY = 3
    MANY_TO_MANY = 4

class AnnotationKey(Enum):
    ONE_TO_ONE_OWNER = 1
    ONE_TO_ONE_REFERENCING = 2
    MANY_TO_ONE = 3 # always owner
    ONE_TO_MANY = 4 # always referencing
    MANY_TO_MANY_OWNER = 5
    MANY_TO_MANY_REFERENCING = 6

class JoinInstruction:
    def __init__(self, entNameL: 'str', entNameR: 'str', relationship: 'TableRelationship', isRefL: 'bool', isRefR: 'bool', isOwnerR: 'bool'):
        self.entNameL = entNameL
        self.entNameR = entNameR
        self.relationship = relationship
        self.isRefL = isRefL
        self.isRefR = isRefR
        self.isOwnerR = isOwnerR

    def __repr__(self):
        return '[%s: %s %s %s; left reference: %s | right reference: %s | is owner right: %s]' % (self.__class__.__name__, 
        self.entNameL, self.relationship, self.entNameR, self.isRefL, self.isRefR, self.isOwnerR)

    def getAnnotationKeyLeft(self):
        match self.relationship:
            case TableRelationship.ONE_TO_ONE:
                if self.isOwnerR:
                    return AnnotationKey.ONE_TO_ONE_REFERENCING
                else:
                    return AnnotationKey.ONE_TO_ONE_OWNER
            case TableRelationship.MANY_TO_ONE:
                return AnnotationKey.MANY_TO_ONE
            case TableRelationship.ONE_TO_MANY:
                return AnnotationKey.ONE_TO_MANY
            case TableRelationship.MANY_TO_MANY:
                if self.isOwnerR:
                    return AnnotationKey.MANY_TO_MANY_REFERENCING
                else:
                    return AnnotationKey.MANY_TO_MANY_OWNER

    def getAnnotationKeyRight(self):
        match self.relationship:
            case TableRelationship.ONE_TO_ONE:
                if self.isOwnerR:
                    return AnnotationKey.ONE_TO_ONE_OWNER
                else:
                    return AnnotationKey.ONE_TO_ONE_REFERENCING
            case TableRelationship.MANY_TO_ONE:
                return AnnotationKey.MANY_TO_ONE
            case TableRelationship.ONE_TO_MANY:
                return AnnotationKey.ONE_TO_MANY
            case TableRelationship.MANY_TO_MANY:
                if self.isOwnerR:
                    return AnnotationKey.MANY_TO_MANY_OWNER
                else:
                    return AnnotationKey.MANY_TO_MANY_REFERENCING

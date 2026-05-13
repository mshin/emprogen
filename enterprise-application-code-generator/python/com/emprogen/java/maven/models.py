from enum import Enum


class Gav:
    def __init__(self, group_id: str, artifact_id: str, version: str):
        self.group_id = group_id
        self.artifact_id = artifact_id
        self.version = version

    def __repr__(self):
        return '%s:%s:%s' % (self.group_id, self.artifact_id, self.version)


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
    def __init__(
        self,
        ent_name_left: str,
        ent_name_right: str,
        relationship: TableRelationship,
        is_ref_left: bool,
        is_ref_right: bool,
        is_owner_right: bool
    ):
        self.ent_name_left = ent_name_left
        self.ent_name_right = ent_name_right
        self.relationship = relationship
        self.is_ref_left = is_ref_left
        self.is_ref_right = is_ref_right
        self.is_owner_right = is_owner_right

    def __repr__(self):
        return (
            '[%s: %s %s %s; left reference: %s | right reference: %s | is owner right: %s]'
            % (
                self.__class__.__name__,
                self.ent_name_left,
                self.relationship,
                self.ent_name_right,
                self.is_ref_left,
                self.is_ref_right,
                self.is_owner_right,
            )
        )

    def get_annotation_key_left(self):
        match self.relationship:
            case TableRelationship.ONE_TO_ONE:
                if self.is_owner_right:
                    return AnnotationKey.ONE_TO_ONE_REFERENCING
                else:
                    return AnnotationKey.ONE_TO_ONE_OWNER
            case TableRelationship.MANY_TO_ONE:
                return AnnotationKey.MANY_TO_ONE
            case TableRelationship.ONE_TO_MANY:
                return AnnotationKey.ONE_TO_MANY
            case TableRelationship.MANY_TO_MANY:
                if self.is_owner_right:
                    return AnnotationKey.MANY_TO_MANY_REFERENCING
                else:
                    return AnnotationKey.MANY_TO_MANY_OWNER

    def get_annotation_key_right(self):
        match self.relationship:
            case TableRelationship.ONE_TO_ONE:
                if self.is_owner_right:
                    return AnnotationKey.ONE_TO_ONE_OWNER
                else:
                    return AnnotationKey.ONE_TO_ONE_REFERENCING
            case TableRelationship.MANY_TO_ONE:
                return AnnotationKey.MANY_TO_ONE
            case TableRelationship.ONE_TO_MANY:
                return AnnotationKey.ONE_TO_MANY
            case TableRelationship.MANY_TO_MANY:
                if self.is_owner_right:
                    return AnnotationKey.MANY_TO_MANY_OWNER
                else:
                    return AnnotationKey.MANY_TO_MANY_REFERENCING

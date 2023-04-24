#!/usr/local/bin/python3

class Gav:
    def __init__(self, groupId: 'str', artifactId: 'str', version: 'str'):
        self.groupId = groupId
        self.artifactId = artifactId
        self.version = version

    def __repr__(self):
        return '[%s %s:%s:%s]' % (self.__class__.__name__, 
        self.groupId, self.artifactId, self.version)

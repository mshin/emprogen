import importlib

from com.emprogen.java.maven.models import Gav

def generate(descriptor: 'dict', archetypeGav: 'Gav' = Gav('com.emprogen', 'service-jaxrs-quarkus-p0-archetype', '0.0.1')
        , *, filesPath: 'str' = None, javaVersion: 'str' = '11') -> None:

    print('in service.jaxrs.quarkus.p0.v11.generate.py')
    script = importlib.import_module('com.emprogen.java.maven.service.jaxrs.quarkus.p0.v1.generate')
    script.generate(descriptor, archetypeGav, filesPath=filesPath, javaVersion=javaVersion)
 
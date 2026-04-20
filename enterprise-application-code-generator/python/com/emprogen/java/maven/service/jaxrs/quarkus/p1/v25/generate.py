import importlib

from com.emprogen.java.maven.models import Gav

def generate(descriptor: 'dict', archetypeGav: 'Gav' = Gav('com.emprogen', 'service-jaxrs-quarkus-p1-archetype', '0.0.2')
        , *, filesPath: 'str' = None, javaVersion: 'str' = '25', **kwargs) -> None:

    print('in service.jaxrs.quarkus.p1.v25.generate.py')
    script = importlib.import_module('com.emprogen.java.maven.service.jaxrs.quarkus.p1.v1.generate')
    script.generate(descriptor, archetypeGav, filesPath=filesPath, javaVersion=javaVersion, **kwargs)
 
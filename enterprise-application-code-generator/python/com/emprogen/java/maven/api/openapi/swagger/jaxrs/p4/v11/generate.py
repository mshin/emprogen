import importlib

def generate(descriptor: 'dict', *, filesPath: 'str' = None, javaVersion: 'str' = '11', jaxrs='jakarta') -> None:

    print('in openapi.swagger.jaxrs.p4.v11.generate.py')

    script = importlib.import_module('com.emprogen.java.maven.api.openapi.swagger.jaxrs.p4.v1.generate')
    script.generate(descriptor, filesPath=filesPath, javaVersion=javaVersion, jaxrs=jaxrs)
 
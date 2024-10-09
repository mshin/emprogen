import importlib

def generate(descriptor: 'dict', *, filesPath: 'str' = None, javaVersion: 'str' = '8', jaxrs='jakarta') -> None:

    print('in openapi.swagger.jaxrs.p5.v8.jakarta.generate.py')

    script = importlib.import_module('com.emprogen.java.maven.api.openapi.swagger.jaxrs.p5.v1.generate')
    script.generate(descriptor, files_path=filesPath, java_version=javaVersion, jaxrs=jaxrs)
 
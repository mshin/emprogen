import importlib
from com.emprogen.java.maven.models import Gav

def generate(descriptor: 'dict', *, filesPath: 'str' = None, javaVersion: 'str' = '8', jaxrs='javax', **kwargs) -> None:

    print('in openapi.swagger.jaxrs.p5.v8.javax.generate.py')

    script = importlib.import_module('com.emprogen.java.maven.api.openapi.swagger.jaxrs.p5.v1.generate')

    extra_kwargs = {
        'javax_gen_gav': Gav('com.emprogen', 'api-openapi-swagger-jakarta-3-archetype', '0.0.1'),
        'microprofile_gav': Gav('org.eclipse.microprofile.openapi', 'microprofile-openapi-api', '1.1.2'),
        'jakarta_validation_gav': Gav('jakarta.validation', 'jakarta.validation-api', '3.0.2'),
        # 'javax_validation_gav': Gav('javax.validation', 'javax.validation-api', '2.0.1.Final'), # 1.1.0.Final-redhat-00002
        'jackson_ann_gav': Gav('com.fasterxml.jackson.core', 'jackson-annotations', '2.9.10'),
        'javax_rs_gav': Gav('javax.ws.rs', 'javax.ws.rs-api', '2.1.1')
    }
    kwargs.update(extra_kwargs)

    script.generate(descriptor, files_path=filesPath, java_version=javaVersion, jaxrs=jaxrs, **kwargs)
 
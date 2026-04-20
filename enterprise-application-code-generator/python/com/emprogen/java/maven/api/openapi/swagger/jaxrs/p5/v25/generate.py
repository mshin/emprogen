import importlib
from com.emprogen.java.maven.models import Gav

def generate(descriptor: 'dict', *, filesPath: 'str' = None, javaVersion: 'str' = '25', jaxrs='jakarta', **kwargs) -> None:

    print('in openapi.swagger.jaxrs.p5.v25.generate.py')

    script = importlib.import_module('com.emprogen.java.maven.api.openapi.swagger.jaxrs.p5.v1.generate')

    extra_kwargs = {
        'microprofile_gav': Gav('org.eclipse.microprofile.openapi', 'microprofile-openapi-api', '4.1.1'),
        'jakarta_validation_gav': Gav('jakarta.validation', 'jakarta.validation-api', '3.1.1'),
        'jackson_ann_gav': Gav('com.fasterxml.jackson.core', 'jackson-annotations', '2.21'),
        'jakarta_rs_gav': Gav('jakarta.ws.rs', 'jakarta.ws.rs-api', '3.1.0')
    }
    kwargs.update(extra_kwargs)

    script.generate(descriptor, files_path=filesPath, java_version=javaVersion, jaxrs=jaxrs, **kwargs)
 
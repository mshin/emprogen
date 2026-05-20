import importlib
from pathlib import Path

from com.emprogen.java.maven.models import Gav


def generate(
    descriptor: dict,
    *,
    files_path: str | Path = None,
    java_version: str = '8',
    jaxrs='jakarta',
    **kwargs
) -> None:
    print('in openapi.swagger.jaxrs.p5.v8.jakarta.generate.py')

    script = importlib.import_module('com.emprogen.java.maven.api.openapi.swagger.jaxrs.p5.v1.generate')

    extra_kwargs = {
        'microprofile_gav': Gav('org.eclipse.microprofile.openapi', 'microprofile-openapi-api', '1.1.2'),
        'jakarta_validation_gav': Gav('jakarta.validation', 'jakarta.validation-api', '3.0.2'),
        'jackson_ann_gav': Gav('com.fasterxml.jackson.core', 'jackson-annotations', '2.9.10'),
        'jakarta_rs_gav': Gav('jakarta.ws.rs', 'jakarta.ws.rs-api', '3.1.0')
    }
    kwargs.update(extra_kwargs)

    script.generate(descriptor, files_path=files_path, java_version=java_version, jaxrs=jaxrs, **kwargs)
 
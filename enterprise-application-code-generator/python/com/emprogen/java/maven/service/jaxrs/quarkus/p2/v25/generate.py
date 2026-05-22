import importlib

from com.emprogen.java.maven.models import Gav

SCRIPT_VERSION = 'java.maven.service.jaxrs.quarkus.p2.v25.generate.py'


def generate(
    descriptor: dict,
    archetype_gav: Gav = Gav(
        'com.emprogen',
        'service-jaxrs-quarkus-p1-archetype',
        '0.0.2'
    ),
    *,
    files_path: str = None,
    java_version: str = '25',
    **kwargs
) -> None:
    print(f'in {SCRIPT_VERSION}')
    script = importlib.import_module('com.emprogen.java.maven.service.jaxrs.quarkus.p2.v1.generate')
    kwargs.update({'script_version': SCRIPT_VERSION})
    script.generate(descriptor, archetype_gav, files_path=files_path, java_version=java_version, **kwargs)
 
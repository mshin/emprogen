#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path
import argparse

import com.emprogen.file_functions as filef

ROOT_PATH = Path(__file__).parent
CEJM_PATH = ROOT_PATH / 'test_functional' / 'com' / 'emprogen' / 'java' / 'maven'
TMP_PATH = ROOT_PATH / 'test_functional' / 'tmp'


def run_for_definition_path_str(definition_path_str) -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT_PATH / 'run.py'), definition_path_str],
        capture_output=True,
        text=True,
        cwd=ROOT_PATH / 'test_functional' / 'tmp'
    )
    print(result.stdout)
    print(result.stderr)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run functional tests or clear tmp directory.")
    parser.add_argument('-c', '--clear', action='store_true', help='Only clear the tmp directory and exit.')
    args = parser.parse_args()

    if args.clear:
        print('clearing tmp directory')
        filef.clear_directory(TMP_PATH)
        sys.exit(0)

    print('clearing tmp directory')
    filef.clear_directory(TMP_PATH)

    print('Running functional tests.')
    print('This may take a few minutes...')

    print('com.emprogen.java.maven.api.openapi.swagger.jaxrs.p5')
    definition_path_str = str(CEJM_PATH / 'api' / 'openapi' / 'swagger' / 'jaxrs' / 'p5' / 'definition')
    run_for_definition_path_str(definition_path_str)

    print('com.emprogen.java.maven.service.jaxrs.quarkus.p2')
    definition_path_str = str(CEJM_PATH / 'service' / 'jaxrs' / 'quarkus' / 'p2' / 'definition')
    run_for_definition_path_str(definition_path_str)

    print('com.emprogen.java.maven.model.lombok.domain.p1')
    definition_path = str(CEJM_PATH / 'model' / 'lombok' / 'domain' / 'p1' / 'descriptor.yaml')
    run_for_definition_path_str(definition_path)

    print('com.emprogen.java.maven.model.lombok.entity.p0')
    definition_path = str(CEJM_PATH / 'model' / 'lombok' / 'entity' / 'p0' / 'definition')
    run_for_definition_path_str(definition_path)

    print('com.emprogen.java.maven.model.lombok.jaxrs.p0')
    definition_path = str(CEJM_PATH / 'model' / 'lombok' / 'jaxrs' / 'p0' / 'descriptor.yaml')
    run_for_definition_path_str(definition_path)

    print('com.emprogen.java.maven.service.jaxrs.springboot.camel.p0')
    definition_path = str(CEJM_PATH / 'service' / 'jaxrs' / 'springboot' / 'camel' / 'p0' / 'descriptor.yaml')
    run_for_definition_path_str(definition_path)
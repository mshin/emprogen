#!/usr/bin/env python3

# run_all_tests.py
import unittest

def run_tests_for_directory(directory: str):
    loader = unittest.TestLoader()
    suite = loader.discover(directory)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

# TODO make platform agnostic
if __name__ == "__main__":
    print('running unit tests in com/emprogen')
    run_tests_for_directory('test_unit/com/emprogen')
    print('running unit tests in com/emprogen/java')
    run_tests_for_directory('test_unit/com/emprogen/java')
    print('running unit tests in com/emprogen/java/maven')
    run_tests_for_directory('test_unit/com/emprogen/java/maven')
    print('running unit tests in com/emprogen/java/maven/api/openapi/swagger/jaxrs')
    run_tests_for_directory('test_unit/com/emprogen/java/maven/api/openapi/swagger/jaxrs')
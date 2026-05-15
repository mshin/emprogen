#!/usr/bin/env python3

# run_all_tests.py
import unittest

def run_tests_for_directory(directory: str):
    loader = unittest.TestLoader()
    suite = loader.discover(directory)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

if __name__ == "__main__":
    print('running unit tests in com/emprogen')
    run_tests_for_directory('test/com/emprogen')
    print('running unit tests in com/emprogen/java')
    run_tests_for_directory('test/com/emprogen/java')
    print('running unit tests in com/emprogen/java/maven')
    run_tests_for_directory('test/com/emprogen/java/maven')

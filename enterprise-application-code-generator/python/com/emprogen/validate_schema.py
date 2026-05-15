#!/usr/bin/env python3
import jsonschema as js
import yaml


def validate_yaml(yaml_doc_to_test_url: str, schema_url: str) -> None:
    """
    Validate a YAML document against a schema.
    Returns None if valid, raises ValidationError if invalid.
    """
    with open(yaml_doc_to_test_url, 'r') as yaml_file:
        yaml_doc_to_test = yaml.safe_load(yaml_file)
    with open(schema_url, 'r') as schema_file:
        schema = yaml.safe_load(schema_file)
    return validate(yaml_doc_to_test, schema)


def validate(yaml_doc_to_test: dict, schema: dict) -> None:
    """
    Validate the given YAML document against the provided schema.
    Returns None if valid, raises ValidationError if invalid.
    Usage: is_invalid = validate()
    """
    js.validate(yaml_doc_to_test, schema)

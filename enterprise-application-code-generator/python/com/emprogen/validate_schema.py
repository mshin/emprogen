#!/usr/local/bin/python3

import jsonschema as js
import yaml

def validateYaml(yamlDocToTestUrl: 'str', schemaUrl: 'str') -> 'None or ValidationError':
    return validate(yaml.load(yamlDocToTestUrl), yaml.load(schemaUrl))

"isInvalid = validate()"
def validate(yamlDocToTest: 'str', schema: 'str') -> 'None or ValidationError':
        js.validate(yamlDocToTest, schema)
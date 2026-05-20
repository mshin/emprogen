#!/usr/bin/env python3
import json
import yaml
from pathlib import Path
from typing import Any

from com.emprogen.java.maven.models import Gav


def yamlToJson(yaml_str: str) -> str:
    return yaml_to_json(yaml_str)

def jsonToYaml(json_str: str) -> str:
    return json_to_yaml(json_str)

def loadOpenApi3(doc_path: str) -> dict:
    return load_open_api3(doc_path)

def loadYamlDocs(proj_desc_loc: str) -> list[dict]:
    return load_yaml_docs(proj_desc_loc)

def getArchetypeGav(yaml: dict) -> Gav:
    return get_archetype_gav(yaml)

def getGeneratedProjectGav(yaml: dict) -> Gav:
    return get_generated_project_gav(yaml)

def getGav(gav_str: str) -> Gav:
    return get_gav(gav_str)

def getFieldsAndTypes(model_dict: dict) -> dict[str, str]:
    return get_fields_and_types(model_dict)

def getEnumValues(enum_dict: dict) -> list:
    return get_enum_values(enum_dict)


def yaml_to_json(yaml_str: str) -> str:
    return json.dumps(yaml.safe_load(yaml_str), indent=2)


def json_to_yaml(json_str: str) -> str:
    return yaml.dump(json.loads(json_str), default_flow_style=False)


def load_open_api3(doc_path: str | Path) -> dict:
    doc_path_str = str(doc_path)
    ext = doc_path_str.split('.')[-1]
    print('ext: ' + ext)
    if ext == 'json':
        with open(doc_path_str) as f:
            return json.load(f)
    elif ext == 'yaml' or ext == 'yml':
        with open(doc_path_str) as f:
            return yaml.safe_load(f)
    else:
        raise ValueError(f"Unsupported file extension: {ext}")


def load_yaml_docs(proj_desc_loc: str | Path) -> list[dict]: 
    with open(proj_desc_loc) as f:
        gen = yaml.safe_load_all(f)
        #file closes before can read all stuff out of gen, so turn to list
        return list(gen)


def get_archetype_gav(yaml: dict) -> Gav:
    gav_str = yaml['archetypeGAV']
    return get_gav(gav_str)


def get_generated_project_gav(yaml: dict) -> Gav:
    gav_str = yaml['generatedGav']
    return get_gav(gav_str)


"gav_str is groupId:artifactId:version"
def get_gav(gav_str: str) -> Gav:
    gav_list = gav_str.split(':')
    version = None
    if len(gav_list) > 2:
        version = gav_list[2]
    return Gav(gav_list[0], gav_list[1], version)


"dict field:type"
def get_fields_and_types(model_dict: dict) -> dict[str, str]:
    fields_dict = {}
    if model_dict:
        field_list = model_dict.get('fields', [])
        for f in field_list:
            type_to_field = f.split(':')
            fields_dict[type_to_field[1]] = type_to_field[0]
    return fields_dict


def get_enum_values(enum_dict: dict) -> list:
    enum_values = []
    if enum_dict:
        enum_values = enum_dict['values']
    return enum_values

print('loaded ' + __file__)

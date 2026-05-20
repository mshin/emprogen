import unittest
import json
import yaml
from unittest.mock import patch, mock_open

from com.emprogen.java.maven.yaml_functions import (
    yaml_to_json,
    json_to_yaml,
    load_open_api3,
    load_yaml_docs,
    get_archetype_gav,
    get_generated_project_gav,
    get_gav,
    get_fields_and_types,
    get_enum_values,
)
from com.emprogen.java.maven.models import Gav

class TestYamlFunctions(unittest.TestCase):
    def test_yaml_to_json(self):
        yaml_str = "a: 1\nb: 2"
        expected = json.dumps({'a': 1, 'b': 2}, indent=2)
        self.assertEqual(yaml_to_json(yaml_str), expected)

    def test_json_to_yaml(self):
        json_str = '{"a": 1, "b": 2}'
        expected = yaml.dump({'a': 1, 'b': 2}, default_flow_style=False)
        self.assertEqual(json_to_yaml(json_str), expected)

    @patch("builtins.open", new_callable=mock_open, read_data='{"openapi": "3.0.0"}')
    def test_load_open_api3_json(self, mock_file):
        result = load_open_api3("api.json")
        self.assertEqual(result, {"openapi": "3.0.0"})

    @patch("builtins.open", new_callable=mock_open, read_data="openapi: 3.0.0")
    def test_load_open_api3_yaml(self, mock_file):
        result = load_open_api3("api.yaml")
        self.assertEqual(result, {"openapi": "3.0.0"})

    @patch("builtins.open", new_callable=mock_open, read_data="---\na: 1\n---\nb: 2")
    def test_load_yaml_docs(self, mock_file):
        result = load_yaml_docs("docs.yaml")
        self.assertEqual(result, [{"a": 1}, {"b": 2}])

    def test_get_archetype_gav(self):
        d = {"archetypeGAV": "g:a:v"}
        with patch("com.emprogen.java.maven.yaml_functions.get_gav", return_value=Gav("g", "a", "v")) as mock_get_gav:
            result = get_archetype_gav(d)
            mock_get_gav.assert_called_with("g:a:v")
            self.assertIsInstance(result, Gav)

    def test_get_generated_project_gav(self):
        d = {"generatedGav": "g:a:v"}
        with patch("com.emprogen.java.maven.yaml_functions.get_gav", return_value=Gav("g", "a", "v")) as mock_get_gav:
            result = get_generated_project_gav(d)
            mock_get_gav.assert_called_with("g:a:v")
            self.assertIsInstance(result, Gav)

    def test_get_gav(self):
        result = get_gav("g:a:v")
        self.assertIsInstance(result, Gav)
        self.assertEqual((result.group_id, result.artifact_id, result.version), ("g", "a", "v"))

    def test_get_fields_and_types(self):
        d = {"fields": ["str:name", "int:age"]}
        result = get_fields_and_types(d)
        self.assertEqual(result, {"name": "str", "age": "int"})

    def test_get_enum_values(self):
        d = {"values": ["A", "B", "C"]}
        result = get_enum_values(d)
        self.assertEqual(result, ["A", "B", "C"])

if __name__ == "__main__":
    unittest.main()
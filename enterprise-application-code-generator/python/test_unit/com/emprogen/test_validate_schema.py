import unittest
import tempfile
import os
import yaml
import jsonschema

from com.emprogen.validate_schema import validate_yaml

VALID_YAML = {'name': 'test', 'age': 30}
VALID_SCHEMA = {
    'type': 'object',
    'properties': {
        'name': {'type': 'string'},
        'age': {'type': 'number'}
    },
    'required': ['name', 'age']
}
INVALID_YAML = {'name': 'test'}  # Missing 'age'

class TestValidateSchema(unittest.TestCase):
    def setUp(self):
        # Create temp files for YAML and schema
        self.yaml_file = tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.yaml')
        self.schema_file = tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.yaml')
        self.yaml_path = self.yaml_file.name
        self.schema_path = self.schema_file.name

    def tearDown(self):
        self.yaml_file.close()
        self.schema_file.close()
        os.unlink(self.yaml_path)
        os.unlink(self.schema_path)

    def write_yaml_and_schema(self, yaml_content, schema_content):
        self.yaml_file.seek(0)
        self.yaml_file.truncate()
        yaml.dump(yaml_content, self.yaml_file)
        self.yaml_file.flush()
        self.schema_file.seek(0)
        self.schema_file.truncate()
        yaml.dump(schema_content, self.schema_file)
        self.schema_file.flush()

    def test_valid_yaml(self):
        self.write_yaml_and_schema(VALID_YAML, VALID_SCHEMA)
        # Should not raise
        validate_yaml(self.yaml_path, self.schema_path)

    def test_invalid_yaml(self):
        self.write_yaml_and_schema(INVALID_YAML, VALID_SCHEMA)
        with self.assertRaises(jsonschema.ValidationError):
            validate_yaml(self.yaml_path, self.schema_path)

if __name__ == '__main__':
    unittest.main()
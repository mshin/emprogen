import unittest
from com.emprogen.java.maven.field_functions import (
    map_fields_to_qualified_types,
    create_field_string
)

class TestFieldFunctions(unittest.TestCase):
    def test_map_fields_to_qualified_types_basic(self):
        field_to_type = {
            'id': 'Long',
            'name': 'String',
            'list': 'List<String>',
            'map': 'Map<String, Integer>'
        }
        type_to_pkg_type = {
            'Long': 'java.lang.Long',
            'String': 'java.lang.String',
            'List': 'java.util.List',
            'Map': 'java.util.Map',
            'Integer': 'java.lang.Integer'
        }
        expected = {
            'id': 'java.lang.Long',
            'name': 'java.lang.String',
            'list': 'java.util.List<java.lang.String>',
            'map': 'java.util.Map<java.lang.String, java.lang.Integer>'
        }
        result = map_fields_to_qualified_types(field_to_type, type_to_pkg_type)
        self.assertEqual(result, expected)

    def test_map_fields_to_qualified_types_partial(self):
        field_to_type = {'foo': 'CustomType', 'bar': 'String'}
        type_to_pkg_type = {'String': 'java.lang.String'}
        expected = {'foo': 'CustomType', 'bar': 'java.lang.String'}
        result = map_fields_to_qualified_types(field_to_type, type_to_pkg_type)
        self.assertEqual(result, expected)

    def test_create_field_string_no_annotation(self):
        field_to_pkg_type = {'id': 'java.lang.Long', 'name': 'java.lang.String'}
        expected = '\n    private java.lang.Long id;\n\n    private java.lang.String name;\n'
        result = create_field_string(field_to_pkg_type, False)
        self.assertEqual(result, expected)

    def test_create_field_string_with_annotation(self):
        field_to_pkg_type = {'id': 'java.lang.Long'}
        expected = '\n&%id&%\n    private java.lang.Long id;\n'
        result = create_field_string(field_to_pkg_type, True)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()
import unittest
from unittest.mock import patch, mock_open, MagicMock

from com.emprogen.java.maven.api.openapi.swagger.jaxrs.fix_nested_enum import (
    fix_nested_enum_classes,
    identify_nested_enum_classes,
    fix_nested_enum_class,
    is_nested_enum_class_missing_closing_bracket
)

SCRIPT = 'com.emprogen.java.maven.api.openapi.swagger.jaxrs.fix_nested_enum'

class TestFixNestedEnum(unittest.TestCase):
    @patch(SCRIPT + '.open', new_callable=mock_open, read_data='class Foo {\n    public enum Bar {\n        A, B;\n    }\n')
    @patch(SCRIPT + '.filef.get_in_file')
    def test_identify_nested_enum_classes(self, mock_get_in_file, mock_file):
        mock_get_in_file.return_value = True
        files = ['Foo.java']
        result = identify_nested_enum_classes(files)
        self.assertIn('Foo.java', result)
        self.assertTrue(result['Foo.java'].startswith('class Foo'))

    def test_fix_nested_enum_class(self):
        content = 'class Foo {\n    public enum Bar {\n        A, B;\n    }\n'
        fixed = fix_nested_enum_class(content)
        self.assertTrue(fixed.endswith('\n}'))

    def test_is_nested_enum_class_missing_closing_bracket_true(self):
        content = 'class Foo {\n    public enum Bar {\n        A, B;\n    }\n'
        self.assertTrue(is_nested_enum_class_missing_closing_bracket(content))

    def test_is_nested_enum_class_missing_closing_bracket_false(self):
        content = 'class Foo {\n    public enum Bar {\n        A, B;\n    }\n}'
        self.assertFalse(is_nested_enum_class_missing_closing_bracket(content))

    @patch(SCRIPT + '.open', new_callable=mock_open, read_data='class Foo {\n    public enum Bar {\n        A, B;\n    }\n')
    @patch(SCRIPT + '.filef.get_in_file')
    def test_fix_nested_enum_classes(self, mock_get_in_file, mock_file):
        mock_get_in_file.return_value = True
        files = ['Foo.java']
        # Patch fix_nested_enum_class to check if it's called
        with patch(SCRIPT + '.fix_nested_enum_class', return_value='fixed content') as mock_fix:
            fix_nested_enum_classes(files)
            mock_fix.assert_called_once()
            handle = mock_file()
            handle.write.assert_called_with('fixed content')

if __name__ == '__main__':
    unittest.main()
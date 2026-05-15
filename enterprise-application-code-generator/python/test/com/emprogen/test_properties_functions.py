import unittest
from unittest.mock import mock_open, patch
import tempfile
import os
from com.emprogen.properties_functions import get_property, load_properties_as_dict

class TestGetProperty(unittest.TestCase):
    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8')
        self.temp_file.write(
            "# This is a comment\n"
            "foo=bar\n"
            "\n"
            "baz=qux\n"
            "#baz=should_not_find\n"
        )
        self.temp_file.close()
        self.file_path = self.temp_file.name

    def tearDown(self):
        os.unlink(self.file_path)

    def test_property_found(self):
        self.assertEqual(get_property('foo', self.file_path), 'bar')
        self.assertEqual(get_property('baz', self.file_path), 'qux')

    def test_property_not_found(self):
        self.assertIsNone(get_property('notfound', self.file_path))

    def test_commented_property(self):
        self.assertNotEqual(get_property('baz', self.file_path), 'should_not_find')

    def test_empty_line(self):
        # No error should occur for empty lines
        self.assertIsNone(get_property('', self.file_path))

class TestLoadPropertiesAsDict(unittest.TestCase):
    def test_loads_properties(self):
        mock_data = "foo=bar\nbaz=qux\n"
        with patch("builtins.open", mock_open(read_data=mock_data)):
            result = load_properties_as_dict("dummy.properties")
            self.assertEqual(result, {"foo": "bar", "baz": "qux"})

    def test_ignores_comments_and_blank_lines(self):
        mock_data = "# comment\n\nfoo=bar\n#another\nbaz=qux\n"
        with patch("builtins.open", mock_open(read_data=mock_data)):
            result = load_properties_as_dict("dummy.properties")
            self.assertEqual(result, {"foo": "bar", "baz": "qux"})

    def test_raises_on_malformed_line(self):
        mock_data = "foo=bar\nbadline\nbaz=qux\n"
        with patch("builtins.open", mock_open(read_data=mock_data)):
            with self.assertRaises(Exception):
                load_properties_as_dict("dummy.properties")

if __name__ == '__main__':
    unittest.main()
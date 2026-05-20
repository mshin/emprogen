import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open, call, PropertyMock

from com.emprogen.java.maven.format_functions import (
    eclipse_formatter_validate, eclipse_formatter, beautify_imports
)

class TestFormatFunctions(unittest.TestCase):
    @patch('com.emprogen.java.maven.java_maven_functions.get_java_maven_path', return_value='/fake/java/maven/path')
    @patch('com.emprogen.java.maven.java_maven_functions.call_mvn_with_options')
    def test_eclipse_formatter_validate(self, mock_call_mvn, mock_get_path):
        eclipse_formatter_validate('/fake/pom.xml')
        mock_call_mvn.assert_called_once()
        _, kwargs = mock_call_mvn.call_args
        self.assertIn('goal', kwargs)
        self.assertTrue(kwargs['goal'].endswith(':validate'))
        self.assertEqual(kwargs['file'], '/fake/pom.xml')
        self.assertIn('configFile', kwargs)

    @patch('com.emprogen.java.maven.java_maven_functions.get_java_maven_path', return_value='/fake/java/maven/path')
    @patch('com.emprogen.java.maven.java_maven_functions.call_mvn_with_options')
    def test_eclipse_formatter(self, mock_call_mvn, mock_get_path):
        eclipse_formatter('/fake/pom.xml')
        mock_call_mvn.assert_called_once()
        _, kwargs = mock_call_mvn.call_args
        self.assertIn('goal', kwargs)
        self.assertTrue(kwargs['goal'].endswith(':format'))
        self.assertEqual(kwargs['file'], '/fake/pom.xml')
        self.assertIn('configFile', kwargs)

    @patch('builtins.open', new_callable=mock_open, read_data='line1\r\nline2\r\n')
    @patch('glob.glob', return_value=['src/Foo.java', 'src/Bar.java'])
    @patch('com.emprogen.java.maven.java_maven_functions.call_mvn_with_options')
    def test_beautify_imports(self, mock_call_mvn, mock_glob, mock_file):
        with patch('pathlib.Path.parent', new_callable=PropertyMock, return_value=Path('/fake')):
            beautify_imports('/fake/pom.xml')
        mock_call_mvn.assert_called_once()
        # Check that open was called for each file
        expected_calls = [
            call(Path('/fake') / 'src/Foo.java', 'r+', encoding='utf-8'),
            call(Path('/fake') / 'src/Bar.java', 'r+', encoding='utf-8')
        ]
        mock_file.assert_has_calls(expected_calls, any_order=True)
        # Check that carriage returns are removed
        handle = mock_file()
        handle.write.assert_any_call('line1\nline2\n')

if __name__ == '__main__':
    unittest.main()
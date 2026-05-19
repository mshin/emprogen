import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.modules['com.emprogen.file_functions'] = MagicMock()
sys.modules['com.emprogen.subprocess_functions'] = MagicMock()
sys.modules['com.emprogen.xml_functions'] = MagicMock()

from com.emprogen.java.maven.java_maven_functions import (
    get_model_path,
    get_test_model_path,
    get_package,
    call_mvn_with_options,
    add_dependency,
    remove_dependency,
    gav_to_jar_local_abs_path_str
)
from com.emprogen.java.maven.models import Gav


class TestJavaMavenScript(unittest.TestCase):
    def test_get_model_path(self):
        gav = Gav('com.example', 'my-artifact', '1.0.0')
        result = get_model_path(gav)
        self.assertIsInstance(result, Path)
        expected = Path('my-artifact') / 'src' / 'main' / 'java' / 'com' / 'example' / 'my' / 'artifact'
        self.assertEqual(result, expected)

    def test_get_test_model_path(self):
        gav = Gav('com.example', 'my-artifact', '1.0.0')
        result = get_test_model_path(gav)
        self.assertIsInstance(result, Path)
        expected = Path('my-artifact') / 'src' / 'test' / 'java' / 'com' / 'example' / 'my' / 'artifact'
        self.assertEqual(result, expected)

    def test_get_package(self):
        gav = Gav('com.example', 'my-artifact', '1.0.0')
        self.assertEqual(get_package(gav), 'com.example.my.artifact')

    @patch('com.emprogen.subprocess_functions.run_subprocess')
    def test_call_mvn_with_options(self, mock_run):
        call_mvn_with_options(goal='clean', file='pom.xml', groupId='g', artifactId='a')
        args = mock_run.call_args[0][0]
        self.assertIn('clean', args)
        self.assertIn('-f', args)
        self.assertIn('pom.xml', args)
        self.assertIn('-DgroupId=g', args)
        self.assertIn('-DartifactId=a', args)

    @patch('xml.etree.ElementTree.parse')
    def test_add_dependency(self, mock_parse):
        mock_tree = MagicMock()
        mock_root = MagicMock()
        mock_tree.getroot.return_value = mock_root
        mock_parse.return_value = mock_tree
        mock_root.find.return_value = None
        gav = Gav('g', 'a', '1.0')
        with patch('xml.etree.ElementTree.SubElement') as mock_sub:
            add_dependency('pom.xml', gav)
            self.assertTrue(mock_sub.called)

    @patch('xml.etree.ElementTree.parse')
    def test_remove_dependency(self, mock_parse):
        mock_tree = MagicMock()
        mock_root = MagicMock()
        mock_tree.getroot.return_value = mock_root
        mock_parse.return_value = mock_tree
        mock_elem = MagicMock()
        mock_parent = MagicMock()
        mock_root.find.side_effect = [mock_elem, mock_parent]
        gav = Gav('g', 'a', '1.0')
        remove_dependency('pom.xml', gav)
        mock_parent.remove.assert_called_with(mock_elem)

    def test_gav_to_path(self):
        gav_str = 'com.example:my-artifact:1.0.0'
        path = gav_to_jar_local_abs_path_str(gav_str)
        self.assertTrue(path.endswith(
            os.path.join('.m2', 'repository', 'com', 'example', 'my-artifact', '1.0.0', 'my-artifact-1.0.0.jar')
        ))

if __name__ == '__main__':
    unittest.main()
import unittest
import tempfile
import zipfile
import os
from unittest.mock import patch

from com.emprogen.java.jar_functions import (
    get_files_from_jar, read_content_from_jar_class
)

class TestJarFunctions(unittest.TestCase):
    def setUp(self):
        # Create a temporary JAR file
        self.temp_jar = tempfile.NamedTemporaryFile(delete=False, suffix='.jar')
        with zipfile.ZipFile(self.temp_jar.name, 'w') as jar:
            jar.writestr('com/example/Foo.class', b'class data')
            jar.writestr('com/example/Bar.class', b'class data')
            jar.writestr('com/example/readme.txt', b'text')
            jar.writestr('com/example/', b'')  # Folder entry
        self.jar_path = self.temp_jar.name

    def tearDown(self):
        os.unlink(self.jar_path)

    def test_get_files_from_jar_all(self):
        files = get_files_from_jar(self.jar_path, exclude_folders=False)
        self.assertIn('com/example/Foo.class', files)
        self.assertIn('com/example/Bar.class', files)
        self.assertIn('com/example/readme.txt', files)
        self.assertIn('com/example/', files)

    def test_get_files_from_jar_exclude_folders(self):
        files = get_files_from_jar(self.jar_path, exclude_folders=True)
        self.assertIn('com/example/Foo.class', files)
        self.assertNotIn('com/example/', files)

    def test_get_files_from_jar_extension_filter(self):
        files = get_files_from_jar(self.jar_path, extension_filter='.class')
        self.assertIn('com/example/Foo.class', files)
        self.assertIn('com/example/Bar.class', files)
        self.assertNotIn('com/example/readme.txt', files)

    @patch('com.emprogen.subprocess_functions.run_subprocess_capture_output')
    def test_read_content_from_jar_class(self, mock_run):
        mock_run.return_value = 'mocked javap output'
        output = read_content_from_jar_class(self.jar_path, 'com.example.Foo')
        self.assertEqual(output, 'mocked javap output')
        mock_run.assert_called_once_with(['javap', '-v', '-cp', self.jar_path, 'com.example.Foo'])

if __name__ == '__main__':
    unittest.main()
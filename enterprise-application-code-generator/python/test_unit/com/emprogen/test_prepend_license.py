import unittest
from unittest.mock import patch, mock_open, MagicMock
from pathlib import Path

from com.emprogen.prepend_license import (
    prepend_license,
    process_licenses,
    prepend_licenses
)

class TestPrependLicense(unittest.TestCase):
    @patch('com.emprogen.prepend_license.open', new_callable=mock_open, read_data='original content')
    def test_prepend_license(self, mock_file):
        file_path = 'test.txt'
        license_text = 'LICENSE TEXT'
        prepend_license(file_path, license_text)
        mock_file.assert_called_with(file_path, 'r+')
        handle = mock_file()
        handle.write.assert_any_call(license_text + '\n' + 'original content')
        handle.truncate.assert_called_once()

    @patch('com.emprogen.prepend_license.open', new_callable=mock_open, read_data='LICENSE')
    @patch('com.emprogen.prepend_license.filef.get_files_list_by_extension_dict')
    @patch('com.emprogen.prepend_license.prepend_license')
    def test_process_licenses(self, mock_prepend, mock_get_files, mock_file):
        license_to_ext_dict = {'LICENSE.txt': ['py', 'md']}
        dir_path = 'project'
        descriptor_path = 'desc'
        mock_get_files.return_value = {
            'py': ['a.py', 'b.py'],
            'md': ['README.md']
        }
        process_licenses(license_to_ext_dict, dir_path, descriptor_path)
        mock_file.assert_called_with('desc/LICENSE.txt', 'r')
        mock_prepend.assert_any_call('a.py', 'LICENSE')
        mock_prepend.assert_any_call('b.py', 'LICENSE')
        mock_prepend.assert_any_call('README.md', 'LICENSE')
        self.assertEqual(mock_prepend.call_count, 3)

    @patch('com.emprogen.prepend_license.process_licenses')
    def test_prepend_licenses(self, mock_process):
        yaml_dict = {
            'license': [
                {'licenseFile': 'L1.txt', 'fileTypes': ['py']},
                {'licenseFile': 'L2.txt', 'fileTypes': ['md']}
            ]
        }
        prepend_licenses(yaml_dict, 'proj', 'desc')
        expected = {'L1.txt': ['py'], 'L2.txt': ['md']}
        mock_process.assert_called_once_with(expected, 'proj', 'desc')

if __name__ == '__main__':
    unittest.main()
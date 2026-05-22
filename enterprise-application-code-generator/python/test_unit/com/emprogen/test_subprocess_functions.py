import subprocess
import unittest
from unittest.mock import patch, MagicMock
from com.emprogen.subprocess_functions import (
    capture_contextual_command_line_options,
    run_subprocess,
    run_subprocess_capture_output
)

class TestSubprocessFunctions(unittest.TestCase):
    def test_capture_contextual_command_line_options_basic(self):
        args = ['mvn=-U,-DskipTests', 'java=-Dfile.encoding=UTF-8']
        self.assertEqual(
            capture_contextual_command_line_options(args, 'mvn'),
            ['-U', '-DskipTests']
        )
        self.assertEqual(
            capture_contextual_command_line_options(args, 'java'),
            ['-Dfile.encoding=UTF-8']
        )

    def test_capture_contextual_command_line_options_no_match(self):
        args = ['mvn=-U,-DskipTests']
        self.assertEqual(
            capture_contextual_command_line_options(args, 'python'),
            []
        )

    def test_capture_contextual_command_line_options_invalid_format(self):
        args = ['mvn-U,-DskipTests', 'java=-Dfile.encoding=UTF-8']
        self.assertEqual(
            capture_contextual_command_line_options(args, 'java'),
            ['-Dfile.encoding=UTF-8']
        )

    @patch('com.emprogen.subprocess_functions.subprocess.run')
    def test_run_subprocess(self, mock_run):
        args = ['echo', 'hello']
        run_subprocess(args)
        mock_run.assert_called_once_with(args, check=True, text=True)

    @patch('com.emprogen.subprocess_functions.subprocess.run')
    def test_run_subprocess_capture_output(self, mock_run):
        args = ['echo', 'hello']
        mock_result = MagicMock()
        mock_result.stdout = "hello\n"
        mock_run.return_value = mock_result
        output = run_subprocess_capture_output(args)
        mock_run.assert_called_once_with(
            args,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        self.assertEqual(output, "hello\n")

if __name__ == '__main__':
    unittest.main()
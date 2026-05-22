import unittest
import tempfile
import os
from pathlib import Path
from com.emprogen.file_functions import (
    copy_file, make_file, get_file_path, replace_file_contents,
    delete_file, delete_directory, replace_text_in_file_multi,
    replace_text_in_file, get_in_file, get_files_from_path
)

class TestFileFunctions(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.dir_path = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_make_file_and_content(self):
        file_path = self.dir_path / "test.txt"
        make_file(file_path, file_content="hello")
        self.assertTrue(file_path.exists())
        self.assertEqual(file_path.read_text(), "hello")

    def test_copy_file(self):
        src = self.dir_path / "src.txt"
        dst = self.dir_path / "subdir" / "dst.txt"
        make_file(src, file_content="copy me")
        copy_file(src, dst)
        self.assertTrue(dst.exists())
        self.assertEqual(dst.read_text(), "copy me")

    def test_get_file_path(self):
        file_path = self.dir_path / "foo" / "bar.txt"
        make_file(file_path, file_content="x")
        parent = get_file_path(file_path)
        self.assertEqual(parent, file_path.parent.resolve())

    def test_replace_file_contents(self):
        file_path = self.dir_path / "file.txt"
        make_file(file_path, file_content="old")
        replace_file_contents("new", file_path)
        self.assertEqual(file_path.read_text(), "new")

    def test_delete_file(self):
        file_path = self.dir_path / "del.txt"
        make_file(file_path, file_content="bye")
        delete_file(file_path)
        self.assertFalse(file_path.exists())

    def test_delete_directory(self):
        subdir = self.dir_path / "todel"
        file_path = subdir / "a.txt"
        make_file(file_path, file_content="x")
        delete_directory(subdir)
        self.assertFalse(subdir.exists())

    def test_replace_text_in_file_multi(self):
        file_path = self.dir_path / "multi.txt"
        make_file(file_path, file_content="foo bar baz foo")
        replace_text_in_file_multi({"foo": "FOO", "baz": "BAZ"}, file_path)
        self.assertEqual(file_path.read_text(), "FOO bar BAZ FOO")

    def test_replace_text_in_file(self):
        file_path = self.dir_path / "single.txt"
        make_file(file_path, file_content="abc abc abc")
        replace_text_in_file("abc", "123", file_path, count=2)
        self.assertEqual(file_path.read_text(), "123 123 abc")

    def test_get_in_file(self):
        file_path = self.dir_path / "find.txt"
        make_file(file_path, file_content="number: 42\nfoo")
        result = get_in_file(r"\d+", file_path)
        self.assertEqual(result, "42")
        result_none = get_in_file(r"notfound", file_path)
        self.assertIsNone(result_none)

    def test_get_files_from_path(self):
        subdir = self.dir_path / "a" / "b"
        file1 = self.dir_path / "root.txt"
        file2 = subdir / "deep.txt"
        make_file(file1, file_content="1")
        make_file(file2, file_content="2")
        files = get_files_from_path(self.dir_path)
        self.assertIn(str(file1), files)
        self.assertIn(str(file2), files)
        self.assertEqual(len(files), 2)

if __name__ == "__main__":
    unittest.main()
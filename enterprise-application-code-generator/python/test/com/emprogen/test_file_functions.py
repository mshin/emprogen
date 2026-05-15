import unittest
import tempfile
import os
import shutil

from com.emprogen.file_functions import (
    copy_file, make_file, get_file_path, replace_file_contents,
    delete_file, delete_directory, replace_text_in_file_multi,
    replace_text_in_file, get_in_file, get_files_from_path
)

# run with: python3 -m unittest test_file_functions.py
class TestFileFunctions(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "test.txt")
        with open(self.test_file, "w") as f:
            f.write("Hello World\nFoo Bar\nBaz")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_copy_file(self):
        dst = os.path.join(self.test_dir, "copy.txt")
        copy_file(self.test_file, dst)
        self.assertTrue(os.path.exists(dst))
        with open(dst) as f:
            self.assertEqual(f.read(), "Hello World\nFoo Bar\nBaz")

    def test_make_file(self):
        new_file = os.path.join(self.test_dir, "new.txt")
        make_file(self.test_dir, "new.txt", file_content="abc")
        self.assertTrue(os.path.exists(new_file))
        with open(new_file) as f:
            self.assertEqual(f.read(), "abc")

    def test_get_file_path(self):
        path = get_file_path(self.test_file)
        print(f'path: {path}')
        path = path.replace('/private', '') # for macOS temp dir
        self.assertEqual(path, os.path.dirname(self.test_file))

    def test_replace_file_contents(self):
        replace_file_contents("new content", self.test_file)
        with open(self.test_file) as f:
            self.assertEqual(f.read(), "new content")

    def test_delete_file(self):
        delete_file(self.test_file)
        self.assertFalse(os.path.exists(self.test_file))

    def test_delete_directory(self):
        subdir = os.path.join(self.test_dir, "subdir")
        os.makedirs(subdir)
        delete_directory(subdir)
        self.assertFalse(os.path.exists(subdir))

    def test_replace_text_in_file_multi(self):
        patterns = {"Hello": "Hi", "Foo": "Bar"}
        replace_text_in_file_multi(patterns, self.test_file)
        with open(self.test_file) as f:
            content = f.read()
        self.assertIn("Hi World", content)
        self.assertIn("Bar Bar", content)

    def test_replace_text_in_file(self):
        replace_text_in_file("Hello", "Hey", self.test_file)
        with open(self.test_file) as f:
            self.assertIn("Hey World", f.read())

    def test_get_in_file(self):
        match = get_in_file(r"Foo \w+", self.test_file)
        self.assertEqual(match, "Foo Bar")

    def test_get_files_from_path(self):
        subdir = os.path.join(self.test_dir, "subdir")
        os.makedirs(subdir)
        file1 = os.path.join(subdir, "a.txt")
        with open(file1, "w") as f:
            f.write("x")
        files = get_files_from_path(self.test_dir)
        self.assertIn(self.test_file, files)
        self.assertIn(file1, files)

if __name__ == "__main__":
    unittest.main()
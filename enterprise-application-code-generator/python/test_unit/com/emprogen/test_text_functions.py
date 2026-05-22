import unittest
from com.emprogen.text_functions import (
    lower_first, camel_to_snake, to_camel, clean_text
)

class TestTextFunctions(unittest.TestCase):
    def test_lower_first(self):
        self.assertEqual(lower_first("Hello"), "hello")
        self.assertEqual(lower_first("hello"), "hello")
        self.assertEqual(lower_first(""), "")
        self.assertEqual(lower_first("A"), "a")

    def test_camel_to_snake(self):
        self.assertEqual(camel_to_snake("CamelCase"), "camel_case")
        self.assertEqual(camel_to_snake("camelCase"), "camel_case")
        self.assertEqual(camel_to_snake("camel"), "camel")
        self.assertEqual(camel_to_snake("CamelCaseTest"), "camel_case_test")
        self.assertEqual(camel_to_snake(""), "")

    def test_to_camel(self):
        self.assertEqual(to_camel("snake_case"), "snakeCase")
        self.assertEqual(to_camel("kebab-case"), "kebabCase")
        self.assertEqual(to_camel("space case"), "spaceCase")
        self.assertEqual(to_camel("AlreadyCamel", is_lower_first=False), "AlreadyCamel")
        self.assertEqual(to_camel("AlreadyCamel", is_lower_first=True), "alreadyCamel")
        self.assertEqual(to_camel(""), "")

    def test_clean_text(self):
        self.assertEqual(clean_text("Hello\r\nWorld"), "Hello World")
        self.assertEqual(clean_text("Line-\nbreak"), "Line-break")
        self.assertEqual(clean_text("  Trim me\n"), "Trim me")
        self.assertEqual(clean_text("NoChange"), "NoChange")
        self.assertEqual(clean_text(""), "")

if __name__ == "__main__":
    unittest.main()
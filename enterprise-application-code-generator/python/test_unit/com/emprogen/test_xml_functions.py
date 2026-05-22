import os
import tempfile
import unittest
import xml.etree.ElementTree as et

from com.emprogen.xml_functions import add_xml_element, remove_xml_element

NAMESPACE = "http://example.com/ns"
et.register_namespace('', NAMESPACE)

SAMPLE_XML = f'''<?xml version="1.0"?>
<root xmlns="{NAMESPACE}">
    <parent>
        <child>value</child>
    </parent>
</root>
'''

# run with: python3 -m unittest test_xml_functions.py
class TestXMLFunctions(unittest.TestCase):
    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xml')
        self.temp_file.write(SAMPLE_XML.encode('utf-8'))
        self.temp_file.close()
        self.file_path = self.temp_file.name

    def tearDown(self):
        os.unlink(self.file_path)

    def test_add_xml_element(self):
        add_xml_element(
            self.file_path,
            NAMESPACE,
            ['parent'],
            {'newchild': 'newvalue'}
        )
        tree = et.parse(self.file_path)
        root = tree.getroot()
        ns = {'x': NAMESPACE}
        new_elem = root.find('./x:parent/x:newchild', ns)
        self.assertIsNotNone(new_elem)
        self.assertEqual(new_elem.text, 'newvalue')

    def test_remove_xml_element(self):
        # Add an element to remove
        add_xml_element(
            self.file_path,
            NAMESPACE,
            ['parent'],
            {'toremove': 'toremovevalue'}
        )
        # Remove the element
        remove_xml_element(
            self.file_path,
            NAMESPACE,
            ['parent'],
            {'toremove': 'toremovevalue'}
        )
        tree = et.parse(self.file_path)
        root = tree.getroot()
        ns = {'x': NAMESPACE}
        removed_elem = root.find('./x:parent/x:toremove', ns)
        self.assertIsNone(removed_elem)

if __name__ == '__main__':
    unittest.main()
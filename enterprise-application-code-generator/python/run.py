#!/usr/bin/env python3
import importlib
import os
import pathlib
from sys import argv

import com.emprogen.file_functions as FILEF
import com.emprogen.java.maven.yaml_functions as YF
import com.emprogen.validate_schema as VS

if not len(argv) > 1:
    raise ValueError('Must pass yaml descriptor for generating code as arg.')

# Command args should follow the pattern command=arg1,arg2,argN command2=arg21,arg22,arg2N, etc.
command_args = []
if len(argv) > 2:
    command_args = argv[2:len(argv)]
    print('Captured command args: ' + str(command_args))

# pass 1 arg in to this script.
# Can pass in a single descriptor yaml file.
# Can pass in a directory containing artifacts and /descriptor directory containing yaml documents containing the definitions of the artifacts.
# /descriptor/order.yaml contains the order of the documents to be generated in.

descriptor_path = argv[1]
descriptor_dir = os.path.join(descriptor_path, 'descriptor/')
yaml_list = []
if os.path.isfile(descriptor_path):
    yaml_list = YF.load_yaml_docs(descriptor_path)
# if directory passed in, iterate over every .yaml and .yml file in the directory and get the documents out to scan.
elif os.path.isdir(descriptor_dir):
    # if there is an order.txt file, use that as the order in which to read the yaml documents.
    doc_list = None
    order_txt_path = os.path.join(descriptor_dir, 'order.txt')
    if os.path.isfile(order_txt_path):
        with open(order_txt_path, 'r') as f:
            doc_list = [line.rstrip() for line in f]
    # get all the files from the directory and add them to the descriptor list.
    file_to_path = {}
    for f in os.listdir(descriptor_dir):
        file_path = os.path.join(descriptor_dir, f)
        if os.path.isfile(file_path):
            file_to_path[f] = file_path
    # if there's an order.txt file, sort the documents based on that.
    if doc_list:
        tmp_file_to_path_dict = {}
        for doc in doc_list:
            if doc.startswith('#') or doc.startswith('//'):
                continue
            tmp_file_to_path_dict[doc] = file_to_path.get(doc, None)
        file_to_path = tmp_file_to_path_dict

    # get the yaml docs and store them from all files into a combined yaml document list.
    for k, v in file_to_path.items():  # after CPython 3.6, dict maintains insertion order
        # for blank newline in order.txt doc
        if k is None or v is None:
            continue
        print('Loading yaml docs from file: ' + str(k) + ' at path: ' + str(v))
        tmp_yaml_list = YF.load_yaml_docs(v)
        yaml_list += tmp_yaml_list
else:
    print('Error while loading file descriptors. No descriptors found at expected locations: ' +
        descriptor_path + ' or: ' + descriptor_dir)
    quit()

# check if the 1st document is a stack descriptor. If so, run
first_document_is_stack_descriptor = False

for i, document_dict in enumerate(yaml_list):
    # prevent "---" end of doc in yaml from being treated as a document with no content.
    if document_dict is None:
        continue
    # Validate yaml descriptors against their schemas.
    pwd = str(FILEF.get_file_path(__file__)) + '/'
    schema_path = os.path.join(pwd, document_dict['id'].replace('.', '/'), 'schema.yaml')
    print('schema_path: ' + str(schema_path))
    schema_yaml_list = YF.load_yaml_docs(schema_path)
    schema = ''
    if schema_yaml_list and len(schema_yaml_list) > 0:
        schema = schema_yaml_list[0]

    VS.validate(document_dict, schema)
    if i == 0 and document_dict['id'] == 'idForStackDescriptor':
        first_document_is_stack_descriptor = True

if first_document_is_stack_descriptor:
    pass
    # TODO run stack descriptor.

for document_dict in yaml_list:
    # prevent "---" end of doc in yaml from being treated as a document with no content.
    if document_dict is None:
        continue
    # if not a stack descriptor,
    # find the script to run and run it.
    script_path = document_dict['id'] + '.generate'
    print('script_path: ' + script_path)
    script = importlib.import_module(script_path)
    opts_dict = {'command_args': command_args}
    script.generate(document_dict, files_path=descriptor_path, **opts_dict)

quit()

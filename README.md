# emprogen

## Instructions

`pip3 install enterprise-application-code-generator/python/requirements.txt`

### If you need to, build all the emprogen java code.
`cd enterprise-application-code-generator/java`
`mvn clean install`

### Generate code

#### Create descriptor
`cd` to the directory where you want to generate the code.
Make the following directories and files:
`mkdir definition/descriptor`
`touch definition/descriptor/descriptor.yaml`
`touch definition/descriptor/order.txt`
optional: `touch definition/my_openapi3_spec_doc.yaml`
`echo "descriptor.yaml" >> definition/descriptor/order.txt`

If you want to use multiple descriptors to generate code, you can put them all in the same yaml file, separated by: `\n---\n` (with no trailing 3-dash separator).
You can also put the descriptors across multiple files, all in the `definition/descriptor` directory. To control the order in which the files are called, define them, newline delimited, in the `order.txt` file.

The contents of the descriptor will be described by the `schema.yaml` example for the type of file you want to generate.

#### Run generator
`cd` to the directory where you want to generate the code. Run the code from the terminal, `run.py` script with argument being the directory with the descriptor code in it.

`./run.py definition`, where 'definition' is the location of the `definition` directory, and 'run.py' is wherever that script is located as well. Don't move the run.py script; it needs to be able to find the other python scripts which it finds by their relative position to it.

If there are no errors, the code will all be generated into the current directory from where you ran `run.py`.
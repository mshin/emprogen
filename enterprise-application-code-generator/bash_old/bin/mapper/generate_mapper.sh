#!/bin/bash

# $1: yaml descriptor path; $2 document number

dir=${0%/*}
source ${dir}/../common_scripts/functions.sh


# for each document in the yaml file
 # generate the maven project (build existing java file url.)
 # create new mapper for the two model jars given
  # create the file in same directory as other file.
  # replace the .java file name with model name
  # find the list of all the mapped properites
   # for each element in the list, create the method given the parameters given.
 # delete placeholder model

declare g a
generate_maven_project $1 $2 g a

mapper_path=${a}/src/main/java/${g//./\/}/${a//-/\/}

# create java interface at template location
mapper_name=$(yq r -d$2 $1 "mapperName")
mapper_path_name=${mapper_path}/${mapper_name}.java
echo "mapper_name: ${mapper_name}"

cp ${mapper_path}/class0.java "$mapper_path_name"

# set the class name in the file to the correct value.
sed -i.bak "s/class0/${mapper_name}/" "${mapper_path_name}" && rm "${mapper_path_name}.bak"

declare mapping_methods_string

# fix if no mapping objects present
num_objects_mapped=$(yq r -d$2 $1 "mappings" -l)

for (( i=0; i<${num_objects_mapped}; i++ ))
do
    # get mapping
    mapping=$(yq r -d$2 $1 "mappings[${i}]")

    # get mapFrom:mapTo objects
    mapping_arr=(${mapping//:/ })
    map_from=${mapping_arr[0]}
    map_to=${mapping_arr[1]}

    # add method to the methods string
    map_from_var="$(lower_first ${map_from##*.})"
    mapping_methods_string+="    ${map_to} map( ${map_from} ${map_from_var} );^^"

done

# replace map placeholder in java class with actual mapping methods
sed -i.bak "s/^    \/\/map()/${mapping_methods_string}/" "${mapper_path_name}" && rm "${mapper_path_name}.bak"

# use tr (translate) command to replace carrot with newline in java file.
tr ^ '\n' < "${mapper_path_name}" > "${mapper_path}/temp.java" && mv "${mapper_path}/temp.java" "${mapper_path_name}"

# delete placeholder model
rm ${mapper_path}/class0.java

# add addtl. dependencies to the project pom.

# count the addtl. dependencies.
num_addtl_dependencies=$(yq r -d$2 $1 "dependencyGav" -l)
# for each addtl. dependency...
for (( i=0; i<${num_addtl_dependencies}; i++ ))
do
    # get the gav string
    dependency_gav_string=$(yq r -d$2 $1 "dependencyGav[${i}].gav")

    echo "dependency_gav_string: $dependency_gav_string"
    echo "pom path: ${a}/pom.xml"
    # add the dependency to the pom.
    add_dependency "$dependency_gav_string" "${a}/pom.xml"
done

# call formatter on project
beautify_imports "$a" "${mapper_path}"

mvn clean install -f $a/pom.xml

exit 0

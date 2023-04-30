#!/bin/bash

# $1: yaml descriptor path; $2 document number

dir=${0%/*}
source ${dir}/../common_scripts/functions.sh
source ${dir}/../common_scripts/field_functions.sh


# for each document in the yaml file
 # generate the maven project (build existing java file url.)
 # create new models based on template
  # create the file in same directory as other file.
  # replace the .java file name with model name
  # replace the fields with a new field string
  # TODO update imports for fields.
 # delete placeholder model

declare g a
generate_maven_project $1 $2 g a

model_path=${a}/src/main/java/${g//./\/}/${a//-/\/}

class_content=$(<$model_path/class0.java)

# fix if models not present
num_models=$(yq r -d$2 $1 "model" -l)

for (( i=0; i<${num_models}; i++ ))
do
    # create java class at template location
    model_name=$(yq r -d$2 $1 "model[${i}].name")
    model_path_name=${model_path}/${model_name}.java
    echo "model_name${i}: ${model_name}"

    cp ${model_path}/class0.java "$model_path_name"

    # set the class name in the file to the correct value.
    sed -i.bak "s/class0/${model_name}/" "${model_path_name}" && rm "${model_path_name}.bak"

    # replace fields with generated fields.
    fields=$(yq r -d$2 $1 "model[${i}].fields[*]")
    get_fields_and_types "${fields}"
    field_string=$(create_field_string "false")

    #replace newline with carrots in field_string because sed has problem processing \n
    field_string=${field_string//$'\n'/^}

    # replace fields placeholder in java class with actual fields with ^
    sed -i.bak "s/^    fields/${field_string}/" "${model_path_name}" && rm "${model_path_name}.bak"

    # use tr (translate) command to replace carrot with newline in java file.
    tr ^ '\n' < "${model_path_name}" > "${model_path}/temp.java" && mv "${model_path}/temp.java" "${model_path_name}"

done

# delete placeholder model
rm ${model_path}/class0.java

enum_content=$(<$model_path/class1.java)

num_enums=$(yq r -d$2 $1 "enum" -l)

# fix if enums not present.
for (( i=0; i<${num_enums}; i++ ))
do
    # create java class at template location
    enum_name=$(yq r -d$2 $1 "enum[${i}].name")
    enum_path_name=${model_path}/${enum_name}.java
    echo "enum_name${i}: ${enum_name}"

    cp ${model_path}/class1.java "$enum_path_name"

    # set the class name in the file to the correct value.
    sed -i.bak "s/class1/${enum_name}/" "${enum_path_name}" && rm "${enum_path_name}.bak"

    # replace enum paceholder with generated enum values.
    # get enums from yaml
    enums=$(yq r -d$2 $1 "enum[${i}].values[*]")
    # put enum list delimited with newline into an array.
    enum_arr=(${enums})
    # add comma to the end of every element of array.
    enum_arr=( "${enum_arr[@]/%/,}" )
    # print out array as new single string. each element is delimted with a space.
    enum_list=$(echo "${enum_arr[@]}")
    # replace last character of enum_list (a comma) with a semicolon.
    enum_list=$(echo "${enum_list%?};")
    echo "$enum_list"

    # replace enum placeholder in java class with actual enums
    sed -i.bak "s/^    enumerations/${enum_list}/" "${enum_path_name}" && rm "${enum_path_name}.bak"

done

# delete placeholder enum
rm ${model_path}/class1.java

# add addtl. dependencies to the project pom.

# count the addtl. dependencies.
num_addtl_dependencies=$(yq r -d$2 $1 "dependencyGav" -l)
# for each addtl. dependency...
for (( i=0; i<${num_addtl_dependencies}; i++ ))
do
    # get the gav string
    dependency_gav_string=$(yq r -d$2 $1 "dependencyGav[${i}].gav")

    # add the dependency to the pom.
    add_dependency "$dependency_gav_string" "${a}/pom.xml"
done

# call formatter on project
beautify_imports "$a" "${model_path}"

mvn clean install -f $a/pom.xml

exit 0

#!/bin/bash

dir=${0%/*}
source ${dir}/../common_scripts/functions.sh
source ${dir}/../common_scripts/field_functions.sh

jpa_ann_prop_url=${dir}/jpa_type_annotation.properties

fields=$1
pk_field=$2

# $1=Type $2=fieldName $3=type.properties $4=pk
build_entity_column_annotation () {
    field_sql_case=$(convert_camel_to_sql_case "$2")
    prop_key=""
    replacement_string=""
    # if the annotation is a primary key, use that one, otherwise try to find it.
    if [[ "$2" = "$4" ]]; then
        prop_key="pk"
        replacement_string="${table_name_sql_case}"
    else 
        prop_key="$1"
        replacement_string="${field_sql_case}"
    fi
    # >&2 echo "prop_key:${prop_key} fieldName: ${2}"
    # get annotation value out of properties file; strip type package info if present.
    annotation=$(grep "^${prop_key##*.}=" "$3"  | cut -f2- -d'=')
    # if no annotation entry for Type in properties file, use default annotation
    if [[ -z "${annotation}" ]]; then
        annotation="    @javax.persistence.Column( name = \"%\" )"
    fi
    # replace the annotation placeholder for the field with the annotation.
    annotation="${annotation//\%/${replacement_string}}"
    echo "${annotation}"
    annotation=""
}

get_fields_and_types "${fields}"
field_string=$(create_field_string "true")

# replace all the annotation placeholders with the real annotations
for (( j=0; j<"${#field_arr[@]}"; j++ ))
do
    ann=$(build_entity_column_annotation ${type_arr[j]} ${field_arr[j]} ${jpa_ann_prop_url} ${pk_field})
    field_string="${field_string/&\%${field_arr[j]}&\%/${ann}}"
done

echo "${field_string}"

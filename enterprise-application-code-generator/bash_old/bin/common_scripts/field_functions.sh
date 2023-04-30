#!/bin/bash

declare -a type_arr field_arr

type_properties_url="${0%/*}/../java_type.properties"

# $1 fields
get_fields_and_types () {
    type_st=$(sed "s/:.*$//" <<< "${1}")
    field_st=$(sed "s/^.*://" <<< "${1}")
    oldIFS=${IFS}
    IFS=$'\n'
    type_arr=(${type_st})
    field_arr=(${field_st})
    IFS=${oldIFS}
    # field_arr=(${field_st//$'\n'/ })

    # replace common java se types with package data.
    for (( j=0; j<"${#type_arr[@]}"; j++ ))
    do

        # find all types for generics
        #replace < > , with space
        gen_type_arr=(${type_arr[j]//[<>,]/ })

        #if multiple things, find each. else, find the one.
        if [[ 1 -lt ${#gen_type_arr[@]} ]]
        then
            # make array have unique values
            gen_type_arr=($(echo "${gen_type_arr[@]}" | tr ' ' '\n' | sort -u | tr '\n' ' '))

            for (( k=0; k<"${#gen_type_arr[@]}"; k++ ))
            do
                # get type from java file
                gen_type=$(grep "^${gen_type_arr[k]}=" "${type_properties_url}"  | cut -f2- -d'=')
                # if the type was found, replace it in the variable.
                if [[ -n "${gen_type}" ]]; then
                    type_arr[j]="${type_arr[j]//${gen_type_arr[k]}/${gen_type}}"
                fi
            done
        else
            # single things. proceed normally.
            # get type from java file
            type=$(grep "^${type_arr[j]}=" "${type_properties_url}"  | cut -f2- -d'=')

            # if the type was found, replace it.
            if [[ -n "${type}" ]]; then
                type_arr[j]="${type}"
            fi
        fi

    done
}

# $1 isAddAnnotationPlaceholder
create_field_string () {
    out=""
    for (( j=0; j<"${#field_arr[@]}"; j++ ))
    do
        if [[ "true" = "$1" ]]
        then
            out="${out}^&%${field_arr[$j]}&%^    private ${type_arr[j]} ${field_arr[j]};^"
        else
            out="${out}^    private ${type_arr[j]} ${field_arr[j]};^"
        fi
    done
    echo "${out}"
    out=""
}

# $1 fields
create_field_string2 () {
    out=""
    # replace colon with \s
    out=${1//:/ }
    # add '    private ' to the beginning of each line
    out=$(sed "s/^/    private /" <<< "${out}")
    # add semicolon to the end of each line
    out=$(sed "s/$/;/" <<< "${out}")
    echo "${out}"
    out=""
}

# $1 field_string
create_field_string_with_annotations () {
    output=""
    k=0
    while IFS="" read -r p || [ -n "$p" ]
    do
        output+="&%${field_arr[$k]}&%^"
        output+="${p}^^"
        ((k++))
    done <<< "${1}"
    echo "${output}"
    output=""
}


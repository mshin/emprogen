#!/bin/bash

# $1: yaml descriptor path; $2 document number

dir=${0%/*}
source ${dir}/../common_scripts/functions.sh

create_fields_url=${dir}/create_entity_fields_w_annotations.sh
join_prop_url=${dir}/jpa_join_annotation.properties
type_converter_gav_url=${dir}/type_converter_gav.txt
local_date_converter="com.github.mshin.jpa.type.converter.LocalDateAttributeConverter"
local_date_time_converter="com.github.mshin.jpa.type.converter.LocalDateTimeAttributeConverter"

declare -a model_name_arr model_pk_arr
# $1 model_name
get_pk_for_model_name () {
    output=""
    
    for (( m=0; m<${#model_name_arr[@]}; m++ ))
    do
        if [[ "${model_name_arr[$m]}" = "$1" ]]; then
            output="${model_pk_arr[$m]}"
        fi
    done
    echo "${output}"
    output=""
}

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

num_models=$(yq r -d$2 $1 "model" -l)

for (( i=0; i<${num_models}; i++ ))
do
    # create java class at template location
    model_name=$(yq r -d$2 $1 "model[${i}].name")
    model_path_name=${model_path}/${model_name}.java
    echo "model_name${i}: ${model_name}"

    cp ${model_path}/class0.java "$model_path_name"

    # set the class name in the file to the correct value.
    sed -i.bak "s/^public class class0/public class ${model_name}/" "${model_path_name}" && rm "${model_path_name}.bak"

    # set the table name in the file to the generated value TODO allow to be set from properties file
    table_name="${model_name%Entity}"
    table_name_sql_case=$(convert_camel_to_sql_case "${table_name}")
    sed -i.bak "s/entity_name/${table_name_sql_case}/" "${model_path_name}" && rm "${model_path_name}.bak"

    # replace fields with generated fields.
    fields=$(yq r -d$2 $1 "model[${i}].fields[*]")
    pk_field=$(yq r -d$2 $1 "model[${i}].pk")

    field_string=$(${create_fields_url} "${fields}" "${pk_field}")

    # replace newline with carrots in field_string because sed has problem processing \n
    # shouldn't need to do this here, but if there is an error, some newlines could make their way through.
    field_string=${field_string//$'\n'/^}

    # replace fields placeholder in java class with actual fields with ^
    sed -i.bak "s/^    fields/${field_string}/" "${model_path_name}" && rm "${model_path_name}.bak"

    # use tr (translate) command to replace carrot with newline in java file.
    tr ^ '\n' < "${model_path_name}" > "${model_path}/temp.java" && mv "${model_path}/temp.java" "${model_path_name}"

done

# delete placeholder model
rm ${model_path}/class0.java

# get joins
joins=$(yq r -d$2 $1 "joins[*]")
num_joins=$(yq r -d$2 $1 "joins" -l)
echo "joins: ${joins}"
echo "num_joins: ${num_joins}"

#set modelnames to pk mappings
model_names=$(yq r -d$2 $1 "model[*].name")
model_name_arr=(${model_names})
model_pks=$(yq r -d$2 $1 "model[*].pk")
model_pk_arr=(${model_pks})

# create 3 arrays from joins.
declare -a entity0_arr entity2_arr rel1_arr var0a_arr var2a_arr pk0_arr pk2_arr
i=0
while IFS="" read -r p || [ -n "$p" ]
do
    tmp_arr=($p)

    entity0_arr[$i]="${tmp_arr[0]}"
    rel1_arr[$i]="${tmp_arr[1]}"
    entity2_arr[$i]="${tmp_arr[2]}"

    pk0_arr[$i]=$(get_pk_for_model_name "${entity0_arr[$i]}" "${model_name_arr[@]}" "${model_pk_arr[@]}")
    pk2_arr[$i]=$(get_pk_for_model_name "${entity2_arr[$i]}" "${model_name_arr[@]}" "${model_pk_arr[@]}")
    
    var0a_arr[$i]=$(lower_first ${entity0_arr[$i]})
    var2a_arr[$i]=$(lower_first ${entity2_arr[$i]})
    var0a_arr[$i]="${var0a_arr[$i]%Entity}"
    var2a_arr[$i]="${var2a_arr[$i]%Entity}"
    
    ((i++))
done <<< "${joins}"

echo "entity0_arr: ${entity0_arr[@]}"
echo "var0a_arr: ${var0a_arr[@]}"
echo "var2a_arr: ${var2a_arr[@]}"
echo "pk0_arr: ${pk0_arr[@]}"
echo "pk2_arr: ${pk2_arr[@]}"

# ~~~~~

# build annotation string by filling in variables.
declare val0 val1 val2 val3 valpk val1pk val3opk
# $1 ann_var $2 jpa_join_annotation.properties location
get_join_ref_ann () {
    # get annotation from file ()
    join_ref_ann=$(grep "^${1}=" "$2"  | cut -f2- -d'=')

    join_ref_ann="${join_ref_ann//\%1_\%pk/${val1pk}}"
    join_ref_ann="${join_ref_ann//\%3_\%opk/${val3opk}}"
    join_ref_ann="${join_ref_ann//\%0/${val0}}"
    join_ref_ann="${join_ref_ann//\%1/${val1}}"
    join_ref_ann="${join_ref_ann//\%2/${val2}}"
    join_ref_ann="${join_ref_ann//\%3/${val3}}"
    join_ref_ann="${join_ref_ann//\%pk/${valpk}}"

    echo "${join_ref_ann}"

    join_ref_ann=""
}

# write the annotation string to file.
# $1 join_ref_ann, $2 model_path, $3 EntityName
write_join_ann_to_file () {

    model_path_name=${2}/${3}.java
    # remove last close brace from end of file.
    sed -i.bak "s/}$//" "${model_path_name}" && rm "${model_path_name}.bak"

    # append join ref variable with annoation to end of file.
    echo "${1}^^}" >> "${model_path_name}"

    # use tr (translate) command to replace carrot with newline in java file.
    tr ^ '\n' < "${model_path_name}" > "${2}/temp.java" && mv "${2}/temp.java" "${model_path_name}"
}

# for each joins...
for (( i=0; i<${#rel1_arr[@]}; i++ ))
do
    # decipher data in operator

    # Assign a numeric value to each join code to make data extraction easier.
    sum=0
    for (( j=0; j<${#rel1_arr[$i]}; j++ )); do
        ch="${rel1_arr[$i]:$j:1}"
        case "${ch}" in
          "1")  sum=$((1 + ${sum})) ;;
          "n")  if [[ 1 -eq "$j" ]]; then sum=$((2 + ${sum})); else sum=$((4 + ${sum})); fi ;;
          "<")  sum=$((10 + ${sum})) ;;
          ">")  sum=$((100 + ${sum})) ;;
          "-")  ;;
          *) echo "malformed join information. ch:${ch} in:${rel1_arr[$i]}"
            ;;
        esac
    done
    echo "sum for ${rel1_arr[$i]}: ${sum}"

    suml="${sum: -1}"
    # 112 is owner 2
    # 102 is owner 2
    # 12 is owner 0
    # xx3 is owner 0
    # xx5 is owner 2
    # xx6 is owner 2

    # 0 or 2, default to 2
    owner=2
    if [[ 12 -eq "${sum}" || "3" = "${suml}" ]]; then
        owner=0
    fi

    #2: one2one, 5: one2many, 3: many2one, 6: many2many, 0: unset
    relationship=0
    case "${suml}" in
      "2")  relationship="one2one" ;;
      "3")  relationship="many2one" ;;
      "5")  relationship="one2many" ;;
      "6")  relationship="many2many" ;;
    esac

    if [[ 2 = "${owner}" ]]; then
        val0=${entity0_arr[$i]}
        val1=${var0a_arr[$i]}
        val2=${entity2_arr[$i]}
        val3=${var2a_arr[$i]}
        valpk=${pk0_arr[$i]}
        valopk=${pk2_arr[$i]}
    else
        val0=${entity2_arr[$i]}
        val1=${var2a_arr[$i]}
        val2=${entity0_arr[$i]}
        val3=${var0a_arr[$i]}
        valpk=${pk2_arr[$i]}
        valopk=${pk0_arr[$i]}
    fi
    val1pk=$(convert_camel_to_sql_case "${val1}_${valpk}")
    val3opk=$(convert_camel_to_sql_case "${val3}_${valopk}")

    # if first digit is 1, write second entity (2)
    printf -v sum "%03d" $sum
    if [[ "1" = ${sum:0:1} ]]; then
        # build annotation string
        ann_var=""
        if [[ "${suml}" = "3" ]]; then
            ann_var="one2many"
        elif [[ "${suml}" = "5" ]]; then
            ann_var="many2one"
        else
            owner_str="referencing"
            if [[ "2" = "${owner}" ]]; then
                owner_str="owner"
            fi
            ann_var="${relationship}_${owner_str}"
        fi

        # get annotation from file ()
        join_ref_ann=$(get_join_ref_ann "${ann_var}" "${join_prop_url}")

        # write the annotation string to file.
        write_join_ann_to_file "${join_ref_ann}" "${model_path}" "${entity2_arr[$i]}"
    fi

    # if second digit is 1, write first entity (0)
    if [[ "1" = ${sum:1:1} ]]; then
        # build annotation string
        ann_var=""
        if [[ "${suml}" = "3" ]]; then
            ann_var="many2one"
        elif [[ "${suml}" = "5" ]]; then
            ann_var="one2many"
        else
            owner_str="referencing"
            if [[ "0" = "${owner}" ]]; then
                owner_str="owner"
            fi
            ann_var="${relationship}_${owner_str}"
        fi

        # get annotation from file ()
        join_ref_ann=$(get_join_ref_ann "${ann_var}" "${join_prop_url}")

        # write the annotation string to file.
        write_join_ann_to_file "${join_ref_ann}" "${model_path}" "${entity0_arr[$i]}"

    fi
done

# If converter in files, then add that dependency.
grep_result=$(grep "${local_date_converter}\|${local_date_time_converter}" -r $a --include "*.java")
if [[ -n "${grep_result}" ]]
then
	# add dependency gav text to pom
	sed -i.bak -e "/<dependencies>/r ${type_converter_gav_url}" $a/pom.xml && rm "$a/pom.xml.bak"
fi

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

# decipher data in operator

# fill out name variables
# for each join, determine owner and relationship
# build annotation string
# write 1 or 2 annotation strings to 1 or 2 .java files.

# %0:Entity class of referencing Type, located in owning entity.
# %1:referencing type isntance variable, located in owning entity.
# %pk:primary key variable of referencing Type.
# %1_%pk: sql case
# %3_%opk: sql case, the primary key other than the %pk one.
# #2:Entity class of owning Type, located in referencing entity.
# #3:owning type isntance variable, located in referencing entity.





exit 0

#!/bin/bash

# $1: yaml descriptor path

dir=${0%/*}
map_url=${dir}/script_to_archetype_map.properties

# $1 property $2 property_file
get_property () {
	prop=""
    prop=$(grep "^${1}=" "$2"  | cut -f2- -d'=')
	echo "${prop}"
	prop=""
}

# $1 key
prepare_script2arch_map_key () {
	output=""
	output=${1//:/___}
	echo "${output}"
	output=""
}
# for each document in the yaml file
 # call script to generate the maven project (build existing java file url.)

# get number of documents in yaml file
num_yaml_docs=$(yq r -d'*' $1 archetypeGAV | tr -dc '\n' | wc -c | tr -d ' ')

echo "num_yaml_docs: ${num_yaml_docs}"

for (( i=0; i<${num_yaml_docs}; i++ ))
do
    # get first GAV to generate
	archetypeGAV=$(yq r -d${i} $1 archetypeGAV)
	prop_key=$(prepare_script2arch_map_key ${archetypeGAV})
	script=$(get_property ${prop_key} ${map_url})
	
	eval "${dir}/${script} $1 $i"
done

exit 0


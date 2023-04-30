#!/bin/bash

# $1: yaml descriptor path; $2 document number

dir=${0%/*}

source ${dir}/../common_scripts/functions.sh

cp_pl_url=${dir}/../common_scripts/maven-cp.pl
camel_route_choice_url=${dir}/camel_route_choice.properties
gen_impl_class="com.github.mshin.generate.impl.GenerateImplService"
spring_component_ann="@org.springframework.stereotype.Component"
generate_impl_gav="com.github.mshin:generate-impl:0.0.1"

declare -a model_name_arr model_pk_arr

# generate the maven project (build existing java file url.)
# get jaxrs service interface
# make impl file.
  # generate impl class
  # delete existing service bean/impl
  # make new service impl .java file with generated content.
# replace Application.java placeholder for service interface name. (with package)
# update camel route with methods from impl.
# update bean test class names
# update route test class names and bean name.

# call formatter on project.
# build resultant project to verify compilation.

# $1 yaml proj descriptor location; $2 doc num index 0
# $3 g callback $4 a callback $5 sigav callback $6 si callback
generate_maven_rest_service_project () {
    GAV_string=$(yq r -d$2 $1 "archetypeGAV")
    GAV_arr=(${GAV_string//:/ })
    gav_string=$(yq r -d$2 $1 "generatedGav")
    gav_arr=(${gav_string//:/ })
    author=$(yq r -d$2 $1 "author")
    sigav_string=$(yq r -d$2 $1 "serviceInterfaceGav")
    sigav_arr=(${sigav_string//:/ })
    service_interface_string=$(yq r -d$2 $1 "serviceInterface")
    jaxrssi_package=${service_interface_string%.*}
    jaxrssi=${service_interface_string##*.}

    local groupId artifiactId
    groupId=${gav_arr[0]}
    artifiactId=${gav_arr[1]}
    v=${gav_arr[2]}
    p=$groupId.${artifiactId//-/.}

    eval "${3}=${groupId} ${4}=${artifiactId}"
    eval "${5}=${sigav_string} ${6}=${service_interface_string}"

    # handle user not giving a version number
    vv=''
    if [[ -n "$v" ]]; then
      vv="-Dversion=";
    fi

    mvn archetype:generate                          \
      -DarchetypeGroupId="${GAV_arr[0]}"            \
      -DarchetypeArtifactId="${GAV_arr[1]}"         \
      -DarchetypeVersion="${GAV_arr[2]}"            \
      -DgroupId="${groupId}"                        \
      -DartifactId="${artifiactId}"                 \
      -Dpackage="${p}"                              \
      -Dapi_groupId="${sigav_arr[0]}"               \
      -Dapi_artifactId="${sigav_arr[1]}"            \
      -Dapi_version="${sigav_arr[2]}"               \
      -Djaxrs_service_interface="${jaxrssi}"        \
      -Djaxrs_service_package="${jaxrssi_package}"  \
      -Dauthor="$author"                            \
      -B                                            \
      $vv$v
}

declare g a sigav si
generate_maven_rest_service_project $1 $2 g a sigav si

class_file_path=${a}/src/main/java/${g//./\/}/${a//-/\/}

# generate impl class
# delete existing service bean/impl
# make new service impl .java file with generated content.

si_classpath=$(${cp_pl_url} ${sigav})
generate_impl_classpath=$(${cp_pl_url} ${generate_impl_gav})

generated_impl=$(java -cp ${si_classpath}:${generate_impl_classpath} ${gen_impl_class} "${si}" "${g}.${a//-/.}")

# Overwrite content of service bean impl with new content.
impl_path=${class_file_path}/${si##*.}Bean.java

echo "${generated_impl}" > ${impl_path}

# Write "@org.springframework.stereotype.Component\n" before "public class"
annotation="${spring_component_ann}^public class"
sed -i.bak "s/^public class/${annotation}/" "${impl_path}" && rm "${impl_path}.bak"
# use tr (translate) command to replace carrot with newline in java file.
tr ^ '\n' < "${impl_path}" > "${class_file_path}/temp.java" && mv "${class_file_path}/temp.java" "${impl_path}"

# update Routes class with interface methods
route_path=${class_file_path}/${si##*.}Routes.java

# create string to add to routes file
declare -a si_methods_arr

#get methods
si_methods="$(grep -o -e "\s\w*\s*(" ${impl_path})"
#strip '(' from matched pattern; can't do lookforward/behind in mac grep (-P required)
si_methods=$(echo ${si_methods} | tr -d '(')

si_methods_arr=(${si_methods})

# build .when() string
when_string=$(grep "^when=" "${camel_route_choice_url}"  | cut -f2- -d'=')

# for each method, append a new when string, replacing %0 placeholder with method name.
declare route_string
for sim in "${si_methods_arr[@]}"
do
	route_string="${route_string}${when_string//\%/${sim}}"
done

# remove existing route choice options
# start pattern
sp=".choice()"
# end pattern
ep=";"
sed -i.bak "/${sp}/,/${ep}/{/${sp}/!{/${ep}/!d;};}" "${route_path}" && rm "${route_path}.bak"

#insert new when statements after .choice(), then replace '^' with \n.
sed -i.bak "s/${sp}/${sp}^${route_string}/" "${route_path}" && rm "${route_path}.bak"

# use tr (translate) command to replace carrot with newline in java file.
tr ^ '\n' < "${route_path}" > "${class_file_path}/temp.java" && mv "${class_file_path}/temp.java" "${route_path}"

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
beautify_imports "$a" "${class_file_path}"

mvn clean install -f $a/pom.xml

exit 0

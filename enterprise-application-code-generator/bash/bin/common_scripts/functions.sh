#!/bin/bash

# $1=camelcase variable
convert_camel_to_sql_case () {
    # convert camel to snake case
    sql_case=$(sed -E "s/([A-Z]+)/_\1/g" <<< "${1}")
    # set all lowercase to uppercase
    sql_case=$(tr '[:lower:]' '[:upper:]' <<< "${sql_case}")
    # remove any leading underscores
    sql_case=${sql_case#_}
    echo "${sql_case}"
    sql_case=""
}

# $1 string that you want to make the first letter lowercase
lower_first () {
    output=""
    output=$(echo ${1:0:1} | tr '[A-Z]' '[a-z]')${1:1}
    echo "${output}"
    output=""
}

# $1 yaml proj descriptor location; $2 doc num index 0; $3 g callback $4 a callback
generate_maven_project () {
    GAV_string=$(yq r -d$2 $1 "archetypeGAV")
    GAV_arr=(${GAV_string//:/ })
    gav_string=$(yq r -d$2 $1 "generatedGav")
    gav_arr=(${gav_string//:/ })
    author=$(yq r -d$2 $1 "author")

    local groupId artifiactId
    groupId=${gav_arr[0]}
    artifiactId=${gav_arr[1]}
    v=${gav_arr[2]}
    p=$groupId.${artifiactId//-/.}

    eval "${3}=${groupId} ${4}=${artifiactId}"

    # handle user not giving a version number
    vv=''
    if [[ -n "$v" ]]; then
      vv="-Dversion=";
    fi

    mvn archetype:generate                     \
      -DarchetypeGroupId="${GAV_arr[0]}"       \
      -DarchetypeArtifactId="${GAV_arr[1]}"    \
      -DarchetypeVersion="${GAV_arr[2]}"       \
      -DgroupId="${groupId}"                   \
      -DartifactId="${artifiactId}"            \
      -Dpackage="$groupId.${artifiactId//-/.}" \
      -Dclass0="class0"                        \
      -Dclass1="class1"                        \
      -Dfields="fields"                        \
      -Denumerations="enumerations"            \
      -Dauthor="$author"                       \
      -B                                       \
      $vv$v
}

# $1 artifactId (a), $2 class file path (${class_file_path})
beautify_imports () {
    # call formatter on project
    mvn org.andromda.maven.plugins:andromda-beautifier-plugin:beautify-imports -f $1/pom.xml

    # need to clean \r from all java files due to andromda beautifier.

    # get all java files in project beautified.
    java_files_arr=($(find $1 -name '*.java'))

    for file in "${java_files_arr[@]}"
    do
        # remove \r to be consistent with rest of files
        # copying to java source dir even for classes not there because we know we have write privileges there.
        tr -d '\r' < "${file}" > "$2/temp.java" && mv "$2/temp.java" "${file}"
    done
}

# $1 gav $2 pom location
add_dependency () {
    local gid aid ver

    gav_arr=(${1//:/ })
    gid=${gav_arr[0]}
    aid=${gav_arr[1]}
    ver=${gav_arr[2]}
    xmlstarlet ed -L -N x=http://maven.apache.org/POM/4.0.0 \
    -s /x:project/x:dependencies -t elem -n dependency -v "" \
    -s "/x:project/x:dependencies/dependency[last()]" -t elem -n groupId -v "$gid" \
    -s "/x:project/x:dependencies/dependency[last()]" -t elem -n artifactId -v "$aid" \
    -s "/x:project/x:dependencies/dependency[last()]" -t elem -n version -v "$ver" \
    "$2"
}

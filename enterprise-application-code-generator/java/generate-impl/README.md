# generate-impl

`java -cp ${classpath_for_jar_containing_interface_classfile}:${classpath_for_generate-impl_jar} com.github.mshin.generate.impl.GenerateImplService "${interface_classname}" "${new_impl_package}"`


You can use the script in bin/maven-cp.pl to help build the classpaths for the different jars. Pass the Maven GAV to the script to get the classpath string.
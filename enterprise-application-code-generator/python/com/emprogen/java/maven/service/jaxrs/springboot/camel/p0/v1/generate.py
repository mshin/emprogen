#!/usr/local/bin/python3

import com.emprogen.java.maven.functions as jmf
import com.emprogen.java.maven.yaml_functions as yf
import com.emprogen.java.maven.field_functions as ff
from com.emprogen.java.maven.models import Gav

def generate(domainModelDescriptor: 'dict', archetypeGav: 'Gav' = Gav('com.github.mshin', 'jaxrms-springboot-camel-archetype', '1.0.1')) -> None:
#def generate(domainModelDescriptor: 'dict', archetypeGav: 'Gav' = Gav('com.emprogen', 'service-jaxrs-springboot-camel-p0-archetype', '0.0.1')) -> None:


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


    # Do all 1 time loads and calculations up front.
    # define archetype Gav used for this generator within script.
    archGav = archetypeGav
    # yf.getArchetypeGav(domainModelDescriptor)
    projGav = yf.getGeneratedProjectGav(domainModelDescriptor)
    projPomPath = projGav.artifactId + '/pom.xml'
    modelPath = jmf.getModelPath(projGav)
    beanTemplateFile = modelPath + '/__jaxrs_service_interface__Bean.java'
    routesTemplateFile = modelPath + '/__jaxrs_service_interface__Routes.java'
    applicationTemplateFile =  modelPath + '/Application.java'
    typToPkgtyp = ff.getTypeToPkgtypeDict(str(jmf.getFilePath(__file__)) + '/../../../../../java_type.properties')
    # Geneate Maven project.
    jmf.generateMavenProject(archGav, projGav, domainModelDescriptor['author'])
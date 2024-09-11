package ${package};

import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import ${jaxrs_service_package}.${jaxrs_service_interface};

/**
 * @author ${author}
 */
@ApplicationScoped
public class ${jaxrs_service_interface}Impl implements ${jaxrs_service_interface} {

    public static final Logger LOGGER = LoggerFactory.getLogger(${jaxrs_service_interface}Impl.class.getName());

    @Inject
    ${jaxrs_service_interface}Service service;

}
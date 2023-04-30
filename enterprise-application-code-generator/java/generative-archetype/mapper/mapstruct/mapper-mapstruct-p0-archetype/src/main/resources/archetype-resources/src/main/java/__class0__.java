package ${package};

import java.io.Serializable;

import org.mapstruct.Mapper;
import org.mapstruct.Mapping;
import org.mapstruct.Mappings;
import org.mapstruct.ValueMapping;
import org.mapstruct.ValueMappings;
import org.mapstruct.factory.Mappers;

/*
 * I think fields with the same name and type will be mapped automatically
 * Use the annotations below to map fields that do not have the same name.
 *    @Mappings( { 
 *        @Mapping( source = "fromObjectValue", target = "toObjectValue" ), 
 *        @Mapping( source =  "homeAddressStreet", target = "contactInfo.address.street")} )
 *     ToObject map( FromObject fromObject );
*/
/**
 * @author ${author}
 */
@Mapper
public interface ${class0} {

    //map()

}

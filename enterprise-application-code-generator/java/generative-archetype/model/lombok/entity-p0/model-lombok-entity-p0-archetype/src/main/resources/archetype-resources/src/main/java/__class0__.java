package ${package};

import javax.persistence.Entity;
import javax.persistence.Table;

import lombok.NoArgsConstructor;
import lombok.Data;

/**
 * 
 * For lazy initialized fields, exclude from the toString.
 * @ToString.Exclude @Getter(lazy = true)
 * 
 * Do not add generated id to hashCode. https://hibernate.atlassian.net/browse/HHH-3799
 * @Id @lombok.EqualsAndHashCode.Exclude
 * 
 * 
 * 
 * @author ${author}
 */
@Data
@NoArgsConstructor
@Entity
@Table( name = "entity_name" )
public class ${class0} {

    ${fields}

}

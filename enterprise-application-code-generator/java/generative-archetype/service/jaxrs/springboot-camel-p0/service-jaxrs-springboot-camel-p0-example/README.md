#### Build
Change directory `cd` to where the project pom.xml is. run:

`mvn clean install`

#### Run locally

`java -jar ${PATH_TO_JAR}`

example: `java -jar target/jaxrms-springboot-camel-rs.jar`

**OR**
  
`cd` to dir where the project pom.xml is. run:

`mvn spring-boot:run`

#### Service locations

<http://localhost:8080/services/info>
*Service information*
  
<http://localhost:8080/services/swagger.json>
*API swagger information in JSON format.*
  
<http://localhost:8080/services/api-docs?url=/services/swagger.json>
*Swagger UI format for API method descriptions. Can also test methods here.*

<http://localhost:8080/services/swagger.yaml>
*Download Swagger in YAML format.*

<http://localhost:8080/services/ping>
*Example of a standard HTTP GET API method call.*

Other service endpoints will have the root URL of <http://localhost:8080/services/> and the URL will be appended to that. Check the JAX-RS interface for API method specific URL details.
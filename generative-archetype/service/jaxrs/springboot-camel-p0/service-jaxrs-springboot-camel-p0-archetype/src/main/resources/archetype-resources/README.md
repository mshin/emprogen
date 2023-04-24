#### Build
Change directory `cd` to where the project pom.xml is. run:

`mvn clean install`

#### Run locally

`java -jar ${PATH_TO_JAR}`

example: `java -jar target/${artifactId}.jar`

**OR**
  
`cd` to dir where the project pom.xml is. run:

`mvn spring-boot:run`

#### Service locations

Other service endpoints will have the root URL of <http://localhost:8080/services/> and the URL will be appended to that. Check the JAX-RS interface for API method specific URL details.
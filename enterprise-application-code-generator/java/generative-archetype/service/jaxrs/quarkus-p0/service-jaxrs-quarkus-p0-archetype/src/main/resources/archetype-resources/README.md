#### Build
Change directory `cd` to where the project pom.xml is. run:

## Compilation
Change directory `cd` to where the project pom.xml is.

To build with tests:
```
mvn clean install
```

To build without tests:
```
mvn clean install -DskipTests
```

## Local Deployment
To run the app in dev mode:
```
mvn quarkus:dev
```

When running the application locally, you can test the application at the following urls:
```
http://localhost:8080/q/
http://localhost:8080/q/dev/
http://localhost:8080/q/swagger-ui/
```

## Configuration Changes: Application Properties
To change the application configuration for various deployment environments, modify the properties file located at `notification-rs/src/main/resources/application.properties`.
# Technical Stack and Dependencies

## Core Technology Foundation

Apache OFBiz is built on a robust Java-based technology stack that emphasizes enterprise-grade scalability, modularity, and standards compliance. The framework leverages a carefully curated set of dependencies that work together to provide a comprehensive business application platform.

### Java Platform Requirements

OFBiz requires **Java 8 or higher** as its runtime environment, with full support for Java 11 and Java 17 LTS versions. The framework takes advantage of modern Java features while maintaining backward compatibility:

```xml
<properties>
    <maven.compiler.source>1.8</maven.compiler.source>
    <maven.compiler.target>1.8</maven.compiler.target>
    <java.version>1.8</java.version>
</properties>
```

The codebase extensively uses Java generics, annotations, and concurrent programming constructs to ensure type safety and performance optimization across the framework's service-oriented architecture.

### Build System and Dependency Management

OFBiz utilizes **Apache Gradle** as its primary build system, moving away from the legacy Ant-based approach. The build configuration is centralized in `build.gradle` files distributed across component modules:

```gradle
dependencies {
    implementation 'org.apache.tomcat:tomcat-catalina:9.0.65'
    implementation 'org.freemarker:freemarker:2.3.31'
    implementation 'org.apache.commons:commons-lang3:3.12.0'
    testImplementation 'junit:junit:4.13.2'
}
```

The modular dependency structure allows individual components to declare their specific requirements while maintaining consistency across the entire framework through version catalogs and dependency constraints.

### Web Container and Servlet Engine

The framework embeds **Apache Tomcat 9.x** as its servlet container, providing a lightweight yet powerful web server capability. OFBiz includes custom Tomcat configurations optimized for its multi-tenant architecture:

```xml
<!-- framework/catalina/ofbiz-component.xml -->
<ofbiz-component name="catalina">
    <webapp name="ROOT" server="default-server" 
            location="webapp/ROOT" mount-point="/" />
</ofbiz-component>
```

The embedded Tomcat instance is configured with custom connectors, security realms, and clustering support for production deployments. The integration allows OFBiz to handle multiple virtual hosts and applications within a single JVM instance.

### Template Engine and View Layer

**Apache FreeMarker 2.3.x** serves as the primary template engine for rendering dynamic content. OFBiz extends FreeMarker with custom directives and transforms specific to business application needs:

```ftl
<#-- Custom OFBiz FreeMarker transforms -->
<@ofbizUrl>EditProduct?productId=${productId}</@ofbizUrl>
<@ofbizCurrency amount=price isoCode=currencyCode/>
```

The framework includes specialized FreeMarker transforms for URL generation, internationalization, currency formatting, and security context handling, all integrated with the entity engine and service framework.

### Database Abstraction and ORM

OFBiz implements a custom **Entity Engine** that provides database abstraction without traditional ORM overhead. The system supports multiple database backends through JDBC:

- **Apache Derby** (embedded, development)
- **PostgreSQL** (recommended production)
- **MySQL/MariaDB**
- **Oracle Database**
- **Microsoft SQL Server**

```xml
<!-- framework/entity/config/entityengine.xml -->
<datasource name="localpostgres" helper-name="postgres"
            field-type-name="postgres" check-on-start="true"
            add-missing-on-start="true" use-pk-constraint-names="false">
    <read-data reader-name="tenant"/>
    <read-data reader-name="seed"/>
    <read-data reader-name="demo"/>
</datasource>
```

The Entity Engine generates optimized SQL queries and provides caching mechanisms that significantly outperform traditional ORM solutions in high-transaction environments.

### Service Framework and Transaction Management

The **Service Engine** implements a comprehensive service-oriented architecture with built-in transaction management, security, and distributed computing capabilities:

```xml
<service name="createProduct" engine="entity-auto" invoke="create" auth="true">
    <description>Create a Product</description>
    <permission-service service-name="genericContentPermission" main-action="CREATE"/>
    <auto-attributes include="pk" mode="INOUT" optional="true"/>
    <auto-attributes include="nonpk" mode="IN" optional="true"/>
</service>
```

Services can be invoked synchronously, asynchronously, or scheduled for later execution. The framework includes built-in support for distributed transactions across multiple databases and external systems.

### Security and Authentication Framework

OFBiz integrates **Apache Shiro** for authentication and authorization, enhanced with custom security implementations:

- LDAP/Active Directory integration
- OAuth 2.0 and OpenID Connect support
- Multi-factor authentication
- Role-based access control (RBAC)
- Data-level security policies

### Caching and Performance

The framework employs **Ehcache** for distributed caching with custom cache regions optimized for entity data, service results, and rendered content:

```xml
<cache name="entity.default" maxElementsInMemory="1000" 
       eternal="false" timeToIdleSeconds="3600" 
       timeToLiveSeconds="7200" overflowToDisk="false"/>
```

### Integration and Communication

OFBiz includes comprehensive integration capabilities through:

- **Apache HttpClient** for REST API consumption
- **Apache Axis2** for SOAP web services
- **Apache Camel** for enterprise integration patterns
- **JMS** providers for asynchronous messaging

### Development and Testing Dependencies

The development environment includes:

- **JUnit 4.x** for unit testing
- **Mockito** for mocking frameworks
- **Selenium WebDriver** for integration testing
- **Apache JMeter** integration for performance testing

This technology stack provides OFBiz with enterprise-grade capabilities while maintaining the flexibility to adapt to diverse business requirements and deployment scenarios.

## Subsections

- [Core Technologies](./Core Technologies.md)
- [Database Support](./Database Support.md)
- [Web Framework Components](./Web Framework Components.md)

## Repository Context

- **Repository**: [https://github.com/apache/ofbiz-framework](https://github.com/apache/ofbiz-framework)
- **Description**: No description available
- **Business Domain**: Software Development
- **Architecture Pattern**: Library/Utility

## Technology Stack

## Related Documentation

This section is part of a comprehensive documentation structure. Related sections include:

- **Core Technologies**: Detailed coverage of core technologies
- **Database Support**: Detailed coverage of database support
- **Web Framework Components**: Detailed coverage of web framework components

---

*Generated by ADocS (Automated Documentation Structure) on 2025-09-05 23:38:42*

*For the most up-to-date information, visit the [original repository](https://github.com/apache/ofbiz-framework)*
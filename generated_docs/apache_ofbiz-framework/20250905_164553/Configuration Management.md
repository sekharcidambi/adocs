## Configuration Management

## Overview

Apache OFBiz employs a comprehensive configuration management system that enables flexible deployment across diverse enterprise environments. The framework's configuration architecture supports multi-tenant deployments, environment-specific settings, and runtime configuration changes without requiring system restarts in most cases. This system is built around XML-based configuration files, property files, and database-driven configuration tables that work together to provide a robust enterprise-grade configuration management solution.

## Configuration Architecture

### Core Configuration Components

The OFBiz configuration system is structured around several key components that integrate seamlessly with the multi-tier architecture:

**Framework Configuration Layer**
- `framework/start/src/main/java/org/apache/ofbiz/base/start/` - Bootstrap configuration
- `framework/base/config/` - Core framework properties and XML configurations
- `framework/entity/config/` - Entity engine and database configurations
- `framework/service/config/` - Service engine configuration files

**Application Configuration Layer**
- `applications/*/config/` - Application-specific configurations
- `specialpurpose/*/config/` - Specialized module configurations
- Component-level `ofbiz-component.xml` files for modular configuration

### Configuration File Hierarchy

OFBiz follows a hierarchical configuration loading pattern that allows for environment-specific overrides:

```
1. Default framework configurations
2. Component-specific configurations  
3. Environment-specific overrides
4. Runtime database configurations
5. JVM system properties (highest priority)
```

## Key Configuration Files

### Entity Engine Configuration

The `entityengine.xml` file serves as the primary database configuration hub:

```xml
<entity-config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
               xsi:noNamespaceSchemaLocation="http://ofbiz.apache.org/dtds/entity-config.xsd">
    
    <resource-loader name="fieldfile" class="org.apache.ofbiz.base.config.FileLoader"
                     prepend-env="ofbiz.home" prefix="/framework/entity/fieldtype/"/>
    
    <datasource name="localderby"
                helper-class="org.apache.ofbiz.entity.datasource.GenericHelperDAO"
                field-type-name="derby"
                check-on-start="true"
                add-missing-on-start="true"
                use-pk-constraint-names="false">
        <read-data reader-name="tenant"/>
        <read-data reader-name="seed"/>
        <read-data reader-name="seed-initial"/>
        <read-data reader-name="demo"/>
        <read-data reader-name="ext"/>
    </datasource>
</entity-config>
```

### Service Engine Configuration

Service definitions and configurations are managed through `serviceengine.xml`:

```xml
<service-config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                xsi:noNamespaceSchemaLocation="http://ofbiz.apache.org/dtds/service-config.xsd">
    
    <service-engine name="default">
        <thread-pool send-to-pool="pool"
                     purge-job-days="4"
                     failed-retry-min="3"
                     ttl="120000"
                     jobs="100"
                     min-threads="5"
                     max-threads="15"
                     poll-enabled="true"
                     poll-db-millis="30000">
            <run-from-pool name="pool"/>
        </thread-pool>
    </service-engine>
</service-config>
```

### Component Configuration

Each OFBiz component includes an `ofbiz-component.xml` file that defines its integration points:

```xml
<ofbiz-component name="accounting"
                 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                 xsi:noNamespaceSchemaLocation="http://ofbiz.apache.org/dtds/ofbiz-component.xsd">
    
    <resource-loader name="main" type="component"/>
    
    <classpath type="jar" location="build/lib/*"/>
    <classpath type="dir" location="config"/>
    
    <entity-resource type="model" reader-name="main" loader="main" location="entitydef/entitymodel.xml"/>
    <entity-resource type="data" reader-name="seed" loader="main" location="data/AccountingTypeData.xml"/>
    
    <service-resource type="model" loader="main" location="servicedef/services.xml"/>
    
    <webapp name="accounting"
            title="Accounting"
            server="default-server"
            location="webapp/accounting"
            base-permission="OFBTOOLS,ACCOUNTING"
            mount-point="/accounting"/>
</ofbiz-component>
```

## Environment-Specific Configuration

### Property File Management

OFBiz supports environment-specific property files through a cascading system:

```bash
# Development environment
framework/base/config/general.properties

# Production overrides
runtime/properties/general.properties

# System-specific overrides
config/general.properties
```

Example property configuration for database connections:

```properties
# Database configuration
entityengine.datasource.default=localpostgres
datasource.localpostgres.uri=jdbc:postgresql://localhost:5432/ofbiz
datasource.localpostgres.driver-class-name=org.postgresql.Driver
datasource.localpostgres.username=${OFBIZ_DB_USER:ofbiz}
datasource.localpostgres.password=${OFBIZ_DB_PASSWORD:ofbiz}
datasource.localpostgres.pool.maxsize=250
datasource.localpostgres.pool.minsize=5
```

### Docker Configuration Integration

For containerized deployments, OFBiz configuration integrates with Docker environment variables:

```dockerfile
ENV OFBIZ_DB_HOST=postgres
ENV OFBIZ_DB_NAME=ofbiz
ENV OFBIZ_DB_USER=ofbiz
ENV OFBIZ_DB_PASSWORD=ofbiz123
ENV JAVA_OPTS="-Xms2048M -Xmx2048M"
```

## Runtime Configuration Management

### Database-Driven Configuration

OFBiz stores runtime configuration in several key entities:

- **SystemProperty** - System-wide configuration parameters
- **PartyContent** - Party-specific configuration content
- **ProductStoreEmailSetting** - Store-specific email configurations
- **WebSiteProperties** - Website-specific properties

### Configuration APIs

The framework provides programmatic access to configuration through service interfaces:

```java
// Accessing system properties
String configValue = EntityUtilProperties.getPropertyValue("general", 
    "currency.uom.id.default", "USD", delegator);

// Runtime property updates
Map<String, Object> context = UtilMisc.toMap(
    "systemResourceId", "general",
    "systemPropertyId", "default.locale",
    "systemPropertyValue", "en_US"
);
dispatcher.runSync("createSystemProperty", context);
```

## Multi-Tenant Configuration

OFBiz supports multi-tenant deployments through tenant-specific configuration:

```xml
<tenant tenant-id="DEMO1" tenant-name="Demo Tenant 1">
    <datasource name="localderby1" 
                helper-class="org.apache.ofbiz.entity.datasource.GenericHelperDAO"
                schema-name="DEMO1"/>
</tenant>
```

## Best Practices

### Configuration Security
- Store sensitive configurations in environment variables or encrypted property files
- Use the built-in encryption utilities for database passwords
- Implement proper access controls for configuration management screens

### Performance Optimization
- Cache frequently accessed configuration values using the UtilCache framework
- Minimize database queries for configuration lookups through proper caching strategies
- Use connection pooling configurations appropriate for your deployment scale

### Deployment Management
- Maintain environment-specific configuration branches in version control
- Use configuration validation services to ensure consistency across environments
- Implement automated configuration deployment through CI/CD pipelines with Maven and Jenkins integration

This configuration management system provides the flexibility needed for enterprise ERP deployments while maintaining the consistency and reliability required for mission-critical business operations.

## Repository Context

- **Repository**: [https://github.com/apache/ofbiz-framework](https://github.com/apache/ofbiz-framework)
- **Description**: Apache OFBiz is an open source enterprise resource planning (ERP) system
- **Business Domain**: Enterprise Resource Planning
- **Architecture Pattern**: Multi-tier Architecture
- **Key Components**: Presentation Layer, Business Logic Layer, Data Access Layer
- **Stars**: 1200
- **Forks**: 800
- **Size**: 50000 KB

## Technology Stack

### Languages
- Java
- Groovy
- JavaScript

### Frameworks
- Apache OFBiz Framework
- Spring
- Hibernate

### Databases
- MySQL
- PostgreSQL
- Derby

### Frontend
- React
- Angular
- Vue.js

### Devops
- Docker
- Jenkins
- Maven

## Quick Setup

```bash
git clone https://github.com/apache/ofbiz-framework.git
cd ofbiz-framework
./gradlew build
./gradlew ofbiz
```

---

*Generated by ADocS (Automated Documentation Structure) on 2025-09-05 17:08:26*

*For the most up-to-date information, visit the [original repository](https://github.com/apache/ofbiz-framework)*
## Running OFBiz Applications

## Overview

Apache OFBiz (Open For Business) is a comprehensive enterprise resource planning (ERP) framework built on Java that provides a complete suite of business applications. Running OFBiz applications involves understanding the framework's multi-tenant architecture, component-based structure, and various deployment options. This section covers the essential aspects of launching, configuring, and managing OFBiz applications in different environments.

## Prerequisites and System Requirements

Before running OFBiz applications, ensure your system meets the following requirements:

- **Java Development Kit (JDK)**: Java 8 or higher (OpenJDK or Oracle JDK)
- **Memory**: Minimum 2GB RAM, recommended 4GB or more
- **Database**: Derby (embedded, default), PostgreSQL, MySQL, or other supported databases
- **Operating System**: Linux, Windows, or macOS

Verify your Java installation:

```bash
java -version
javac -version
```

## Initial Setup and Build Process

### Building OFBiz

OFBiz uses Gradle as its build system. The framework includes a Gradle wrapper that automatically downloads the correct Gradle version:

```bash
# On Linux/macOS
./gradlew build

# On Windows
gradlew.bat build
```

This command compiles all components, runs tests, and prepares the application for execution. The build process handles:

- Component compilation and dependency resolution
- Entity model generation and validation
- Service definition processing
- Web application packaging

### Loading Initial Data

OFBiz requires seed data to function properly. Load the essential datasets:

```bash
# Load seed data (required for basic functionality)
./gradlew loadDefault

# Load demo data (optional, for testing and development)
./gradlew loadDemo

# Load specific data types
./gradlew "loadData --load-file=framework/security/data/SecurityData.xml"
```

The data loading process populates:
- Entity definitions and relationships
- Security permissions and roles
- Basic configuration parameters
- Optional demonstration data

## Starting OFBiz Applications

### Standard Startup

Launch OFBiz using the Gradle wrapper:

```bash
# Start with default configuration
./gradlew ofbiz

# Start with specific arguments
./gradlew "ofbiz --start"

# Start in background mode
./gradlew "ofbiz --start --portoffset=10000"
```

### Advanced Startup Options

OFBiz provides numerous startup parameters for different scenarios:

```bash
# Start with custom JVM options
./gradlew "ofbiz --start" -Dfile.encoding=UTF-8 -Xms1024M -Xmx2048M

# Start with specific component loading
./gradlew "ofbiz --start --load-component=order,party,accounting"

# Start with database configuration
./gradlew "ofbiz --start --database=postgresql"

# Debug mode startup
./gradlew "ofbiz --start --debug"
```

### Container-Based Architecture

OFBiz applications run within specialized containers that manage different aspects of the framework:

- **Catalina Container**: Handles web applications and HTTP requests
- **RMI Container**: Manages remote method invocation services
- **Service Container**: Executes business logic services
- **Entity Container**: Manages database connections and ORM operations

Monitor container status:

```bash
# Check running containers
./gradlew "ofbiz --status"

# Shutdown gracefully
./gradlew "ofbiz --shutdown"
```

## Configuration Management

### Framework Configuration

The primary configuration files control various aspects of OFBiz execution:

**framework/start/src/main/java/org/apache/ofbiz/base/start/StartupControlPanel.java**
- Manages startup sequence and container initialization
- Handles command-line argument processing

**framework/base/config/ofbiz-containers.xml**
```xml
<container name="catalina-container" 
           class="org.apache.ofbiz.catalina.container.CatalinaContainer">
    <property name="config-file" value="framework/catalina/config/catalina-containers.xml"/>
    <property name="apps-context-reloadable" value="false"/>
    <property name="apps-cross-context" value="false"/>
</container>
```

### Database Configuration

Configure database connections in **framework/entity/config/entityengine.xml**:

```xml
<datasource name="localderby"
            helper-class="org.apache.ofbiz.entity.datasource.GenericHelperDAO"
            schema-name="OFBIZ"
            field-type-name="derby"
            check-on-start="true"
            add-missing-on-start="true"
            use-pk-constraint-names="false">
    <read-data reader-name="tenant"/>
    <read-data reader-name="seed"/>
    <read-data reader-name="demo"/>
</datasource>
```

## Multi-Tenant Operations

OFBiz supports multi-tenant architecture, allowing multiple isolated business instances:

### Tenant Management

```bash
# Create new tenant
./gradlew "ofbiz --load-tenant --tenant-id=DEMO_TENANT --tenant-name='Demo Company'"

# Load tenant-specific data
./gradlew "loadData --load-file=applications/party/data/DemoPartyData.xml --delegator=default#DEMO_TENANT"

# Start with specific tenant
./gradlew "ofbiz --start --tenant-id=DEMO_TENANT"
```

### Tenant Configuration

Each tenant maintains separate:
- Database schemas or connections
- Security configurations
- Business data isolation
- Custom component configurations

## Application Access and Verification

### Web Application Access

Once started, OFBiz applications are accessible through various web interfaces:

- **eCommerce Store**: `https://localhost:8443/ecommerce/`
- **Backend Applications**: `https://localhost:8443/webtools/`
- **Accounting**: `https://localhost:8443/accounting/`
- **Manufacturing**: `https://localhost:8443/manufacturing/`
- **Human Resources**: `https://localhost:8443/humanres/`

Default credentials:
- Username: `admin`
- Password: `ofbiz`

### Health Checks and Monitoring

Verify application health:

```bash
# Check system status
curl -k https://localhost:8443/webtools/control/main

# Monitor log files
tail -f runtime/logs/ofbiz.log

# Database connectivity test
./gradlew "ofbiz --test-list --test-case=entity"
```

## Performance Optimization

### JVM Tuning

Optimize JVM parameters for production environments:

```bash
export JAVA_OPTS="-server -Xms2048M -Xmx4096M -XX:MaxMetaspaceSize=512M 
                  -XX:+UseG1GC -XX:+UseStringDeduplication 
                  -Dfile.encoding=UTF-8"
./gradlew ofbiz
```

### Component Loading Optimization

Selectively load components to reduce startup time and memory usage:

```bash
# Load only essential components
./gradlew "ofbiz --start --load-component=base,entity,security,service,webapp"

# Exclude specific components
./gradlew "ofbiz --start --exclude-component=example,ebay,googlebase"
```

## Troubleshooting Common Issues

### Port Conflicts

If default ports are occupied, use port offset:

```bash
./gradlew "ofbiz --start --portoffset=1000"
# HTTP: 8080 -> 9080, HTTPS: 8443 -> 9443
```

### Memory Issues

Monitor and adjust memory allocation:

```bash
# Increase heap size
./gradlew ofbiz -Xmx8192M

# Enable memory debugging
./gradlew ofbiz -XX:+PrintGCDetails -XX:+PrintGCTimeStamps
```

### Database Connection Problems

Verify database configuration and connectivity:

```bash
# Test database connection
./gradlew "ofbiz --test-list --test-case=entity-query"

# Reset database (development only)
./gradlew cleanAll loadDefault
```

This comprehensive approach to running OFBiz applications ensures proper initialization, configuration, and operation of the enterprise framework across various deployment scenarios.

## Repository Context

- **Repository**: [https://github.com/apache/ofbiz-framework](https://github.com/apache/ofbiz-framework)
- **Description**: No description available
- **Business Domain**: Software Development
- **Architecture Pattern**: Library/Utility

## Technology Stack

---

*Generated by ADocS (Automated Documentation Structure) on 2025-09-06 22:46:03*

*For the most up-to-date information, visit the [original repository](https://github.com/apache/ofbiz-framework)*
## Running Your First Application

## Overview

Apache OFBiz (Open For Business) is a comprehensive enterprise resource planning (ERP) and customer relationship management (CRM) framework built on Java. Running your first application in OFBiz involves understanding its component-based architecture, service-oriented design, and web application deployment model. This section guides you through the essential steps to get your first OFBiz application up and running, from initial setup to accessing the various business applications included in the framework.

## Prerequisites and Environment Setup

Before running your first OFBiz application, ensure your development environment meets the following requirements:

### System Requirements

- **Java Development Kit (JDK)**: Java 8 or higher (OpenJDK recommended)
- **Memory**: Minimum 2GB RAM, 4GB recommended for development
- **Disk Space**: At least 2GB free space for the framework and data
- **Operating System**: Linux, Windows, or macOS

### Environment Configuration

Verify your Java installation and set the appropriate environment variables:

```bash
# Check Java version
java -version
javac -version

# Set JAVA_HOME (Linux/macOS example)
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH
```

## Building and Starting OFBiz

### Initial Build Process

OFBiz uses Gradle as its build system. The framework follows a component-based architecture where each business domain (accounting, manufacturing, ecommerce, etc.) is organized as separate components with their own entities, services, and web applications.

```bash
# Navigate to the OFBiz root directory
cd ofbiz-framework

# Load initial data and build the system
./gradlew loadDefault

# Alternative: Load only seed data (minimal dataset)
./gradlew loadSeed
```

The `loadDefault` task performs several critical operations:
- Compiles all Java source code across components
- Generates entity definitions from XML schema files
- Loads seed data (essential system data)
- Loads demo data (sample business data for testing)
- Initializes the embedded Derby database

### Starting the Application Server

OFBiz includes an embedded Apache Tomcat server managed through Gradle tasks:

```bash
# Start OFBiz server
./gradlew ofbiz

# Start with specific JVM options
./gradlew ofbiz -Dargs="-Xms1024M -Xmx2048M"

# Start in background mode
./gradlew ofbizBackground
```

The startup process initializes:
- **Container Framework**: Manages component lifecycle and dependency injection
- **Entity Engine**: ORM layer handling database operations
- **Service Engine**: SOA framework for business logic execution
- **Web Framework**: MVC framework for web application rendering

## Accessing Core Applications

Once OFBiz is running (typically on port 8080), you can access various business applications through different web contexts:

### Web Store (eCommerce)
```
URL: https://localhost:8443/ecommerce/
Purpose: B2C eCommerce storefront
Key Features: Product catalog, shopping cart, customer registration
```

### Accounting Manager
```
URL: https://localhost:8443/accounting/
Login: admin/ofbiz
Purpose: Financial management and accounting operations
Key Features: GL accounts, invoicing, payments, financial reports
```

### Manufacturing Manager
```
URL: https://localhost:8443/manufacturing/
Login: admin/ofbiz
Purpose: Production planning and manufacturing execution
Key Features: Bill of materials, work orders, inventory management
```

### Party Manager
```
URL: https://localhost:8443/partymgr/
Login: admin/ofbiz
Purpose: Customer and supplier relationship management
Key Features: Contact management, organizational structures, roles
```

## Understanding the Component Architecture

OFBiz applications are built using a component-based architecture located in the following directories:

### Framework Components (`framework/`)
Core infrastructure components providing foundational services:
- **entity**: Entity engine and data model definitions
- **service**: Service engine and business logic framework
- **webapp**: Web application framework and common UI components
- **security**: Authentication and authorization services

### Application Components (`applications/`)
Business domain-specific components:
- **accounting**: Financial management functionality
- **party**: Customer/supplier management
- **product**: Product catalog and inventory
- **order**: Order management and fulfillment
- **manufacturing**: Production planning and execution

### Specialized Components (`specialpurpose/`)
Extended functionality and integrations:
- **ecommerce**: Web store implementation
- **pos**: Point of sale application
- **projectmgr**: Project management tools

## Configuration and Customization

### Database Configuration

OFBiz uses the Entity Engine for database abstraction. Default configuration uses embedded Derby, but production deployments typically use PostgreSQL or MySQL:

```xml
<!-- framework/entity/config/entityengine.xml -->
<datasource name="localpostgres"
    helper-class="org.apache.ofbiz.entity.datasource.GenericHelperDAO"
    schema-name="public"
    field-type-name="postgres"
    check-on-start="true"
    add-missing-on-start="true"
    use-pk-constraint-names="false">
    <read-data reader-name="tenant"/>
    <read-data reader-name="seed"/>
    <read-data reader-name="seed-initial"/>
    <read-data reader-name="demo"/>
    <read-data reader-name="ext"/>
    <inline-jdbc
        jdbc-driver="org.postgresql.Driver"
        jdbc-uri="jdbc:postgresql://127.0.0.1:5432/ofbiz"
        jdbc-username="ofbiz"
        jdbc-password="ofbiz"
        isolation-level="ReadCommitted"
        pool-minsize="2"
        pool-maxsize="250"/>
</datasource>
```

### Service Configuration

Business logic is implemented through the Service Engine. Services are defined in XML and implemented in Java, Groovy, or other supported languages:

```xml
<!-- Example service definition -->
<service name="createCustomer" engine="java"
    location="org.apache.ofbiz.party.party.PartyServices"
    invoke="createPerson" auth="false">
    <description>Create a Customer</description>
    <attribute name="firstName" type="String" mode="IN" optional="false"/>
    <attribute name="lastName" type="String" mode="IN" optional="false"/>
    <attribute name="partyId" type="String" mode="OUT" optional="false"/>
</service>
```

## Development Workflow

### Hot Deployment

OFBiz supports hot deployment for rapid development cycles:

```bash
# Reload specific component
./gradlew "ofbiz --load-component=accounting"

# Reload data for specific component
./gradlew "ofbiz --load-data file=applications/accounting/data/AccountingTypeData.xml"
```

### Testing Your Application

Run automated tests to verify functionality:

```bash
# Run all tests
./gradlew test

# Run tests for specific component
./gradlew test -Dtest.component=accounting

# Run integration tests
./gradlew testIntegration
```

## Troubleshooting Common Issues

### Port Conflicts
If port 8080 is already in use, modify the configuration in `framework/catalina/ofbiz-component.xml`:

```xml
<property name="port" value="8080"/>
<property name="ssl-port" value="8443"/>
```

### Memory Issues
Increase JVM heap size for large datasets:

```bash
export JAVA_OPTS="-Xms1024M -Xmx4096M -XX:MaxPermSize=512M"
./gradlew ofbiz
```

### Database Connection Issues
Verify database connectivity and ensure proper JDBC drivers are available in the classpath. Check logs in `runtime/logs/ofbiz.log` for detailed error information.

This foundation provides the essential knowledge needed to successfully run and begin developing with your first OFBiz application, leveraging its powerful component-based architecture and comprehensive business functionality.

## Repository Context

- **Repository**: [https://github.com/apache/ofbiz-framework](https://github.com/apache/ofbiz-framework)
- **Description**: No description available
- **Business Domain**: Software Development
- **Architecture Pattern**: Library/Utility

## Technology Stack

---

*Generated by ADocS (Automated Documentation Structure) on 2025-09-05 23:48:30*

*For the most up-to-date information, visit the [original repository](https://github.com/apache/ofbiz-framework)*
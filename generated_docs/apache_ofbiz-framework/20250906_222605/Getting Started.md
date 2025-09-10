# Getting Started

## Prerequisites

Before getting started with Apache OFBiz, ensure your development environment meets the following requirements:

### System Requirements
- **Java Development Kit (JDK)**: Version 8 or higher (OpenJDK recommended)
- **Memory**: Minimum 2GB RAM, 4GB+ recommended for development
- **Disk Space**: At least 2GB free space for the framework and data
- **Operating System**: Linux, macOS, or Windows with proper shell support

### Required Tools
- **Git**: For cloning the repository and version control
- **Apache Ant**: Build automation tool (included in the framework)
- **Database**: H2 (embedded, default), PostgreSQL, MySQL, or other supported RDBMS

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/apache/ofbiz-framework.git
cd ofbiz-framework
```

### 2. Initial Build and Data Loading

OFBiz uses Gradle as its primary build system. The framework includes wrapper scripts that automatically download and configure the appropriate Gradle version:

```bash
# On Linux/macOS
./gradlew cleanAll loadDefault

# On Windows
gradlew.bat cleanAll loadDefault
```

This command performs several critical operations:
- **cleanAll**: Removes any existing build artifacts and temporary files
- **loadDefault**: Loads the default dataset including demo data, seed data, and essential configuration

The initial build process typically takes 10-15 minutes and includes:
- Compiling all Java source code across 50+ components
- Processing Freemarker templates and screen definitions
- Loading entity definitions into the database schema
- Initializing the embedded H2 database with sample data

### 3. Starting the Framework

Launch OFBiz using the Gradle wrapper:

```bash
./gradlew ofbiz
```

The startup sequence initializes several key subsystems:
- **Entity Engine**: Database abstraction layer with connection pooling
- **Service Engine**: Asynchronous and synchronous service execution framework  
- **Web Framework**: Multi-tenant web application container
- **Workflow Engine**: Business process automation system
- **Security Framework**: Authentication, authorization, and data protection

Monitor the console output for the startup completion message:
```
[main] INFO org.apache.ofbiz.base.start.Start - Started OFBiz in XX seconds
```

### 4. Accessing the Applications

Once started, OFBiz serves multiple web applications on different ports:

| Application | URL | Default Credentials |
|-------------|-----|-------------------|
| eCommerce | https://localhost:8443/ecommerce | N/A (public) |
| Accounting | https://localhost:8443/accounting | admin/ofbiz |
| Manufacturing | https://localhost:8443/manufacturing | admin/ofbiz |
| Human Resources | https://localhost:8443/humanres | admin/ofbiz |
| Web Tools | https://localhost:8443/webtools | admin/ofbiz |

## Architecture Overview

### Component-Based Structure

OFBiz follows a modular component architecture where each business domain is encapsulated in self-contained components:

```
framework/
├── base/           # Core utilities and configuration
├── entity/         # Entity Engine (ORM layer)
├── service/        # Service Engine and definitions
├── security/       # Authentication and authorization
├── webapp/         # Web framework and common web resources
└── widget/         # Screen, form, and menu widget system

applications/
├── accounting/     # Financial management
├── manufacturing/  # MRP and production planning
├── order/          # Order management
├── party/          # Customer/vendor/employee management
└── product/        # Catalog and inventory management
```

### Key Configuration Files

Understanding these configuration files is essential for customization:

#### framework/base/config/ofbiz-containers.xml
Defines the runtime containers that provide core services:
```xml
<container name="entity-container" 
           class="org.apache.ofbiz.entity.container.EntityContainer">
    <property name="delegator-name" value="default"/>
    <property name="entity-group-name" value="org.apache.ofbiz"/>
</container>
```

#### framework/webapp/config/url.properties
Controls URL generation and routing:
```properties
port.https.enabled=Y
port.https=8443
force.https.host=localhost
```

### Entity Engine Configuration

The Entity Engine provides database abstraction through XML entity definitions. Example entity definition:

```xml
<entity entity-name="Product" package-name="org.apache.ofbiz.product.product">
    <field name="productId" type="id-ne"/>
    <field name="productTypeId" type="id"/>
    <field name="productName" type="name"/>
    <field name="description" type="very-long"/>
    <prim-key field="productId"/>
    <relation type="one" fk-name="PROD_PRTP" rel-entity-name="ProductType">
        <key-map field-name="productTypeId"/>
    </relation>
</entity>
```

## Development Workflow

### Hot Deployment

OFBiz supports hot deployment for rapid development cycles:

```bash
# Reload specific component without restart
./gradlew "ofbiz --load-component=applications/product"

# Reload data for specific component
./gradlew "ofbiz --load-data file=applications/product/data/ProductTypeData.xml"
```

### Custom Component Creation

Create new components using the built-in plugin system:

```bash
./gradlew createComponent -PcomponentName=mycomponent -PcomponentResourceName=MyComponent
```

This generates a complete component structure with:
- Entity definitions and database scripts
- Service definitions and implementations  
- Screen definitions and controller mappings
- Build configuration and dependency management

### Testing Framework Integration

OFBiz includes comprehensive testing support:

```bash
# Run all tests
./gradlew test

# Run tests for specific component
./gradlew :applications:product:test

# Run integration tests with database
./gradlew testIntegration
```

## Common Configuration Tasks

### Database Configuration

Modify `framework/entity/config/entityengine.xml` to configure external databases:

```xml
<datasource name="localpostgres"
            helper-class="org.apache.ofbiz.entity.datasource.GenericHelperDAO"
            schema-name="public"
            field-type-name="postgres"
            check-on-start="true"
            add-missing-on-start="true"
            use-pk-constraint-names="false">
    <read-data reader-name="tenant"/>
    <read-data reader-name="seed"/>
    <read-data reader-name="demo"/>
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

### Security Configuration

Configure HTTPS certificates and security policies in `framework/security/config/security.properties`:

```properties
security.login.password.encrypt=true
security.login.password.encrypt.hash.type=SHA
login.secret.key=change-this-key-in-production
```

This comprehensive setup provides a solid foundation for developing enterprise applications using the Apache OFBiz framework's robust architecture and extensive business application suite.

## Subsections

- [Prerequisites and Requirements](./Prerequisites and Requirements.md)
- [Installation and Setup](./Installation and Setup.md)
- [Configuration Guide](./Configuration Guide.md)
- [Running OFBiz Applications](./Running OFBiz Applications.md)

## Repository Context

- **Repository**: [https://github.com/apache/ofbiz-framework](https://github.com/apache/ofbiz-framework)
- **Description**: No description available
- **Business Domain**: Software Development
- **Architecture Pattern**: Library/Utility

## Technology Stack

## Related Documentation

This section is part of a comprehensive documentation structure. Related sections include:

- **Prerequisites and Requirements**: Detailed coverage of prerequisites and requirements
- **Installation and Setup**: Detailed coverage of installation and setup
- **Configuration Guide**: Detailed coverage of configuration guide
- **Running OFBiz Applications**: Detailed coverage of running ofbiz applications

---

*Generated by ADocS (Automated Documentation Structure) on 2025-09-06 22:43:02*

*For the most up-to-date information, visit the [original repository](https://github.com/apache/ofbiz-framework)*
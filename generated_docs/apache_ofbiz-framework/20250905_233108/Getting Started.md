# Getting Started

## Prerequisites

Before setting up Apache OFBiz, ensure your development environment meets the following requirements:

### System Requirements
- **Java Development Kit (JDK)**: Version 8 or higher (OpenJDK or Oracle JDK)
- **Memory**: Minimum 4GB RAM (8GB+ recommended for development)
- **Disk Space**: At least 2GB free space for the framework and data
- **Operating System**: Linux, macOS, or Windows with proper shell support

### Required Tools
- **Git**: For cloning the repository and version control
- **Apache Ant**: Build automation tool (included in the framework)
- **Database**: PostgreSQL, MySQL, or Derby (Derby is included for quick start)

## Quick Installation

### 1. Clone the Repository

```bash
git clone https://github.com/apache/ofbiz-framework.git
cd ofbiz-framework
```

### 2. Initial Setup and Build

OFBiz uses Gradle as its primary build system. The framework includes a Gradle wrapper, so you don't need to install Gradle separately:

```bash
# On Linux/macOS
./gradlew cleanAll loadDefault

# On Windows
gradlew.bat cleanAll loadDefault
```

This command performs several critical operations:
- **cleanAll**: Removes any existing build artifacts and database data
- **loadDefault**: Loads the default dataset including demo data, seed data, and essential configuration

### 3. Start the Framework

```bash
# Start OFBiz
./gradlew ofbiz

# Alternative: Start with specific run-time arguments
./gradlew "ofbiz --start"
```

The framework will start multiple services:
- **Web Server**: Typically runs on port 8443 (HTTPS) and 8080 (HTTP)
- **Service Engine**: Handles business logic and service orchestration
- **Entity Engine**: Manages database operations and ORM functionality
- **Widget Framework**: Renders UI components and forms

## Architecture Overview

### Multi-Tier Architecture
OFBiz implements a sophisticated multi-tier architecture:

```
┌─────────────────┐
│   Presentation  │ ← Screens, Forms, Menus (Widget Framework)
├─────────────────┤
│    Business     │ ← Services, Events, Business Logic
├─────────────────┤
│   Integration   │ ← Service Engine, Message Processing
├─────────────────┤
│      Data       │ ← Entity Engine, Database Abstraction
└─────────────────┘
```

### Core Framework Components

#### Entity Engine
The Entity Engine provides database abstraction and ORM capabilities:

```xml
<!-- Example entity definition in entitymodel.xml -->
<entity entity-name="Product" package-name="org.apache.ofbiz.product.product">
    <field name="productId" type="id-ne"/>
    <field name="productTypeId" type="id"/>
    <field name="productName" type="name"/>
    <field name="description" type="very-long"/>
    <prim-key field="productId"/>
</entity>
```

#### Service Engine
Services encapsulate business logic and can be invoked synchronously or asynchronously:

```xml
<!-- Service definition in services.xml -->
<service name="createProduct" engine="entity-auto" invoke="create" auth="true">
    <description>Create a Product</description>
    <auto-attributes include="pk" mode="INOUT" optional="false"/>
    <auto-attributes include="nonpk" mode="IN" optional="true"/>
</service>
```

## Development Environment Setup

### IDE Configuration

#### IntelliJ IDEA Setup
1. Import the project as a Gradle project
2. Configure JDK in Project Structure settings
3. Enable annotation processing for the framework's code generation

#### Eclipse Setup
```bash
# Generate Eclipse project files
./gradlew eclipse
```

### Hot Deployment Configuration

OFBiz supports hot deployment for rapid development. Configure your component in the `component-load.xml`:

```xml
<component-loader xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="http://ofbiz.apache.org/dtds/component-loader.xsd">
    <load-component component-location="framework"/>
    <load-component component-location="applications"/>
    <load-component component-location="specialpurpose"/>
    <!-- Your custom components -->
    <load-component component-location="hot-deploy/your-component"/>
</component-loader>
```

## Database Configuration

### Default Derby Setup
OFBiz ships with Apache Derby for immediate development:

```properties
# framework/entity/config/entityengine.xml
<datasource name="localderby"
    helper-class="org.apache.ofbiz.entity.datasource.GenericHelperDAO"
    schema-name="OFBIZ"
    field-type-name="derby"
    check-on-start="true"
    add-missing-on-start="true"
    use-pk-constraint-names="false">
    <read-data reader-name="seed"/>
    <read-data reader-name="demo"/>
</datasource>
```

### PostgreSQL Configuration
For production environments, configure PostgreSQL:

```xml
<datasource name="localpostgres"
    helper-class="org.apache.ofbiz.entity.datasource.GenericHelperDAO"
    field-type-name="postgres"
    check-on-start="true"
    add-missing-on-start="true">
    <read-data reader-name="seed"/>
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

## First Steps After Installation

### 1. Access the Applications
- **eCommerce Store**: https://localhost:8443/ecommerce
- **Backend Applications**: https://localhost:8443/webtools
- **Accounting**: https://localhost:8443/accounting
- **Manufacturing**: https://localhost:8443/manufacturing

### 2. Default Login Credentials
- **Username**: admin
- **Password**: ofbiz

### 3. Explore the Framework Structure
```
ofbiz-framework/
├── framework/          # Core framework components
│   ├── entity/        # Entity Engine
│   ├── service/       # Service Engine  
│   ├── webapp/        # Web framework
│   └── widget/        # UI Widget framework
├── applications/      # Business applications
│   ├── accounting/    # Financial management
│   ├── party/         # Party management
│   └── product/       # Product catalog
├── specialpurpose/    # Specialized modules
└── hot-deploy/        # Custom development area
```

### 4. Create Your First Component
```bash
# Generate a new component structure
./gradlew createComponent -PcomponentName=mycomponent -PcomponentResourceName=MyComponent -PwebappName=mycomponent -PbasePermission=MYCOMPONENT
```

This creates a complete component structure with entity definitions, services, web applications, and security configurations, following OFBiz architectural patterns and best practices.

## Subsections

- [Prerequisites and System Requirements](./Prerequisites and System Requirements.md)
- [Installation and Setup](./Installation and Setup.md)
- [Configuration Guide](./Configuration Guide.md)
- [Running Your First Application](./Running Your First Application.md)

## Repository Context

- **Repository**: [https://github.com/apache/ofbiz-framework](https://github.com/apache/ofbiz-framework)
- **Description**: No description available
- **Business Domain**: Software Development
- **Architecture Pattern**: Library/Utility

## Technology Stack

## Related Documentation

This section is part of a comprehensive documentation structure. Related sections include:

- **Prerequisites and System Requirements**: Detailed coverage of prerequisites and system requirements
- **Installation and Setup**: Detailed coverage of installation and setup
- **Configuration Guide**: Detailed coverage of configuration guide
- **Running Your First Application**: Detailed coverage of running your first application

---

*Generated by ADocS (Automated Documentation Structure) on 2025-09-05 23:45:36*

*For the most up-to-date information, visit the [original repository](https://github.com/apache/ofbiz-framework)*